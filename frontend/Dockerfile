FROM node:26

WORKDIR /app

RUN mkdir -p /app/.npm-cache /app/static/css /app/static/js /app/static/img /app/static/webfonts && \
	chown -R node:node /app

COPY --chown=node:node package*.json tsconfig.json ./
COPY --chown=node:node vite.config.ts ./

USER node

RUN npm config set cache /app/.npm-cache && \
	npm install --ignore-scripts && \
	chmod -R u+w /app/node_modules

COPY --chown=node:node ./src ./src

# Compiler pour produire les assets au démarrage
CMD ["npm", "run", "watch"]