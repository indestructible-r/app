from sanic import Sanic
from sanic_ext import Extend
from app.database import get_async_session_maker, init_db
from app.routes import user_bp, admin_bp, webhook_bp
from app.config import APP_HOST, APP_PORT

def create_app():
    app = Sanic('PaymentApp')
    Extend(app)
    
    @app.middleware('request')
    async def db_middleware(request, call_next):
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as session:
            request.ctx.db = session
            response = await call_next(request)
            return response
    
    app.blueprint(user_bp)
    app.blueprint(admin_bp)
    app.blueprint(webhook_bp)
    
    @app.after_server_start
    async def setup_database(app, loop):
        await init_db()
    
    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host=APP_HOST, port=APP_PORT, auto_reload=True)