import pytest
from flask import Flask
from routes.access_checker import bp as access_checker_bp
from models.user_state import db,UserState

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    # In-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    app.register_blueprint(access_checker_bp)

    return app


@pytest.fixture
def client(app):
    with app.app_context():
        # Ensure the app context is active for all operations
        db.create_all()  # Create tables for tests
        yield app.test_client()
        db.drop_all()  # Clean up tables after tests


def test_can_message_missing_user_id(client):
    response = client.get('/canmessage')
    assert response.status_code == 400
    assert response.json == {"error": "User ID is required"}


def test_can_message_invalid_user(client, mocker):
    mocker.patch('models.user_state.UserState.query.get', return_value=None)
    response = client.get('/canmessage', query_string={"user_id": "123"})
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}


def test_can_message_allowed(client, app):
    # Add user to the database
    with app.app_context():
        new_user = UserState(user_id=123, can_message=True, can_purchase=True)
        db.session.add(new_user)
        db.session.commit()

    response = client.get('/canmessage', query_string={"user_id": "123"})
    assert response.status_code == 200
    assert response.json == {"can_message": True}


def test_can_message_restricted(client, app):
    with app.app_context():
        # Add a user to the database with restricted messaging
        new_user = UserState(user_id=123, can_message=False)
        db.session.add(new_user)
        db.session.commit()

    response = client.get('/canmessage', query_string={"user_id": "123"})
    assert response.status_code == 200
    assert response.json == {"can_message": False}


def test_can_message_allowed(client, app):
    with app.app_context():
        # Add a user to the database who can send messages
        new_user = UserState(user_id=123, can_message=True)
        db.session.add(new_user)
        db.session.commit()

    response = client.get('/canmessage', query_string={"user_id": "123"})
    assert response.status_code == 200
    assert response.json == {"can_message": True}


def test_can_purchase_user_not_found(client):
    response = client.get(
        '/canpurchase', query_string={"user_id": "999"})  # Nonexistent user
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}


def test_can_purchase_restricted(client, app):
    with app.app_context():
        # Add a user to the database with restricted purchasing
        new_user = UserState(user_id=456, can_purchase=False)
        db.session.add(new_user)
        db.session.commit()

    response = client.get('/canpurchase', query_string={"user_id": "456"})
    assert response.status_code == 200
    assert response.json == {"can_purchase": False}


def test_can_purchase_allowed(client, app):
    with app.app_context():
        # Add a user to the database who can purchase
        new_user = UserState(user_id=456, can_purchase=True)
        db.session.add(new_user)
        db.session.commit()

    response = client.get('/canpurchase', query_string={"user_id": "456"})
    assert response.status_code == 200
    assert response.json == {"can_purchase": True}

