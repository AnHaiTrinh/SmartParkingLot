from .configs.load_env import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .configs.allowed_origins import allowed_origins
from .routes import user, auth, parking_lot, vehicle, activity_log, rating_feedback, parking_space
from fastapi_pagination import add_pagination
from app.internal.admin import admin
from app.internal.device import devices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(parking_lot.router)
app.include_router(vehicle.router)
app.include_router(activity_log.router)
app.include_router(rating_feedback.router)
app.include_router(parking_space.router)
app.include_router(admin.router)
app.include_router(devices.router)

add_pagination(app)


@app.get("/")
def root():
    return {"message": "Hello World"}
