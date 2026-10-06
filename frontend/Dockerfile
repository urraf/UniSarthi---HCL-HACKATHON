FROM node:20-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

EXPOSE 5173
# VITE_API_URL comes from docker-compose (environment), not from the code
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
