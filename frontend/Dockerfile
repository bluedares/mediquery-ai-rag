# Frontend Dockerfile for Railway deployment
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY . .

# Build the app
RUN npm run build

# Expose port
EXPOSE 4173

# Start the preview server
CMD ["npm", "run", "start"]
