#node:26
FROM node@sha256:1b84b89ada025e3b14543cbb837ffaa1c1b5273b841c5b94dd1a8f9c1d8cf7fe

WORKDIR /app

COPY package*.json tsconfig.json ./
COPY vite.config.ts ./

RUN npm install --ignore-scripts

COPY ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]