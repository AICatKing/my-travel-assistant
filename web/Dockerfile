# --- 第一阶段: 构建前端 ---
FROM node:22-slim AS builder

WORKDIR /app

# 拷贝依赖配置
COPY package*.json ./
RUN npm install

# 拷贝源代码并构建
COPY . .
# 生产环境通常需要将 API 地址改为相对路径 /api，Nginx 会处理代理
# 我们修改 App.vue 中的 baseURL 逻辑或使用环境变量
RUN npm run build

# --- 第二阶段: Nginx 托管 ---
FROM nginx:stable-alpine

# 拷贝构建好的文件
COPY --from=builder /app/dist /usr/share/nginx/html

# 拷贝 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
