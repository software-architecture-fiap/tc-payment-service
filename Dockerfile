# Usa uma imagem oficial do Python como base
FROM python:3.10

# Instala dependências do sistema (incluindo curl e gnupg para instalar mongosh)
RUN apt-get update && apt-get install -y curl gnupg && \
    rm -rf /var/lib/apt/lists/*

# Adiciona o repositório oficial do MongoDB e instala o mongosh
RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mongodb-server-keyring.gpg] https://repo.mongodb.org/apt/debian buster/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && apt-get install -y mongodb-mongosh && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /payment-service

# Copia os arquivos do projeto para dentro do container
COPY . .
COPY .env .env

# Instala o Poetry para gerenciar as dependências
RUN pip install --no-cache-dir poetry

# Instala as dependências do projeto usando Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Expõe a porta que o FastAPI usará
EXPOSE 8002

# Define o script de entrada
ENTRYPOINT ["bash", "cmd/entrypoint.sh"]
