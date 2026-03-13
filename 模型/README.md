# 模型服务说明

## 概述

该目录提供项目使用的图像推理服务，基于 Flask + PyTorch 实现眼底图像分析和 OCT 分层，并向业务后端暴露 HTTP 接口。

## 启动

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

默认端口：`5000`

## 接口

- `GET /api/fundus_analysi`：服务探活接口
- `POST /api/fundus_analysis`：眼底图像分析，返回增强图、血管分割图和分类概率
- `POST /api/oct_segmentation`：OCT 分层，返回分层结果图

## 权重文件

模型权重默认不纳入 Git。请根据 [model_param/README.md](./model_param/README.md) 将所需的 `*.pth` 文件放入 `model_param` 目录。

## 说明

- 业务后端通过 `AI_MODEL_URL` 调用该服务
- 如果模型服务未启动，图像分析链路无法正常工作
