# 模型服务说明（Flask + PyTorch）

## 启动

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

默认端口：`5000`

## 接口

1. `GET /api/fundus_analysi`：健康检查
2. `POST /api/fundus_analysis`：眼底分类 + 血管分割
3. `POST /api/oct_segmentation`：OCT 分层

## 权重文件

权重文件默认不入 Git。请查看 [model_param/README.md](./model_param/README.md)。
