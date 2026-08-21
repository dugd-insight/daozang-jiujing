# ===== 阶段一: 构建站点 (python + OpenCC) =====
FROM python:3.11-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir opencc-python-reimplemented
# 站点数据与生成脚本
COPY site/ /build/site/
COPY scripts/ /build/scripts/
RUN cd /build && python3 scripts/generate_all.py

# ===== 阶段二: 运行 (Node, 零依赖) =====
FROM node:22-alpine
WORKDIR /app
ENV PORT=8123
COPY server.js package.json ./
COPY --from=builder /build/site/ ./site/
EXPOSE 8123
USER node
CMD ["node", "server.js"]
