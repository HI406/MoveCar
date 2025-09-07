# 一键挪车 · Docker 版

## 快速开始

```bash
# 1) 解压后进入目录
docker compose up -d --build

# 2) 打开
# 前端页面: http://<服务器IP>/
# 403页面:  http://<服务器IP>/403
# 后台管理: http://<服务器IP>/admin
```

> 端口：对外 80（容器内 8000）

### 配置 WeComChan

在启动前，按需设置环境变量（也可以直接在 docker-compose.yml 中修改）：

- `WECOMCHAN_BASE_URL` 例如：`http://10.1.5.186:7032/wecomchan`
- `WECOMCHAN_SENDKEY`   例如：`sendkey1234`
- `WECOMCHAN_MSG_TYPE`  默认为 `text`

### 编辑配置

- 配置文件：`config.yml`（容器启动时读取；直接修改本文件并 `docker compose restart` 即生效）
- 后台管理保存配置后也会写回 `config.yml`
- 本地背景图放在 `static/backImg/` 目录，前端背景文件名形如 `front.png|jpg|webp|gif`，403 页面背景文件名形如 `403.jpg|png|webp|gif`。本地图优先于 URL。

### 启用时间段逻辑

- `enable_windows` 为每日时间段列表（支持跨日，如 `22:00-06:00`）。
- 非启用时间访问 `/` 会展示 403 提示页（仅提示文字，不显示车牌与按钮）。

### 车牌样式

- 自动判断新能源车牌：
  - 规则：以 `D/F` 结尾的常见新能源格式优先；或长度为 8 且以 `D/F` 结尾的简化判断。
  - 新能源牌渲染为渐变绿，普通燃油车为蓝牌。

### 文案格式

- 支持 **加粗** 与 *斜体* 的 Markdown 语法（受限版），可设置文字对齐与字号。

### 设计规范

- 遵循简洁、层次清晰、留白充分的移动端设计；按钮采用圆角、柔和阴影与清新色彩；背景图按设定模式自适应铺满。

