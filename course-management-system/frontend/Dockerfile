# 多阶段构建 - 构建阶段
FROM node:18-alpine as build

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 设置环境变量跳过Cypress安装
ENV CYPRESS_INSTALL_BINARY=0

# 安装依赖（包含 devDependencies 以便构建）
RUN npm ci --legacy-peer-deps

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段 - 使用nginx提供静态文件
FROM nginx:alpine

# 复制构建产物到nginx目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 设置权限（nginx用户已存在于基础镜像中）
RUN chown -R nginx:nginx /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
