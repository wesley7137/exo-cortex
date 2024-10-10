# security/access_control.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/access_control.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AccessControl:
    def __init__(self):
        self.permissions = {}  # user_id: set of allowed actions

    def grant_permission(self, user_id, action):
        self.permissions.setdefault(user_id, set()).add(action)
        logger.info(f"Granted '{action}' permission to user {user_id}.")

    def revoke_permission(self, user_id, action):
        self.permissions.get(user_id, set()).discard(action)
        logger.info(f"Revoked '{action}' permission from user {user_id}.")

    def check_permission(self, user_id, action):
        allowed = action in self.permissions.get(user_id, set())
        logger.debug(f"Permission check for user {user_id}, action '{action}': {allowed}")
        return allowed
