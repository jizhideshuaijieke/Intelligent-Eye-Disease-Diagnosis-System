# 智慧眼疾诊断系统

一个前后端分离的眼科辅助诊断项目，包含：

1. 前端：Vue2 + ElementUI + ECharts + Electron
2. 后端：FastAPI + MySQL + Redis
3. 模型服务：Flask + PyTorch（眼底分类/血管分割 + OCT 分层）

## 目录结构

```text
代码/
├─ 前端/
├─ 后端/
├─ 模型/
└─ 测试案例/
```

## 服务端口与通信关系

1. 前端开发服务：`http://127.0.0.1:7000`
2. Mock/桥接服务（前端内置）：`http://127.0.0.1:8800`
3. 后端 FastAPI：`http://127.0.0.1:8800`（和 Mock 二选一）
4. 模型 Flask：`http://127.0.0.1:5000`

通信链路：

1. 演示模式：`前端 -> mock-server(8800)`，并可选桥接到模型 `5000`
2. 全链路模式：`前端 -> FastAPI(8800) -> 模型(5000)`

## 快速演示

只启动前端 + mock-server：

```powershell
# 终端1：模型服务
cd 模型
python app.py

# 终端2：Mock桥接
cd 前端
node mock-server.js

# 终端3：前端
cd 前端
npm run serve
```

访问：`http://127.0.0.1:7000`

## 全链路启动（含后端数据库）

详细步骤见 [DEPLOYMENT.md](./DEPLOYMENT.md)。

模型权重放置说明见 [模型/model_param/README.md](./模型/model_param/README.md)。
