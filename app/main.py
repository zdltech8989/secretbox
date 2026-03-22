import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import router as secret_router
from app.auth_routes import router as auth_router
from app.category_routes import router as category_router
from app.export_routes import router as export_router
from app.user_routes import router as user_router
from app.database import init_db

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
HAS_FRONTEND = os.path.isdir(STATIC_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title='SecretBox', version='1.0.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(secret_router)
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(export_router)
app.include_router(user_router)


@app.get('/api/health')
def health():
    return {'status': 'ok'}


# Serve Vue SPA frontend
if HAS_FRONTEND:
    app.mount('/assets', StaticFiles(directory=os.path.join(STATIC_DIR, 'assets')), name='assets')

    @app.get('/{full_path:path}')
    def serve_spa(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, 'index.html'))
else:
    @app.get('/')
    def root():
        return {'status': 'SecretBox running', 'version': '1.0.0'}
