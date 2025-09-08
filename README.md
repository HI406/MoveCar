# 一键挪车 · Docker 版

## 快速开始

```bash
# 1) 解压后进入目录
docker compose up -d --build

# 2) 打开
# 前端页面: http://<你的服务器IP>/
# 403页面:  http://<你的服务器IP>/403
# 后台管理: http://<你的服务器IP>/admin
```

> 端口：对外 80（容器内 8000）

### 配置 WeComChan

消息提醒当前仅支持[WeComChan](https://github.com/easychen/wecomchan "点击跳转") 渠道，请自行搭建，具体教程请参照WeComChan官方文档。
在本程序启动前，按需设置环境变量（也可以直接在 docker-compose.yml 中修改）：

- `WECOMCHAN_BASE_URL` 例如：`http://10.1.5.186:7032/wecomchan`
- `WECOMCHAN_SENDKEY`   例如：`yoursendkey`
- `WECOMCHAN_MSG_TYPE`  默认为 `text`

### 编辑配置

- 配置文件：`config.yml`（容器启动时读取；直接修改本文件并 `docker compose restart` 即生效）
- 后台管理保存配置后也会写回 `config.yml`
- 本地背景图放在 `static/backImg/` 目录，前端背景文件名形如 `front.png|jpg|webp|gif`，403 页面背景文件名形如 `403.jpg|png|webp|gif`。本地图优先于 URL。

### 启用时间段逻辑

- `enable_windows` 为每日时间段列表（支持跨日，如 `22:00-06:00`）。
- 非启用时间访问 `/` 会展示 403 提示页（仅提示文字，不显示车牌与按钮）。
- 一行一个时段，例如
```
08:00-12:00
14:00-22:00
```

### 车牌样式

- 自动判断新能源车牌：
  - 规则：以 `D/F` 结尾的常见新能源格式优先；或长度为 8 且以 `D/F` 结尾的简化判断。
  - 新能源牌渲染为渐变绿，普通燃油车为蓝牌。

### 文案格式

- 支持 **加粗** 与 *斜体* 两种 Markdown 语法（受限版），可设置文字对齐与字号。


### 设计规范

- 遵循简洁、层次清晰、留白充分的移动端设计；按钮采用圆角、柔和阴影与清新色彩；背景图按设定模式自适应铺满。
- 挪车二维码可以自己将前端地址```http://<你的服务器IP>/```通过 [草料二维码](https://cli.im/url "点击跳转") 生成，如果想自己设计也无需专业设计软件，打开**PPT**做一个就行，参加```imgs```文件夹中的PPT模板```停车码.pptx```。
 <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/qrcode-templates-1.jpg" width = "40%" height = "40%" alt="挪车码模板" align=center /> &emsp;   <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/qrcode-templates-2.jpg" width = "40%" height = "40%" alt="挪车码模板" align=center />

- **实体挪车码**可以上万能的某宝搜索```亚克力磁吸标签展示牌```，各种尺寸大小都有，根据需要购买即可，然后在PPT制作对应大小的挪车码打印出来，裁剪好后即可使用。

 <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/tb.jpg" width = "60%" height = "60%" alt="点击去购买" align=center />

### 必要说明

- 别人第一次扫码时不会出现打电话按钮，只会向车主微信发送挪车消息提醒，点击了一次挪车按钮后，才会出现打电话按钮。
- 本项目不提供第三方隐私号码转接服务，点击打电话给车主按钮后会跳转到拨号页面，此时播出的号码为后台设置的车主号码。
- 本项目的是避免直接放置车主电话号码到车上被人抄牌，也方便了他人通知车主时还要手输11位电话号码。毕竟车子挡住人家已经造成不便了，就不要再给别人带来更多不便。
- 本项目支持完全自主本地部署，对于车主和挪车提醒人都不收集任何个人隐私信息。

---
### 页面截图

后台管理界面截图：

 <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/admin.png" width = "75%" height = "75%" alt="前端挪车页面1" align=center />

---
前端挪车页面截图：

 <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/front-1.png" width = "40%" height = "40%" alt="前端挪车页面1" align=center />&emsp;  <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/front-2.png" width = "40%" height = "40%" alt="前端挪车页面2" align=center />

---
点击**叫车主挪车**按钮后，弹出提示框，同时微信收到挪车消息提醒：

 <img src="https://raw.githubusercontent.com/HI406/MoveCar/refs/heads/main/imgs/front-3.png" width = "40%" height = "40%" alt="前端挪车页面3" align=center />
