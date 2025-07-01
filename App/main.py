from App.users.routes import router as users_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.mysql import engine, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


@app.get('/')
def welcome():
    return {"message": "Welcome to the API"}

app.include_router(users_router, prefix="/users", tags=["Users"])
