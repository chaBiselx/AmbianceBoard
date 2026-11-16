#node:26
FROM node@sha256:6d2c7d5d074bf72f81ddc252b4fbb5d625bc028eeda49cb4b8c2ff8eda1ee617

WORKDIR /app

COPY package*.json tsconfig.json ./
COPY vite.config.ts ./

RUN npm install --ignore-scripts

COPY ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]