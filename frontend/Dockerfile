# ==================== 构建阶段 ====================
FROM node:20-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --legacy-peer-deps

# 复制源代码
COPY . .

# 清理并重新安装以解决rollup依赖问题
RUN rm -rf node_modules package-lock.json && npm install --legacy-peer-deps

# 构建生产版本
RUN npm run build

# ==================== 生产阶段 ====================
FROM nginx:1.25-alpine

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
