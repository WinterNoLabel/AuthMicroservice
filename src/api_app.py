from fastapi import FastAPI
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from api.controllers.auth_controller import router as auth_router


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

app = FastAPI(
    title="Auth Microservice API",
    version="0.0.1",
    docs_url="/docs",
    middleware=middleware,
)

app.include_router(auth_router)
