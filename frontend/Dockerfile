#node:26
FROM node@sha256:bde0dae02f2b12d2bce5ee72b2432f0e511767b7b2dc4dd3b064df11ae422fee

WORKDIR /app

COPY package*.json tsconfig.json ./
COPY vite.config.ts ./

RUN npm install --ignore-scripts

COPY ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]