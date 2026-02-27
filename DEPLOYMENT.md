# 可移植配置与部署指南

## 1. 环境要求

1. Node.js 18+
2. Python 3.10（推荐）
3. MySQL 8+（全链路模式需要）
4. Redis 6+（全链路模式需要）
5. 可选：NVIDIA GPU + CUDA（模型推理更快）

## 2. 拉取后首次准备

```powershell
cd 代码
```

### 前端

```powershell
cd 前端
npm install
Copy-Item .env.example .env.local
```

### 后端

```powershell
cd ..\后端
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 模型服务

```powershell
cd ..\模型
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## 3. 配置文件说明

### 前端 `前端/.env.local`

1. `VUE_APP_REAL_API`：真实后端地址（默认 `http://127.0.0.1:8800`）
2. `VUE_APP_MOCK_API`：Mock 地址（默认 `http://127.0.0.1:8800`）
3. `VUE_APP_API_HEALTH_PATH`：后端健康检查路径（默认 `/getPatientsNum`）

### 后端 `后端/.env`

1. MySQL：`MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DB`
2. Redis：`REDIS_HOST`、`REDIS_PORT`、`REDIS_DB`
3. 模型服务：`AI_MODEL_URL`（默认 `http://127.0.0.1:5000`）
4. AI 问答：`AI_CHAT_API_KEY`（不配置则 `/aiQuestion`、`/aiSuggestion` 无法调用外部模型）
5. 邮件：`MAIL_USER`、`MAIL_PASSWORD`
6. 鉴权：`JWT_SECRET_KEY`（上线请务必更换）

### 模型 `模型/.env`

1. `MODEL_HOST`、`MODEL_PORT`
2. `MODEL_DIR` 或者单独设置四个权重路径：
   `MAIN_MODEL_PATH`、`SUB_MODEL_PATH`、`VESSEL_MODEL_PATH`、`OCT_MODEL_PATH`

## 4. 启动方式

## A. 面试演示模式

```powershell
# 终端1：模型
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

## B. 全链路模式

```powershell
# 终端1：模型
cd 模型
python app.py

# 终端2：后端
cd 后端
python main.py

# 终端3：前端
cd 前端
npm run serve
```

## 5. 验证接口是否通

### 模型健康检查

```powershell
Invoke-WebRequest http://127.0.0.1:5000/api/fundus_analysi
```

### Mock 服务检查

```powershell
Invoke-WebRequest http://127.0.0.1:8800/getPatientsNum
```

## 6. 常见问题

1. `ModuleNotFoundError: No module named 'PIL'`
   - 解决：在模型环境安装 `Pillow`，或直接 `pip install -r 模型/requirements.txt`
2. 8800 端口冲突
   - Mock 和 FastAPI 都默认用 8800，只能同时开一个
3. 没有分割图/OCT 分层图
   - 先确认模型服务启动成功，再确认 `mock-server` 日志里 `Model bridge target` 指向 `http://127.0.0.1:5000`
4. GitHub 推送失败（大文件）
   - `*.pth` 超过 100MB，默认不入库；需要时用 Git LFS
