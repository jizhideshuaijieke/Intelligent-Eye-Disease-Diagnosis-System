# 前端说明

## 本地启动

```powershell
npm install
npm run serve
```

默认端口：`7000`

## Mock 桥接

```powershell
node mock-server.js
```

默认端口：`8800`

## 环境变量

复制模板：

```powershell
Copy-Item .env.example .env.local
```

关键变量：

1. `VUE_APP_REAL_API`
2. `VUE_APP_MOCK_API`
3. `VUE_APP_API_HEALTH_PATH`

完整部署流程见仓库根目录 [README.md](../README.md) 与 [DEPLOYMENT.md](../DEPLOYMENT.md)。
