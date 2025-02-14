from pymongo import MongoClient
import os
from dotenv import load_dotenv
from ..tools.logging import logger
from pymongo.errors import ConnectionFailure

# Carregar variáveis de ambiente
load_dotenv()

# Pegar a URI do ambiente
MONGO_URI = os.getenv("MONGO_URI", "")

try:
    # Criar conexão com o MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # Timeout de 5s
    
    # Testar conexão
    client.admin.command('ping')
    logger.info("Conexão com MongoDB bem-sucedida!")
    
    # Obter banco de dados e coleção
    db = client["payment_service"]
    payments_collection = db["payments"]
    logger.info(f"payments_collection: {payments_collection}")
except ConnectionFailure as e:
    logger.error(f"Erro na conexão com MongoDB: {e}")
    raise  # Lança a exceção para interromper a execução
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
    raise  # Lança a exceção para interromper a execução
