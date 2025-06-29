"""
Feedback Controller for Email Generation System
Handles upvote, downvote, and regeneration feedback functionality
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, jsonify, session
from sqlalchemy.exc import SQLAlchemyError

from models.feedback_model import MessageFeedback, db
from controllers.generate_controller import GenerateController
from controllers.prompt_controller import  get_prompt_path
from logging_setup import setup_logging

# Get logger instance (logging setup should be called in app.py)
logger = logging.getLogger(__name__)

class FeedbackController:
    """
    Controller class to handle all feedback-related operations
    including upvote, downvote, and regeneration functionality
    """
    
    def __init__(self):
        self.generate_controller = GenerateController()
        self.prompt_controller = get_prompt_path()
    
    def capture_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture user feedback (upvote/downvote) and store in database
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Validate required fields
            required_fields = ['message_id', 'feedback_type', 'user_id', 'company_name', 
                             'industry', 'tone', 'focus', 'context', 'model_used', 
                             'prompt_template', 'prompt_text', 'generated_message']
            
            missing_fields = [field for field in required_fields if field not in feedback_data]
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Validate feedback type
            if feedback_data['feedback_type'] not in ['upvote', 'downvote']:
                return {
                    'success': False,
                    'error': 'Invalid feedback type. Must be "upvote" or "downvote"'
                }
            
            # Create feedback record
            feedback_record = MessageFeedback(
                id=str(uuid.uuid4()),
                user_id=feedback_data['user_id'],
                company_name=feedback_data['company_name'],
                industry=feedback_data['industry'],
                tone=feedback_data['tone'],
                focus=feedback_data['focus'],
                context=feedback_data['context'],
                model_used=feedback_data['model_used'],
                prompt_template=feedback_data['prompt_template'],
                prompt_text=feedback_data['prompt_text'],
                generated_message=feedback_data['generated_message'],
                is_upvote=feedback_data['feedback_type'] == 'upvote',
                is_downvote=feedback_data['feedback_type'] == 'downvote',
                is_regeneration=False,
                timestamp=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(feedback_record)
            db.session.commit()
            
            logger.info(f"Feedback captured successfully: {feedback_data['feedback_type']} for message_id: {feedback_data['message_id']}")
            
            return {
                'success': True,
                'message': f'Feedback ({feedback_data["feedback_type"]}) captured successfully',
                'feedback_id': feedback_record.id
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
    
    def handle_regeneration(self, regeneration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle regeneration request - generate new content with same or different model
        
        Args:
            regeneration_data: Dictionary containing regeneration parameters
            
        Returns:
            Dictionary with new generated content and success status
        """
        try:
            # Validate required fields for regeneration
            required_fields = ['user_id', 'company_name', 'industry', 'tone', 
                             'focus', 'context', 'model_choice']
            
            missing_fields = [field for field in required_fields if field not in regeneration_data]
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Store original request data for feedback logging
            original_data = regeneration_data.get('original_data', {})
            
            # Generate new content using the generate controller
            generation_payload = {
                'company_name': regeneration_data['company_name'],
                'industry': regeneration_data['industry'],
                'tone': regeneration_data['tone'],
                'focus': regeneration_data['focus'],
                'context': regeneration_data['context'],
                'model_choice': regeneration_data['model_choice']
            }
            
            # Call generate controller to create new content
            generation_result = self.generate_controller.generate_email(generation_payload)
            
            if not generation_result.get('success', False):
                return {
                    'success': False,
                    'error': 'Failed to generate new content',
                    'details': generation_result.get('error', 'Unknown error')
                }
            
            # Log regeneration as feedback if original data exists
            if original_data:
                regeneration_feedback = MessageFeedback(
                    id=str(uuid.uuid4()),
                    user_id=regeneration_data['user_id'],
                    company_name=original_data.get('company_name', regeneration_data['company_name']),
                    industry=original_data.get('industry', regeneration_data['industry']),
                    tone=original_data.get('tone', regeneration_data['tone']),
                    focus=original_data.get('focus', regeneration_data['focus']),
                    context=original_data.get('context', regeneration_data['context']),
                    model_used=original_data.get('model_used', 'unknown'),
                    prompt_template=original_data.get('prompt_template', 'unknown'),
                    prompt_text=original_data.get('prompt_text', ''),
                    generated_message=original_data.get('generated_message', {}),
                    is_upvote=False,
                    is_downvote=False,
                    is_regeneration=True,
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(regeneration_feedback)
                db.session.commit()
            
            logger.info(f"Regeneration completed successfully for user: {regeneration_data['user_id']}")
            
            return {
                'success': True,
                'message': 'Content regenerated successfully',
                'generated_content': generation_result.get('generated_message', ''),
                'model_used': generation_result.get('model_used', ''),
                'prompt_template': generation_result.get('prompt_template', ''),
                'prompt_text': generation_result.get('prompt_text', ''),
                'generation_id': generation_result.get('generation_id', ''),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during regeneration: {str(e)}")
            return {
                'success': False,
                'error': 'Database error occurred during regeneration'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error during regeneration: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred during regeneration'
            }
    
    def get_feedback_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve feedback analytics and statistics
        
        Args:
            filters: Optional filters for analytics (user_id, model_used, date_range, etc.)
            
        Returns:
            Dictionary containing analytics data
        """
        try:
            query = MessageFeedback.query
            
            # Apply filters if provided
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
            
            # Get all feedback records
            feedback_records = query.all()
            
            # Calculate analytics
            total_feedback = len(feedback_records)
            upvotes = sum(1 for record in feedback_records if record.is_upvote)
            downvotes = sum(1 for record in feedback_records if record.is_downvote)
            regenerations = sum(1 for record in feedback_records if record.is_regeneration)
            
            # Model performance
            model_stats = {}
            for record in feedback_records:
                model = record.model_used
                if model not in model_stats:
                    model_stats[model] = {'upvotes': 0, 'downvotes': 0, 'regenerations': 0}
                
                if record.is_upvote:
                    model_stats[model]['upvotes'] += 1
                elif record.is_downvote:
                    model_stats[model]['downvotes'] += 1
                elif record.is_regeneration:
                    model_stats[model]['regenerations'] += 1
            
            # Tone and focus performance
            tone_stats = {}
            focus_stats = {}
            
            for record in feedback_records:
                # Tone stats
                tone = record.tone
                if tone not in tone_stats:
                    tone_stats[tone] = {'upvotes': 0, 'downvotes': 0}
                if record.is_upvote:
                    tone_stats[tone]['upvotes'] += 1
                elif record.is_downvote:
                    tone_stats[tone]['downvotes'] += 1
                
                # Focus stats
                focus = record.focus
                if focus not in focus_stats:
                    focus_stats[focus] = {'upvotes': 0, 'downvotes': 0}
                if record.is_upvote:
                    focus_stats[focus]['upvotes'] += 1
                elif record.is_downvote:
                    focus_stats[focus]['downvotes'] += 1
            
            return {
                'success': True,
                'analytics': {
                    'total_feedback': total_feedback,
                    'upvotes': upvotes,
                    'downvotes': downvotes,
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
    
    def get_user_feedback_history(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get feedback history for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
            
        Returns:
            Dictionary containing user's feedback history
        """
        try:
            feedback_records = MessageFeedback.query.filter(
                MessageFeedback.user_id == user_id
            ).order_by(MessageFeedback.timestamp.desc()).limit(limit).all()
            
            history = []
            for record in feedback_records:
                history.append({
                    'id': record.id,
                    'company_name': record.company_name,
                    'industry': record.industry,
                    'tone': record.tone,
                    'focus': record.focus,
                    'model_used': record.model_used,
                    'prompt_template': record.prompt_template,
                    'is_upvote': record.is_upvote,
                    'is_downvote': record.is_downvote,
                    'is_regeneration': record.is_regeneration,
                    'timestamp': record.timestamp.isoformat()
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
    
    def delete_feedback(self, feedback_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a specific feedback record (if user has permission)
        
        Args:
            feedback_id: Feedback record ID
            user_id: User identifier for permission check
            
        Returns:
            Dictionary with success status
        """
        try:
            feedback_record = MessageFeedback.query.filter(
                MessageFeedback.id == feedback_id,
                MessageFeedback.user_id == user_id
            ).first()
            
            if not feedback_record:
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