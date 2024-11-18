import pytest
from services.access_control import check_scam_flags, check_credit_card_zip
from models.user_state import UserState
from models.credit_card import CreditCard
import pytest
from flask import Flask
from models.user_state import db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()  # Clean up after tests


def test_check_scam_flags(app):
    with app.app_context():
        from models.user_state import UserState

        # Add a user to the database
        user = UserState(user_id=123, scam_flags=3, can_message=True)
        db.session.add(user)
        db.session.commit()

        check_scam_flags(user, user.user_id)

        # Assertions
        assert user.can_message is False  # Messaging should be disabled


def test_check_credit_card_zip(app):
    with app.app_context():
        # Add a user and their credit cards to the database
        user = UserState(user_id="456", can_purchase=True)
        db.session.add(user)
        cards = [
            CreditCard(user_id="456", last_four_digits="0001", zip_code="12345"),
            CreditCard(user_id="456", last_four_digits="0002",
                       zip_code="67890"),
            CreditCard(user_id="456", last_four_digits="0003",
                       zip_code="12346"),
        ]
        db.session.add_all(cards)
        db.session.commit()

        check_credit_card_zip(user.user_id)

        # Assertions
        assert user.can_purchase is False  # Purchasing should be disabled
