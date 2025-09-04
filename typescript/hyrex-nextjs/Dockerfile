# Use Node.js LTS (Long Term Support) as the base image
FROM node:20-slim

# Create app directory
WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Compile TypeScript
RUN npm install -g typescript ts-node
RUN tsc

# Start the application
CMD npx hyrex init-db hyrex/hyrex-app.ts && npx hyrex run-worker hyrex/hyrex-app.ts 2
