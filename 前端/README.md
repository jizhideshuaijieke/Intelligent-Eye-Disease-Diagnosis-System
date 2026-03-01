# 前端说明

## 运行方式（浏览器模式）

```powershell
npm install
npm run mock
npm run serve
```

访问地址：`http://127.0.0.1:7000`

## 脚本说明

1. `npm run serve`：启动 Vue 开发服务器（7000）
2. `npm run mock`：启动 Mock API 服务（8800）
3. `npm run build`：打包生产构建
4. `npm run lint`：代码检查

## 环境变量

可参考 `.env.example` 或新增 `.env.local`：

1. `VUE_APP_REAL_API`
2. `VUE_APP_MOCK_API`
3. `VUE_APP_API_HEALTH_PATH`

## 说明

项目统一使用浏览器端演示与部署。
