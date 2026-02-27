# 后端说明（FastAPI）

## 启动

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

默认端口：`8800`

## 关键配置

`.env` 中至少需要：

1. `MYSQL_*`
2. `REDIS_*`
3. `AI_MODEL_URL`
4. `JWT_SECRET_KEY`

如果要启用外部 AI 问答，还需配置：

1. `AI_CHAT_API_KEY`
2. `AI_CHAT_HOST`
3. `AI_CHAT_PATH`

完整部署流程见仓库根目录 [README.md](../README.md) 与 [DEPLOYMENT.md](../DEPLOYMENT.md)。
