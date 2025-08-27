from fastapi import FastAPI
from chatbot import router as chatbot_router
from locater import router as locater_router

app = FastAPI()
app.include_router(chatbot_router)
app.include_router(locater_router)