# AgentHub Agent Service — Docker Build
# Python 3.11 + Node.js (for Claude Code CLI) + Claude Code CLI

FROM python:3.11-slim

WORKDIR /app

# 安装 Node.js 20.x + npm（Claude Code CLI 依赖）
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /data/workspaces

# 环境变量
ENV BACKEND_URL=http://backend:8080
ENV AGENT_WORKSPACE_ROOT=/data/workspaces

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
