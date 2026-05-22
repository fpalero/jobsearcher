# Use Node.js 20 image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for @angular/cli)
RUN npm ci

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 4200

# Run the application
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--disable-host-check"]