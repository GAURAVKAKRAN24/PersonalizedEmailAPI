from flask import Flask
from flask_cors import CORS
from flask_apscheduler import APScheduler

from routes import register_routes

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
CORS(app)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

register_routes(app, scheduler)

if __name__ == '__main__':
    app.run(debug=True)