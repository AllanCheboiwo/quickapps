# Use a Node.js base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Set environment variable to indicate we're in Docker
ENV DOCKER_ENV=true

# Build the Next.js application
RUN npm run build

# Expose the port for the Next.js server
EXPOSE 3000

# Command to run the Next.js production server
CMD ["npm", "start"]
