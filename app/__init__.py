from flask import Flask
from config.settings import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 블루프린트 등록
    from app.routes import main, firewall, policy
    app.register_blueprint(main.bp)
    app.register_blueprint(firewall.bp)
    app.register_blueprint(policy.bp)
    
    return app 