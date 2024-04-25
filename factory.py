from config import db,bcrypt,jwt,Config
from flask import Flask
from routes import auth_router,user_router
from middleware.token_required import token_reqiured
from flask_cors import CORS



def createapp():
  
  app = Flask(__name__)
  app.config.from_object(Config)
  app.secret_key = Config.APP_SECRET_KEY
  app.register_blueprint(auth_router.auth_route)
  app.register_blueprint(user_router.user_route)
  CORS(app)
  CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}},supports_credentials=True)
  app.before_request(token_reqiured)
  db.init_app(app=app)
  bcrypt.init_app(app=app)
  jwt.init_app(app=app)
  return app