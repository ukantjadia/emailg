import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from models.feedback_model import MessageFeedback, db
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from config.config import Config

logger = logging.getLogger(__name__)

class FeedbackController:
    """
    Handles all feedback-related operations: upvote, downvote, regeneration, analytics, history, and deletion.
    All methods are static as this controller is stateless.
    """

    @staticmethod
    def capture_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture user feedback (upvote/downvote/generation/regeneration) and store in the database.
        Returns a dict with success status and message.
        """
        logger.info(f"Capturing feedback: {feedback_data}")
        required_fields = [
            'message_id', 'feedback_type', 'company_name',
            'industry', 'tone', 'focus', 'context', 'model_used',
            'prompt_template', 'prompt_text', 'generated_message'
        ]
        missing_fields = [f for f in required_fields if f not in feedback_data]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return {
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }

        # Accept 'generation' as a feedback_type for initial logging
        valid_types = ['upvote', 'downvote', 'generation', 'regeneration']
        if feedback_data['feedback_type'] not in valid_types:
            logger.error(f"Invalid feedback type: {feedback_data['feedback_type']}")
            return {
                'success': False,
                'error': f'Invalid feedback type. Must be one of {valid_types}'
            }

        # Handle user_id defaulting
        user_id = feedback_data.get('user_id')
        if not user_id:
            user_id = 'test_user'

        try:
            feedback_record = MessageFeedback(
                entry_id=str(uuid.uuid4()),
                message_id=feedback_data['message_id'],
                parent_message_id=feedback_data.get('parent_message_id'),
                user_id=user_id,
                company_name=feedback_data['company_name'],
                industry=feedback_data['industry'],
                tone=feedback_data['tone'],
                focus=feedback_data['focus'],
                context=feedback_data['context'],
                model_used=feedback_data['model_used'],
                prompt_template=feedback_data['prompt_template'],
                prompt_text=feedback_data['prompt_text'],
                generated_message=feedback_data['generated_message'],
                feedback_type=feedback_data['feedback_type'],
                timestamp=datetime.utcnow()
            )
            db.session.add(feedback_record)
            db.session.commit()
            logger.info(f"Feedback ({feedback_data['feedback_type']}) captured for message_id: {feedback_data['message_id']}")
            return {
                'success': True,
                'message': f'Feedback ({feedback_data["feedback_type"]}) captured successfully',
                'feedback_id': feedback_record.entry_id
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while capturing feedback: {str(e)}")
            return {
                'success': False,
                'error': 'Database error occurred while saving feedback'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error while capturing feedback: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred while processing feedback'
            }

    @staticmethod
    def get_feedback_analytics(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve feedback analytics and statistics.
        Returns a dict containing analytics data.
        """
        logger.info(f"Retrieving feedback analytics with filters: {filters}")
        try:
            query = MessageFeedback.query
            if filters:
                if 'user_id' in filters:
                    query = query.filter(MessageFeedback.user_id == filters['user_id'])
                if 'model_used' in filters:
                    query = query.filter(MessageFeedback.model_used == filters['model_used'])
                if 'tone' in filters:
                    query = query.filter(MessageFeedback.tone == filters['tone'])
                if 'focus' in filters:
                    query = query.filter(MessageFeedback.focus == filters['focus'])
                if 'start_date' in filters and 'end_date' in filters:
                    query = query.filter(
                        MessageFeedback.timestamp >= filters['start_date'],
                        MessageFeedback.timestamp <= filters['end_date']
                    )
            feedback_records = query.all()
            total_feedback = len(feedback_records)
            upvotes = sum(1 for record in feedback_records if record.feedback_type == 'upvote')
            downvotes = sum(1 for record in feedback_records if record.feedback_type == 'downvote')
            generations = sum(1 for record in feedback_records if record.feedback_type == 'generation')
            regenerations = sum(1 for record in feedback_records if record.feedback_type == 'regeneration')
            model_stats = {}
            for record in feedback_records:
                model = record.model_used
                if model not in model_stats:
                    model_stats[model] = {'upvotes': 0, 'downvotes': 0, 'generations': 0, 'regenerations': 0}
                if record.feedback_type == 'upvote':
                    model_stats[model]['upvotes'] += 1
                elif record.feedback_type == 'downvote':
                    model_stats[model]['downvotes'] += 1
                elif record.feedback_type == 'generation':
                    model_stats[model]['generations'] += 1
                elif record.feedback_type == 'regeneration':
                    model_stats[model]['regenerations'] += 1
            tone_stats = {}
            focus_stats = {}
            for record in feedback_records:
                tone = record.tone
                if tone not in tone_stats:
                    tone_stats[tone] = {'upvotes': 0, 'downvotes': 0}
                if record.feedback_type == 'upvote':
                    tone_stats[tone]['upvotes'] += 1
                elif record.feedback_type == 'downvote':
                    tone_stats[tone]['downvotes'] += 1
                focus = record.focus
                if focus not in focus_stats:
                    focus_stats[focus] = {'upvotes': 0, 'downvotes': 0}
                if record.feedback_type == 'upvote':
                    focus_stats[focus]['upvotes'] += 1
                elif record.feedback_type == 'downvote':
                    focus_stats[focus]['downvotes'] += 1
            return {
                'success': True,
                'analytics': {
                    'total_feedback': total_feedback,
                    'upvotes': upvotes,
                    'downvotes': downvotes,
                    'generations': generations,
                    'regenerations': regenerations,
                    'satisfaction_rate': (upvotes / (upvotes + downvotes)) * 100 if (upvotes + downvotes) > 0 else 0,
                    'model_performance': model_stats,
                    'tone_performance': tone_stats,
                    'focus_performance': focus_stats
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving feedback analytics: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve feedback analytics'
            }

    @staticmethod
    def get_user_feedback_history(user_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get feedback history for a specific user.
        Returns a dict containing the user's feedback history.
        """
        logger.info(f"Retrieving feedback history for user_id: {user_id}")
        try:
            feedback_records = MessageFeedback.query.filter(
                MessageFeedback.user_id == user_id
            ).order_by(MessageFeedback.timestamp.desc()).limit(limit).all()
            history = []
            for record in feedback_records:
                history.append({
                    'entry_id': record.entry_id,
                    'message_id': record.message_id,
                    'company_name': record.company_name,
                    'industry': record.industry,
                    'tone': record.tone,
                    'focus': record.focus,
                    'model_used': record.model_used,
                    'prompt_template': record.prompt_template,
                    'feedback_type': record.feedback_type,
                    'timestamp': record.timestamp.isoformat(),
                    'generated_message': record.generated_message
                })
            return {
                'success': True,
                'history': history,
                'total_records': len(history)
            }
        except Exception as e:
            logger.error(f"Error retrieving user feedback history: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve feedback history'
            }

    @staticmethod
    def delete_feedback(feedback_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a specific feedback record (if user has permission).
        Returns a dict with success status.
        """
        logger.info(f"Deleting feedback record: {feedback_id} for user: {user_id}")
        try:
            feedback_record = MessageFeedback.query.filter(
                MessageFeedback.entry_id == feedback_id,
                MessageFeedback.user_id == user_id
            ).first()
            if not feedback_record:
                logger.error(f"Feedback record not found or access denied: {feedback_id}")
                return {
                    'success': False,
                    'error': 'Feedback record not found or access denied'
                }
            db.session.delete(feedback_record)
            db.session.commit()
            logger.info(f"Feedback record {feedback_id} deleted successfully")
            return {
                'success': True,
                'message': 'Feedback record deleted successfully'
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while deleting feedback: {str(e)}")
            return {
                'success': False,
                'error': 'Database error occurred while deleting feedback'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error while deleting feedback: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred while deleting feedback'
            }


