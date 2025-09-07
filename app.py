import os
import re
import io
import shutil
import datetime
from typing import List, Optional

import yaml
import requests
from fastapi import FastAPI, Request, UploadFile, Form, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

CONFIG_PATH = os.path.abspath("config.yml")
STATIC_DIR = os.path.abspath("static")
BACKIMG_DIR = os.path.join(STATIC_DIR, "backImg")
os.makedirs(BACKIMG_DIR, exist_ok=True)

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

def within_enable_window(enable_windows: List[str], now: Optional[datetime.datetime] = None) -> bool:
    now = now or datetime.datetime.now()
    t = now.time()
    for win in enable_windows or []:
        try:
            start, end = win.split("-")
            hs, ms = map(int, start.split(":"))
            he, me = map(int, end.split(":"))
            start_t = datetime.time(hs, ms)
            end_t = datetime.time(he, me)
            if start_t <= end_t:
                if start_t <= t <= end_t:
                    return True
            else:
                # 跨日
                if t >= start_t or t <= end_t:
                    return True
        except Exception:
            continue
    return False

PROVINCES = "京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵青藏川宁琼港澳使领学警"
NEW_ENERGY_PATTERN = re.compile(rf"^[{PROVINCES}][A-Z][A-HJ-NP-Z0-9]{{4}}[DF]$", re.I)

NEW_ENERGY_PREFIX = set("DABCE")  # 纯电
NEW_ENERGY_SUFFIX = set("FGHJK")  # 插电混动/燃料电池

def is_new_energy(plate: str) -> bool:
    """
    判断是否为新能源车牌。
    支持格式：
    - 桂A·D12345（首位字母新能源标识）
    - 粤B·12345F（末位字母新能源标识）
    """
    raw = plate.replace("·","").replace(" ","").upper()
    if len(raw) < 6:
        return False

    # 序号部分：去掉省(1) + 城市(1) = 前两位
    seq = raw[2:]
    if not seq:
        return False

    # 首位字母表示新能源
    if seq[0] in NEW_ENERGY_PREFIX or seq[0] in NEW_ENERGY_SUFFIX:
        return True
    # 末位字母表示新能源
    if seq[-1] in NEW_ENERGY_PREFIX or seq[-1] in NEW_ENERGY_SUFFIX:
        return True

    return False


def format_plate(plate: str) -> str:
    # 保持 "桂A·12345" 这种视觉格式，如果没有 · 则自动加入
    raw = plate.replace(" ","")
    if "·" in raw:
        return raw
    if len(raw) >= 3:
        return raw[:2] + "·" + raw[2:]
    return raw

app = FastAPI(title="一键挪车")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def front(request: Request):
    cfg = load_config()
    enabled = within_enable_window(cfg.get("enable_windows", []))
    if not enabled:
        return templates.TemplateResponse("403.html", {
            "request": request,
            "cfg": cfg,
            "page": cfg.get("page403", {}),
            "front_mode": False
        })
    plate = cfg.get("plate", "")
    plate_fmt = format_plate(plate)
    # 分割省份、城市、号码
    province, city, number = "", "", ""
    if "·" in plate_fmt:
        parts = plate_fmt.split("·")
        if len(parts) == 2:
            province = parts[0][0] if len(parts[0])>0 else ""
            city = parts[0][1] if len(parts[0])>1 else ""
            number = parts[1]
    else:
        if len(plate_fmt) >= 2:
            province = plate_fmt[0]
            city = plate_fmt[1]
            number = plate_fmt[2:]
        else:
            province = plate_fmt
    return templates.TemplateResponse("front.html", {
        "request": request,
        "cfg": cfg,
        "province": province,
        "city": city,
        "number": number,
        "is_new_energy": is_new_energy(plate_fmt),
    })


@app.get("/403", response_class=HTMLResponse)
async def page403(request: Request):
    cfg = load_config()
    return templates.TemplateResponse("403.html", {
        "request": request,
        "cfg": cfg,
        "page": cfg.get("page403", {}),
        "front_mode": False
    })

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    cfg = load_config()
    return templates.TemplateResponse("admin.html", {"request": request, "cfg": cfg})

