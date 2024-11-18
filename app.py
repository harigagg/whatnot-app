import redis
from flask import Flask
from routes import event_handler, access_checker
from config import Config
from flask_redis import FlaskRedis
from models import db
# Initialize Flask app
app = Flask(__name__)

# Initialize Redis
app.config['REDIS_HOST'] = 'redis'
app.config['REDIS_PORT'] = 6379
redis = FlaskRedis(app)


def create_app():
    app.config.from_object(Config)
    db.init_app(app)
    redis.init_app(app)
    redis.flushall()
    for event_type in ["message_restriction", "purchase_restriction"]:
        redis.set(f"restriction_enabled:{event_type}", "false")
    app.register_blueprint(event_handler.bp)
    app.register_blueprint(access_checker.bp)
    return app  # Add this return statement

app = create_app()
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Welcome to the Whatnot app!"

if __name__ == '__main__':
    # Create tables in database if they do not exist
    app.run(host='0.0.0.0', port=5005)
