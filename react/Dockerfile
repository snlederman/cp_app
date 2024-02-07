# Node image
FROM node:14

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./react_app/package*.json ./

# Install dependencies
RUN npm install

# Copy the source code
COPY ./react_app/ ./

# Build the app
RUN npm run build

# Start the app using serve
CMD ["npx", "serve", "-s", "build", "-l", "3000"]

