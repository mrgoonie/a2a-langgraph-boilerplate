from sqlalchemy.orm import Session
from uuid import UUID
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate

def create_conversation(db: Session, conversation: ConversationCreate):
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: UUID):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Conversation).offset(skip).limit(limit).all()
