from flask import Flask, redirect, url_for

def create_app():
    app = Flask(__name__)
    
    from app.routes import policy
    app.register_blueprint(policy.bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('policy.index'))
    
    return app 