FROM node:18

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# 如果您正在开发中使用
CMD ["npm", "start"]

# 如果您想构建生产版本，可以改为:
# RUN npm run build
# CMD ["npm", "run", "serve"]