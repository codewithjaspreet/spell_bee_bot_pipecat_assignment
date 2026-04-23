
from fastapi import FastAPI
from app.routes.session import router as session_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="SpellBee Voice Bot")

# add cors
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    
)

app.include_router(session_router, prefix="/api")