@app.post("/admin/save")
async def admin_save(
    request: Request,
    plate: str = Form(...),
    owner_phone: str = Form(...),
    enable_windows: str = Form(""),
    front_text: str = Form(""),
    front_align: str = Form("center"),
    front_font_size: int = Form(20),
    front_bg_mode: str = Form("auto"),
    front_bg_url: str = Form(""),
    page403_text: str = Form(""),
    page403_align: str = Form("center"),
    page403_font_size: int = Form(20),
    page403_bg_mode: str = Form("auto"),
    page403_bg_url: str = Form(""),
    label_notify: str = Form("叫车主挪车"),
    label_call: str = Form("打电话给车主"),
    notify_dialog: str = Form("抱歉临时停车给您带来不便，车主已收到您的挪车提醒，正在火速赶来中，请您耐心等待。"),
):
    cfg = load_config()
    cfg["plate"] = plate.strip()
    cfg["owner_phone"] = re.sub(r"\D", "", owner_phone)

    wins = [w.strip() for w in (enable_windows or "").splitlines() if w.strip()]
    cfg["enable_windows"] = wins

    cfg.setdefault("front", {})
    cfg["front"]["text"] = front_text
    cfg["front"]["align"] = front_align
    cfg["front"]["font_size"] = int(front_font_size)
    cfg["front"]["bg_mode"] = front_bg_mode
    cfg["front"]["bg_url"] = front_bg_url.strip()

    cfg.setdefault("page403", {})
    cfg["page403"]["text"] = page403_text
    cfg["page403"]["align"] = page403_align
    cfg["page403"]["font_size"] = int(page403_font_size)
    cfg["page403"]["bg_mode"] = page403_bg_mode
    cfg["page403"]["bg_url"] = page403_bg_url.strip()

    cfg.setdefault("labels", {})
    cfg["labels"]["notify"] = label_notify
    cfg["labels"]["call"] = label_call

    cfg["notify_dialog"] = notify_dialog

    save_config(cfg)
    return RedirectResponse(url="/admin", status_code=303)

def _save_uploaded(file: UploadFile, target_stem: str) -> str:
    # 保存到 static/backImg/{target_stem}.{ext}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".png",".jpg",".jpeg",".webp",".gif"]:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    target = os.path.join(BACKIMG_DIR, f"{target_stem}{ext}")
    # 删除同名（不同后缀）旧文件，保持唯一
    for f in os.listdir(BACKIMG_DIR):
        if f.startswith(target_stem + "."):
            os.remove(os.path.join(BACKIMG_DIR, f))
    with open(target, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return "/static/backImg/" + os.path.basename(target)

@app.post("/admin/upload/front")
async def upload_front(img: UploadFile = File(...)):
    url = _save_uploaded(img, "front")
    return JSONResponse({"ok": True, "url": url})

@app.post("/admin/upload/403")
async def upload_403(img: UploadFile = File(...)):
    url = _save_uploaded(img, "403")
    return JSONResponse({"ok": True, "url": url})

@app.post("/api/notify")
async def api_notify():
    cfg = load_config()
    plate = format_plate(cfg.get("plate", ""))
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"您的车辆 {plate} 在 {now_str} 收到挪车请求，请及时去挪车。"

    base = os.getenv("WECOMCHAN_BASE_URL", "").rstrip("/")
    sendkey = os.getenv("WECOMCHAN_SENDKEY", "")
    msg_type = os.getenv("WECOMCHAN_MSG_TYPE", "text")
    if not base or not sendkey:
        return JSONResponse({"ok": False, "error": "未配置WECOMCHAN_BASE_URL或WECOMCHAN_SENDKEY"}, status_code=500)

    try:
        # 兼容 GET 方式：/wecomchan?sendkey=xxx&msg=...&msg_type=text
        params = {"sendkey": sendkey, "msg": msg, "msg_type": msg_type}
        r = requests.get(base, params=params, timeout=10)
        r.raise_for_status()
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/config")
async def api_config():
    cfg = load_config()
    return JSONResponse(cfg)
