from unittest.mock import MagicMock, patch
import pytest
from models.credit_card import add_credit_card, check_valid_chargeback


@pytest.fixture
def mock_db_session():
    with patch('models.credit_card.db.session') as mock_session:
        yield mock_session


@pytest.fixture
def mock_credit_card_model():
    with patch('models.credit_card.CreditCard') as mock_model:
        yield mock_model


def test_add_credit_card_success(mock_db_session, mock_credit_card_model):
    mock_card = MagicMock()
    mock_credit_card_model.query.filter_by.return_value.first.return_value = None
    mock_credit_card_model.return_value = mock_card

    user_id = '12345'
    zip_code = '12345'
    total_spend = 100.0
    last_four_digits = '1234'

    add_credit_card(user_id, zip_code, total_spend, last_four_digits)

    # Assert
    mock_db_session.add.assert_called_once_with(mock_card)
    mock_card.user_id == user_id
    mock_card.zip_code == zip_code
    mock_card.total_spend == total_spend
    mock_card.last_four_digits == last_four_digits


def test_add_credit_card_duplicate(mock_db_session, mock_credit_card_model):
    existing_card = MagicMock()
    mock_credit_card_model.query.filter_by.return_value.first.return_value = existing_card

    user_id = '12345'
    zip_code = '12345'
    total_spend = 100.0
    last_four_digits = '1234'

    add_credit_card(user_id, zip_code, total_spend, last_four_digits)

    # Assert
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_check_valid_chargeback(mock_credit_card_model):
    mock_card1 = MagicMock()
    mock_card1.total_spend = 5000

    mock_card2 = MagicMock()
    mock_card2.total_spend = 3000

    mock_credit_card_model.query.filter_by.return_value.all.return_value = [
        mock_card1, mock_card2]

    user_id = '12345'
    # 10% of (5000 + 3000) = 800, so 700 is under the limit
    total_chargeback_amount = 700

    result = check_valid_chargeback(user_id, total_chargeback_amount)

    # Assert
    assert result is True


def test_check_valid_chargeback_exceeds_limit(mock_credit_card_model):
    # Arrange
    mock_card1 = MagicMock()
    mock_card1.total_spend = 5000

    mock_card2 = MagicMock()
    mock_card2.total_spend = 3000

    mock_credit_card_model.query.filter_by.return_value.all.return_value = [
        mock_card1, mock_card2]

    user_id = '12345'
    # 10% of (5000 + 3000) = 800, so 900 exceeds the limit
    total_chargeback_amount = 900

    result = check_valid_chargeback(user_id, total_chargeback_amount)

    # Assert
    assert result is False


def test_check_valid_chargeback_no_cards(mock_credit_card_model):
    # Arrange
    mock_credit_card_model.query.filter_by.return_value.all.return_value = []

    user_id = '12345'
    total_chargeback_amount = 100

    # Act
    result = check_valid_chargeback(user_id, total_chargeback_amount)

    # Assert
    assert result is False
