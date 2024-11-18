import pytest
from flask import Flask
from routes.event_handler import bp as event_handler_bp
from models.user_state import db, UserState


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    # In-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    app.register_blueprint(event_handler_bp)

    return app


@pytest.fixture
def client(app):
    with app.app_context():
        # Ensure the app context is active for all operations
        db.create_all()  # Create tables for tests
        yield app.test_client()
        db.drop_all()  # Clean up tables after tests

def test_event_flag_scam_message(client, app):
    with app.app_context():
        # Add a user to the database
        new_user = UserState(user_id=789, scam_flags=0, can_message=True)
        db.session.add(new_user)
        db.session.commit()

    response = client.post('/event', json={
        "name": "flag_scam_message",
        "event_properties": {"user_id": "789"}
    })

    assert response.status_code == 200
    assert response.json == {"status": "success"}

    # Verify user state was updated
    with app.app_context():
        user = UserState.query.get(789)
        assert user.scam_flags == 1


def test_event_add_credit_card(client, app):
    with app.app_context():
        # Add a user to the database
        new_user = UserState(user_id=789, can_purchase=True)
        db.session.add(new_user)
        db.session.commit()

    response = client.post('/event', json={
        "name": "add_credit_card",
        "event_properties": {
            "user_id": "789",
            "zip_code": "12345",
            "last_four_digits": "6789",
            "total_spend": 100
        }
    })

    assert response.status_code == 200
    assert response.json == {"status": "success"}
