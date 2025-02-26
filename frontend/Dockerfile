FROM node:18

WORKDIR /app

COPY package*.json tsconfig.json ./
COPY vite.config.ts ./

RUN npm install

COPY ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]