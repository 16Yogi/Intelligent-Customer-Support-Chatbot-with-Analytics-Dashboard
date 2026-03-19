# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Build with empty API URL so frontend uses same-origin /api (nginx will proxy)
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
RUN npm install --omit=dev

COPY frontend/ .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
