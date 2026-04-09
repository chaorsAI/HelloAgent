# FROM python:3.11-slim

# docker内置
FROM ghcr.io/astral-sh/uv:python3.11-bookworm

WORKDIR /app

# 复制 uv 配置文件（依赖声明 + 版本锁文件，*兼容无锁文件的情况）
COPY pyproject.toml uv.lock* ./
# 【推荐】uv 安装生产依赖（不装开发依赖，速度极快）
RUN uv sync --no-dev --production --system  # 直接装到系统里

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "server.py"]
