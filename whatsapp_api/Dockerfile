# Use an official Node.js runtime as a parent image
FROM node:23-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install app dependencies
RUN npm install --only=production

# Bundle app source
COPY . .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define environment variable (optional, if your app uses it)
# ENV NODE_ENV production

# Run index.js when the container launches
CMD [ "node", "index.js" ]
