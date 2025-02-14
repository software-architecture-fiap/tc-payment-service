#!/bin/bash

# Aguarda o MongoDB iniciar
echo "Aguardando o MongoDB iniciar..."
echo "MongoDB está pronto!"

# Inicia o FastAPI com Uvicorn
echo "Iniciando o FastAPI..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
