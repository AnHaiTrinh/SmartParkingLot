from .configs.load_env import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .configs.allowed_origins import allowed_origins
from .routes import user, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
