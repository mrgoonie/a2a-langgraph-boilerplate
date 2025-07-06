from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.auth import get_api_key_with_rate_limit
from app.services import conversation as conversation_service
from app.schemas import conversation as conversation_schema

router = APIRouter()

@router.post("/", response_model=conversation_schema.Conversation)
def create_conversation(
    conversation: conversation_schema.ConversationCreate, 
    db: Session = Depends(get_db),
    api_key: str = Security(get_api_key_with_rate_limit)
):
    return conversation_service.create_conversation(db=db, conversation=conversation)

@router.get("/", response_model=list[conversation_schema.Conversation])
def read_conversations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    api_key: str = Security(get_api_key_with_rate_limit)
):
    conversations = conversation_service.get_conversations(db, skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=conversation_schema.Conversation)
def read_conversation(
    conversation_id: UUID, 
    db: Session = Depends(get_db),
    api_key: str = Security(get_api_key_with_rate_limit)
):
    db_conversation = conversation_service.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db_conversation
