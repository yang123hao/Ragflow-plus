# 后端构建阶段
FROM python:3.10.16 AS backend
# 安装 LibreOffice 及字体支持
RUN apt-get update && \
    apt-get install -y libreoffice fonts-noto-cjk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 复制后端代码
COPY . /app

# 创建必要的目录（如果需要的话）
RUN mkdir -p /root/.cache/huggingface/hub/ || true
RUN mkdir -p /root/nltk_data || true

# 设置环境变量确保端口正确
ENV FLASK_RUN_PORT=5001
ENV FLASK_ENV=production

# 暴露后端端口
EXPOSE 5001
CMD ["python", "app.py"]
