# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /HUT

# 复制项目文件到容器中
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8800

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800"]
