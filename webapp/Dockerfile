# Builder image
FROM node:10.16.0-alpine as build

# Copy package.json and install dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --silent

# Build react app
COPY . .
RUN npm run build


# Final image
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80