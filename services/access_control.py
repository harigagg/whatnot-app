from models.user_state import UserState
from models.credit_card import CreditCard, db
from services.tripwire import update_tripwire_count
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def check_scam_flags(user_state, user_id):
    if user_state.scam_flags >= 2:
        user_state.can_message = False
        update_tripwire_count("can_message", user_id)


def check_credit_card_zip(user_id):
    log.debug("user_id", user_id)
    log.debug("Session open:", db.session.is_active)
    cards = db.session.query(CreditCard).filter_by(user_id=str(user_id)).all()
    unique_zips = len(set(card.zip_code for card in cards))
    log.debug("unique_zips", unique_zips)
    log.debug("len(cards)", len(cards))
    if unique_zips / max(1, len(cards)) > 0.75 and len(cards) >= 3:
        log.info(f"User:{user_id} restricted from purchasing due to credit card fraud.")
        user_state = UserState.query.get(user_id)
        user_state.can_purchase = False
        update_tripwire_count("can_purchase", user_id)
