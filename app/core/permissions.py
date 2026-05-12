from typing import Optional
from modules.users.models import User

class UXControlLayer:
    """
    Centralized Permission and Visibility logic sitting between Handlers, Services, and DB.
    """
    
    @staticmethod
    def can_receive_anonymous_message(receiver: Optional[User]) -> bool:
        if not receiver:
            return False
        if getattr(receiver, 'is_banned', False):
            return False
        return getattr(receiver, 'allow_anonymous_messages', True)

    @staticmethod
    def can_participate_in_friendship(receiver: Optional[User]) -> bool:
        if not receiver:
            return False
        if getattr(receiver, 'is_banned', False):
            return False
        return getattr(receiver, 'allow_friend_requests', True)

    @staticmethod
    def can_participate_in_polls(receiver: Optional[User]) -> bool:
        if not receiver:
            return False
        if getattr(receiver, 'is_banned', False):
            return False
        return getattr(receiver, 'allow_polls', True)

    @staticmethod
    def check_global_action_block(user: Optional[User]) -> tuple[bool, str]:
        """Returns True if the user is ALLOWED to act. Otherwise False and a reason."""
        if not user:
            return False, "User not found."
            
        if getattr(user, 'is_banned', False):
            return False, "Siz platformadan bloklangansiz. Barcha tizimlar yopilgan. 🛑"
            
        from datetime import datetime
        import pytz
        if getattr(user, 'is_muted', False):
            # Also check if it's expired
            if user.is_muted_until:
                now_utc = datetime.utcnow()
                # Assuming naive utc from DB
                if user.is_muted_until > now_utc:
                    return False, "Siz vaqtinchalik yozish funksiyasidan mahrumsiz. 🔇"
                else:
                    # Expired mute
                    user.is_muted = False
                    user.is_muted_until = None
            else:
                return False, "Siz vaqtinchalik yozish funksiyasidan mahrumsiz. 🔇"
                
        return True, ""
