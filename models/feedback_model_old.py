# SQLAlchemy model for feedback

import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import String, Text, Boolean, DateTime, Column
from models import db

class MessageFeedback(db.Model):
    __tablename__ = 'message_feedback'

    entry_id = db.Column('uuid', String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(Text, nullable=True)
    company_name = db.Column(Text, nullable=True)
    industry = db.Column(Text, nullable=True)
    tone = db.Column(Text, nullable=True)
    focus = db.Column(Text, nullable=True)
    context = db.Column(Text, nullable=True)
    model_used = db.Column(Text, nullable=True)
    prompt_template = db.Column(Text, nullable=True)
    prompt_text = db.Column(Text, nullable=True)
    generated_message = db.Column(JSONB, nullable=True)
    is_upvote = db.Column(Boolean, default=False)
    is_downvote = db.Column(Boolean, default=False)
    is_regeneration = db.Column(Boolean, default=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MessageFeedback {self.id}>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'tone': self.tone,
            'focus': self.focus,
            'context': self.context,
            'model_used': self.model_used,
            'prompt_template': self.prompt_template,
            'prompt_text': self.prompt_text,
            'generated_message': self.generated_message,
            'is_upvote': self.is_upvote,
            'is_downvote': self.is_downvote,
            'is_regeneration': self.is_regeneration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
