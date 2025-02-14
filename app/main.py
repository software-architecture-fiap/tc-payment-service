import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

from .middleware.middleware import ExceptionLoggingMiddleware
from .routers import payments, test_routes
from .tools.logging import logger

app = FastAPI()

logger.info('Application startup')

# Configuração do CORS
origins = [
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:8002',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Incluindo os roteadores
app.add_middleware(ExceptionLoggingMiddleware)
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(test_routes.router, prefix="/tests", tags=["tests"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status code": 422,
            "msg": f"Validation error in request body or parameters: {exc.errors()}"
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status code": exc.status_code,
            "msg": exc.detail,
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status code": 500,
            "msg": "An unexpected error occurred. Please try again later or contact your Support Team."
        },
    )

@app.get('/health', tags=['health'])
def health_check() -> dict:
    """Retorna o status operacional da aplicação.

    Returns:
        dict: Um dicionário com o status da aplicação.
    """
    logger.debug('Status endpoint accessed')
    return {'status': 'Operational'}

# Adiciona a rota para a documentação do ReDoc
@app.get('/redoc', include_in_schema=False, tags=['documentation'])
async def redoc() -> str:
    """Retorna o HTML para a documentação do ReDoc.

    Returns:
        str: O HTML da documentação do ReDoc.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - ReDoc',
        redoc_js_url='https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js',
    )

@app.get('/docs', tags=['documentation'])
def get_docs():
    return app.openapi()

def run_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=True)

if __name__ == '__main__':
    run_server()