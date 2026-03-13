# 后端说明

## 概述

该目录是项目当前使用的真实业务后端，基于 FastAPI、SQLAlchemy 和 MySQL 实现账号认证、病例管理、统计分析、邮件发送与模型结果接入。

## 数据库

- 初始化脚本位于 `db/init_schema.sql`
- 启动前请先创建 MySQL 数据库，并执行该脚本
- `Case_history.reportId` 已统一为 `VARCHAR(50)`，用于匹配前端病历号格式和 `patient.reportId` 外键

## 启动

```powershell
Copy-Item .env.example .env
pip install -r requirements.txt
python main.py
```

默认地址：`http://127.0.0.1:8800`

## 环境配置

`.env` 中至少需要正确配置以下内容：

- `MYSQL_*`
- `HOST`
- `PORT`
- `JWT_*`
- `AI_MODEL_URL`
- `MAIL_*`

## 主要接口

- `POST /registerByAccount`
- `POST /loginByAccount`
- `POST /getPersonalInform`
- `POST /updatePersonalInform`
- `POST /changePassword`
- `POST /saveCaseHistory`
- `GET /getCaseHistory/{reportId}`
- `GET /getPatientsNum`
- `GET /getDiseasesDistribution`
- `POST /getDiseaseConditionByAge`
- `POST /aibo`
- `POST /aiSuggestion`
- `POST /aiQuestion`
- `POST /sendEmail`

## 说明

- 当前业务后端已经直接连接 MySQL，并直接提供登录、统计和病例管理接口
- 图像分析请求会由 `/aibo` 转发到模型服务，请确保 `AI_MODEL_URL` 可访问
