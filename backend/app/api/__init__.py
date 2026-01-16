from fastapi import APIRouter
from app.api import transcripts, players, analysis

api_router = APIRouter()

api_router.include_router(transcripts.router)
api_router.include_router(players.router)
api_router.include_router(analysis.router)
