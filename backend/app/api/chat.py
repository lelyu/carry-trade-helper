from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse
from app.agents.carry_trade_agent import carry_trade_agent

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_message = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=message.content
    )
    db.add(user_message)
    await db.commit()
    
    chat_history = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    chat_history = chat_history.scalars().all()[::-1]
    
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in chat_history
    ]
    
    result = carry_trade_agent.invoke({"messages": messages})
    
    assistant_content = result["messages"][-1].content
    
    assistant_message = ChatMessage(
        user_id=current_user.id,
        role="assistant",
        content=assistant_content
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return ChatMessageResponse.from_orm(assistant_message)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()[::-1]
    
    return ChatHistoryResponse(
        messages=[ChatMessageResponse.from_orm(msg) for msg in messages],
        count=len(messages)
    )