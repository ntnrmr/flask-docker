import os
import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class TrackingData(db.Model):
    __tablename__ = "tracking_data"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, index=True, nullable=False)
    event_name = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True), default=datetime.datetime.now, nullable=False
    )
    amount = db.Column(db.Float)
    referral = db.Column(db.String)
    url = db.Column(db.String)


class MarketingTouchpointData(db.Model):
    __tablename__ = "marketing_touchpoint_data"
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, index=True, nullable=False)
    channel_name = db.Column(db.String, nullable=False)


def init_db():
    """Initialize the database, creating tables if they don't exist."""
    with app.app_context():
        db.create_all()


@app.route("/touchpoints", methods=["POST"])
def create_touchpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required_fields = ["event_name", "user_id", "channel_name"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    touchpoint = MarketingTouchpointData(
        event_name=data["event_name"],
        user_id=data["user_id"],
        channel_name=data["channel_name"],
    )

    try:
        db.session.add(touchpoint)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return (
        jsonify(
            {
                "id": touchpoint.id,
                "event_name": touchpoint.event_name,
                "user_id": touchpoint.user_id,
                "channel_name": touchpoint.channel_name,
            }
        ),
        201,
    )


@app.route("/touchpoints", methods=["GET"])
def get_touchpoints():
    touchpoints = MarketingTouchpointData.query.all()
    result = [
        {
            "id": touch.id,
            "event_name": touch.event_name,
            "user_id": touch.user_id,
            "channel_name": touch.channel_name,
        }
        for touch in touchpoints
    ]
    return jsonify(result), 200


def populate_dummy_data():
    """Insert initial dummy data if the tables are empty."""
    with app.app_context():
        if TrackingData.query.first() is None:
            dummy_tracking_data = []
            for i in range(10):
                dummy_tracking_data.append(
                    TrackingData(
                        user_id=f"user{i}",
                        event_name="pageview" if i % 2 == 0 else "conversion",
                        timestamp=datetime.datetime.utcnow()
                        - datetime.timedelta(minutes=i * 10),
                        amount=round(10.0 * i, 2),
                        referral=f"referrer{i}",
                        url=f"http://example.com/page{i}",
                    )
                )
            db.session.bulk_save_objects(dummy_tracking_data)
            db.session.commit()

        if MarketingTouchpointData.query.first() is None:
            dummy_marketing_data = []
            channels = ["Facebook", "Google", "LinkedIn"]
            for i in range(10):
                dummy_marketing_data.append(
                    MarketingTouchpointData(
                        event_name="click" if i % 2 == 0 else "impression",
                        user_id=f"user{i}",
                        channel_name=channels[i % len(channels)],
                    )
                )
            db.session.bulk_save_objects(dummy_marketing_data)
            db.session.commit()


if __name__ == "__main__":
    init_db()
    populate_dummy_data()
    app.run(host="0.0.0.0", port=8080)
