# 前端说明

## 概述

该目录是项目的 Web 前端，基于 Vue 2、Vue Router、Element UI、Axios 和 ECharts 实现图像上传、分析展示、病例管理、统计可视化与医生信息维护。

## 启动

```powershell
Copy-Item .env.example .env.local
npm install
npm run serve
```

默认访问地址：`http://127.0.0.1:7000`

## 后端配置

前端当前只连接真实 Python 后端，请在 `.env.local` 中配置业务后端地址：

```env
VUE_APP_API_BASE=http://127.0.0.1:8800
```

如果后端需要调用模型服务，请同时确保 `后端/.env` 中的 `AI_MODEL_URL` 指向可用的 Flask 模型服务。

## 常用脚本

- `npm run serve`：启动开发服务器
- `npm run build`：构建生产资源
- `npm run lint`：执行代码检查

## 说明

- 登录、统计、病例保存等功能已经接入真实后端
- 图像分析请求发送到 `/aibo`，由后端再转发给模型服务处理
