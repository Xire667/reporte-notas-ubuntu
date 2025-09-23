from flask import Flask

def create_app():
        
        app=Flask(__name__)
        
        from .routes import blueprints
        for bp in blueprints:
                app.register_blueprint(bp)
        
        return app