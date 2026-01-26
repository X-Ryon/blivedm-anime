# Bilibili Live Monitor Backend

这是一个基于 FastAPI 的 Bilibili 直播间弹幕与礼物监听后端系统。

## 功能特性

- **实时监听**：连接 Bilibili 直播间 WebSocket，实时接收弹幕、礼物、上舰、SC (醒目留言)。
- **数据持久化**：使用 SQLite + SQLAlchemy 自动保存所有接收到的消息。
- **实时推送**：提供 WebSocket 接口，将解析后的数据实时推送给前端客户端。
- **分层架构**：遵循 Model-Schema-CRUD-Service-API 分层设计，结构清晰，易于扩展。

## 技术栈

- **Python 3.9+**
- **FastAPI**: 高性能 Web 框架
- **SQLAlchemy (Async)**: 异步 ORM
- **SQLite (aiosqlite)**: 数据库
- **blivedm**: Bilibili 直播协议库 (GitHub 版)
- **Pydantic**: 数据验证与序列化

## 快速开始

### 1. 环境准备

确保已安装 Python 3.9 或更高版本。

```bash
# 1. 克隆或下载本项目
# 2. 创建虚拟环境 (推荐)
python -m venv venv
# Windows 激活
venv\Scripts\activate
# Linux/Mac 激活
source venv/bin/activate
```

### 2. 安装依赖

使用提供的 `run.bat` 脚本（Windows）或手动安装：

```bash
# Windows 自动安装
run.bat

# 或手动安装
pip install -r requirements.txt
```

### 3. 运行服务

直接运行 `main.py` 即可启动服务（默认端口 8000）：

```bash
python main.py
```

服务启动后，Swagger API 文档地址：http://127.0.0.1:8000/docs

## API 接口使用说明

### 1. 启动监听与实时推送

推荐使用 WebSocket 直接连接，连接建立后服务器会自动开始监听目标直播间。

#### 弹幕流 (含 SC)
- **协议**: WebSocket
- **地址**: `ws://127.0.0.1:8000/api/ws/danmaku/{room_id}`
- **示例**: `ws://127.0.0.1:8000/api/ws/danmaku/605`
- **数据格式**:
  ```json
  {
    "user_name": "用户昵称",
    "level": 10,
    "privilege_name": "舰长",
    "dm_text": "弹幕内容",
    "identity": "普通",
    "price": 0.0
  }
  ```

#### 礼物流 (含上舰)
- **协议**: WebSocket
- **地址**: `ws://127.0.0.1:8000/api/ws/gift/{room_id}`
- **示例**: `ws://127.0.0.1:8000/api/ws/gift/605`
- **数据格式**:
  ```json
  {
    "user_name": "用户昵称",
    "level": 0,
    "privilege_name": "普通",
    "gift_type": "小心心",
    "price": 100.0
  }
  ```

### 2. RESTful 触发接口 (可选)

如果你无法直接发起 WebSocket 连接，可以使用 POST 接口触发后台监听任务（实际数据仍需通过 WebSocket 接收）。

- **启动弹幕监听**: `POST /api/listen/danmaku`
  - Body: `{"room_id": "605"}`
- **启动礼物监听**: `POST /api/listen/gift`
  - Body: `{"room_id": "605"}`

## 数据库

项目默认使用 SQLite 数据库，文件名为 `sql_app.db`，位于项目根目录。
应用启动时会自动检测并创建所需的数据表 (`danmakus`, `gifts`, `super_chats`)。

## 目录结构

```
.
├── app/
│   ├── api/          # 路由与接口定义
│   ├── core/         # 核心配置 (数据库连接)
│   ├── crud/         # 数据库 CRUD 操作
│   ├── models/       # SQLAlchemy 数据模型
│   ├── schemas/      # Pydantic 数据模式
│   └── services/     # 业务逻辑 (B站连接管理)
├── main.py           # 应用入口
├── requirements.txt  # 依赖列表
├── run.bat           # Windows 启动脚本
└── README.md         # 项目文档
```
