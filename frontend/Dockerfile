#node:26
FROM node@sha256:32fa97f3363975684b08bf4e8a68a47c7905175cc20275b50b974bbd02aba731

WORKDIR /app

COPY package*.json tsconfig.json ./
COPY vite.config.ts ./

RUN npm install --ignore-scripts

COPY ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]