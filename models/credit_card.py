from . import db
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class CreditCard(db.Model):
    __tablename__ = 'credit_card'
    card_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(
        'user_state.user_id'), nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    last_four_digits = db.Column(db.String, nullable=False)
    total_spend = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


def add_credit_card(user_id, zip_code, total_spend, last_four_digits):
    """
    Adds a credit card to the database if it doesn't already exist for the given user.

    Parameters:
        user_id (str): The ID of the user.
        zip_code (str): The zip code associated with the credit card.
        total_spend (float): The total amount spent using the credit card.
        last_four_digits (str): The last four digits of the credit card number.
    
    Returns:
        CreditCard or None: Returns the CreditCard instance if added successfully, or None if the card already exists.
    """
    # Check if the card with the same last four digits and zip code already exists for the user
    existing_card = CreditCard.query.filter_by(
        user_id=str(user_id),
        zip_code=str(zip_code),
        last_four_digits=str(last_four_digits),
        is_active=True
    ).first()
    log.debug("existing_card", existing_card) 
    if existing_card:
        # Card already exists; do not add it again
        return None

    # Add new card
    new_card = CreditCard(user_id=user_id, zip_code=zip_code,
                          total_spend=total_spend,
                          last_four_digits=last_four_digits)
    db.session.add(new_card)
    log.info(f"User:{user_id} added a credit card with zip code: \
             {zip_code} and last four digits:{last_four_digits}.")
    return new_card

def check_valid_chargeback(user_id, total_chargeback_amount):
    """
    Check if the user has exceeded the chargeback limit.

    Parameters:
        user_id (str): The ID of the user.
        total_chargeback_amount (float): The total chargeback amount for the user.

    Returns:
        bool: True if the user has exceeded the chargeback limit, False otherwise.
    """

    user_cards = CreditCard.query.filter_by(user_id=str(user_id)).all()
    sum_total_spend = sum(card.total_spend for card in user_cards)
    log.debug("sum_total_spend", sum_total_spend)
    if total_chargeback_amount > 0.1 * sum_total_spend:
        return False
    return True
