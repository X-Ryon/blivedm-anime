# Bilidmj Anime (Bilibili 直播弹幕姬(互动版))

这是一个基于 blivedm 的支持动画播放的 Bilibili 直播弹幕姬客户端。

## 📁 项目结构

当前项目主要包含后端服务，前端部分正在规划中。

- **backend/**: 核心逻辑、API 服务及弹幕监听模块。
- **Frontend/**: 暂未开发 (计划采用 **React + Vite** 构建)。

## 🛠️ 技术栈

### 后端 (Backend)
- **Language**: Python
- **Framework**: FastAPI (配合 Uvicorn)
- **Core Library**: [blivedm](https://github.com/xfgryujk/blivedm) (Bilibili 直播协议客户端)
- **Database**: SQLite (暂定)

### 前端 (Frontend - Coming Soon)
- **Framework**: React
- **Build Tool**: Vite
- **UI Component**: Ant Design (预计)

## 🚀 快速开始 (后端)

### 1. 环境准备
确保已安装 Python 3.10+。

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 运行服务
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## 📝 开发计划

- [x] 后端基础架构搭建
- [x] 弹幕监听核心功能
- [ ] 完善 RESTful API
- [ ] **前端开发**: 初始化 React + Vite 项目
- [ ] 前后端联调

