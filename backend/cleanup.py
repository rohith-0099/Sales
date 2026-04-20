"""
Session cleanup and lifecycle management utilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SessionLifecycleManager:
    """
    Manages session expiration and cleanup.
    Helps prevent memory leaks from accumulating sessions.
    """
    
    def __init__(self, ttl_minutes: int = 90, cleanup_interval: int = 300):
        """
        Initialize the session lifecycle manager.
        
        Args:
            ttl_minutes: Session time-to-live in minutes
            cleanup_interval: Seconds between cleanup runs
        """
        self.ttl_minutes = ttl_minutes
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = datetime.now()
    
    def should_cleanup(self) -> bool:
        """Check if cleanup should run."""
        elapsed = (datetime.now() - self.last_cleanup).total_seconds()
        return elapsed >= self.cleanup_interval
    
    def mark_cleanup_done(self):
        """Record that cleanup was performed."""
        self.last_cleanup = datetime.now()
    
    def is_session_expired(self, created_at: datetime) -> bool:
        """Check if a session has expired."""
        expiry_time = created_at + timedelta(minutes=self.ttl_minutes)
        return datetime.now() > expiry_time
    
    def get_age_seconds(self, created_at: datetime) -> int:
        """Get session age in seconds."""
        return int((datetime.now() - created_at).total_seconds())
    
    def cleanup_expired_sessions(
        self,
        sessions: Dict[str, Dict[str, Any]],
        timestamp_key: str = "created_at"
    ) -> int:
        """
        Remove expired sessions from dictionary.
        
        Args:
            sessions: Dictionary of sessions
            timestamp_key: Key in session dict containing creation timestamp
        
        Returns:
            Number of sessions cleaned up
        """
        expired_ids = []
        
        for session_id, session_data in sessions.items():
            if timestamp_key not in session_data:
                continue
            
            created_at = session_data[timestamp_key]
            if isinstance(created_at, datetime) and self.is_session_expired(created_at):
                expired_ids.append(session_id)
        
        for session_id in expired_ids:
            del sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        if expired_ids:
            self.mark_cleanup_done()
        
        return len(expired_ids)
