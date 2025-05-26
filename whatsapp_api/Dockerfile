# ---- Estágio de Build ----
# Usamos um alias "builder" para este estágio
FROM node:24-alpine AS builder

# Define o diretório de trabalho no container
WORKDIR /usr/src/app

# Copia package.json e package-lock.json (se disponível)
# Copiar ambos garante que o cache seja invalidado se qualquer um deles mudar.
COPY package*.json ./

# Instala todas as dependências, incluindo devDependencies se necessário para algum passo de build
# Se você não tem um passo de build que precise de devDependencies, pode usar --only=production aqui também.
# Para um build mais rápido e determinístico, use 'npm ci' se você tiver um package-lock.json
RUN npm install

# Copia o restante do código da aplicação
COPY . .

# (Opcional) Se sua aplicação tiver um passo de build (ex: TypeScript, Babel, Webpack)
# RUN npm run build

# ---- Estágio de Produção ----
# Começa de uma nova imagem base Node slim para manter a imagem final pequena
FROM node:24-alpine AS production

# Define o diretório de trabalho no container
WORKDIR /usr/src/app

# Instala curl para a verificação de saúde e limpa o cache do apt
# Fazemos isso no estágio de produção porque o curl é necessário em tempo de execução.
RUN apk update && \
    apk add --no-cache curl && \
    rm -rf /var/cache/apk/*

# Copia package.json e package-lock.json
COPY package*.json ./

# Instala APENAS as dependências de produção
RUN npm install --only=production --ignore-scripts --prefer-offline

# Copia os artefatos da aplicação do estágio de build
# Se você tiver um passo de build, ajuste o caminho de origem, por exemplo: COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app ./

# Expõe a porta que a aplicação usa
EXPOSE 3000

# (Opcional) Define a variável de ambiente para produção
# ENV NODE_ENV production

# Comando para executar a aplicação
CMD [ "node", "index.js" ]