from app.routes.user import user_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

__all__ = ['user_bp', 'admin_bp', 'webhook_bp']