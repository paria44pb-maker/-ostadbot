import os
import re

class Security:
    """
    Security layer for CryptoPulseAI
    """

    BLACKLIST_PATTERNS = [
        r"rm -rf",
        r"shutdown",
        r"format",
        r"del /f",
    ]

    @staticmethod
    def is_admin(user_id: int) -> bool:
        admins = os.getenv("ADMIN_IDS", "")
        admin_list = [a.strip() for a in admins.split(",") if a.strip()]
        return str(user_id) in admin_list

    @staticmethod
    def sanitize(text: str) -> str:
        """
        Remove dangerous patterns from input
        """
        if not text:
            return ""

        for pattern in Security.BLACKLIST_PATTERNS:
            text = re.sub(pattern, "***", text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def validate_command(command: str) -> bool:
        """
        Basic command validation for bot inputs
        """
        if not command:
            return False

        if len(command) > 200:
            return False

        if any(char in command for char in ["<", ">", "{", "}"]):
            return False

        return True
