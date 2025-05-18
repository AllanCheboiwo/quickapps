# Use a Node.js base image
FROM node:16

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json .
COPY package-lock.json . 
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the port for the development server
EXPOSE 3000

# Command to run the React development server
CMD ["npm", "start"]
