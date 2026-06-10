# AgentHub Frontend — Multi-stage Docker Build
# Stage 1: Build Vue 3 app
# Stage 2: Serve with Nginx

# ============================================
# Stage 1: Build
# ============================================
FROM node:20-alpine AS builder

# 构建时通过 --build-arg 传入后端 API 地址
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ============================================
# Stage 2: Serve
# ============================================
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
