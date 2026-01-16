import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Player
from app.schemas import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerListResponse

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[PlayerListResponse])
async def list_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sport: Optional[str] = Query(None),
    team: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all detected players with optional filtering."""
    query = db.query(Player)

    if sport:
        query = query.filter(Player.sport == sport)
    if team:
        query = query.filter(Player.team == team)

    players = query.order_by(Player.name).offset(skip).limit(limit).all()
    return players


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific player by ID."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("", response_model=PlayerResponse)
async def create_player(player_data: PlayerCreate, db: Session = Depends(get_db)):
    """Manually create a player entry."""
    player = Player(**player_data.model_dump())
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: uuid.UUID,
    update_data: PlayerUpdate,
    db: Session = Depends(get_db),
):
    """Update player information (name, aliases, team, etc.)."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}")
async def delete_player(player_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a player and associated analysis results."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}


@router.post("/import")
async def import_players(players: List[PlayerCreate], db: Session = Depends(get_db)):
    """Bulk import player roster."""
    created_players = []
    for player_data in players:
        # Check if player already exists by name
        existing = db.query(Player).filter(Player.name == player_data.name).first()
        if existing:
            # Update existing player
            for field, value in player_data.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(existing, field, value)
            created_players.append(existing)
        else:
            # Create new player
            player = Player(**player_data.model_dump())
            db.add(player)
            created_players.append(player)

    db.commit()
    return {
        "message": f"Imported {len(created_players)} players",
        "count": len(created_players),
    }
