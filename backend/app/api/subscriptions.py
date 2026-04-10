from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import UserPreferences
from app.schemas.subscription import (
    PreferencesCreate,
    PreferencesUpdate,
    PreferencesResponse,
)

router = APIRouter(prefix="/api/preferences", tags=["preferences"])


@router.get("/", response_model=PreferencesResponse)
async def get_preferences(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)

    return PreferencesResponse.model_validate(preferences)


@router.post("/", response_model=PreferencesResponse)
async def create_preferences(
    preferences_data: PreferencesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Preferences already exist")

    preferences = UserPreferences(
        user_id=current_user.id, **preferences_data.model_dump()
    )
    db.add(preferences)
    await db.commit()
    await db.refresh(preferences)

    return PreferencesResponse.model_validate(preferences)


@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    preferences_data: PreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")

    update_data = preferences_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    await db.commit()
    await db.refresh(preferences)

    return PreferencesResponse.model_validate(preferences)
