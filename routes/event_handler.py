from flask import Blueprint, request, jsonify
from services.tripwire import update_tripwire_count, check_tripwire
from services.access_control import check_scam_flags, check_credit_card_zip
from models.user_state import db, UserState
from models.credit_card import add_credit_card, check_valid_chargeback
import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

bp = Blueprint('event_handler', __name__)


@bp.route('/event', methods=['POST'])
def handle_event():
    data = request.json
    print(data)
    event_name = data["name"]
    user_id = data["event_properties"]["user_id"]

    with db.session.begin():
        user_state = UserState.query.get(user_id)
        if not user_state:
            user_state = UserState(user_id=user_id)
            db.session.add(user_state)
        log.debug("user_state", user_state)
        if event_name == "flag_scam_message":
            if user_state.scam_flags is None:
                user_state.scam_flags = 0
            user_state.scam_flags += 1
            check_scam_flags(user_state, user_id)
            if user_state.scam_flags >= 2:
                log.info(f"User:{user_id} restricted from messaging due to scam flags exceeding threshold.")
                # Mark user as restricted from messaging
                user_state.can_message = False
                # Track the restriction
                update_tripwire_count("message_restriction", user_id)

        elif event_name == "add_credit_card":
            zip_code = data["event_properties"]["zip_code"]
            last_four_digits = data["event_properties"]["last_four_digits"]
            total_spend = data["event_properties"]["total_spend"]
            add_credit_card(user_id, zip_code, total_spend, last_four_digits)
            check_credit_card_zip(user_id)
            log.debug("user_state.can_purchase", user_state.can_purchase)
            if user_state.can_purchase is False:
                # Track restriction for purchase
                update_tripwire_count("purchase_restriction", user_id)

        elif event_name == "chargeback":
            user_data = UserState.query.filter_by(user_id=str(user_id)).all()
            sum_total_chargeback = sum(
                data.chargeback_total for data in user_data)
            log.debug("sum_total_chargeback", sum_total_chargeback)
            chargeback_total = sum_total_chargeback + data["event_properties"]["chargebacks"]
            log.debug("chargeback_total", chargeback_total)
            # checks if the user has exceeded the chargeback limit
            valid = check_valid_chargeback(
                user_id, chargeback_total)
            log.debug("validity", valid)
            if valid:
                log.info(f"User:{user_id}s chargeback has been accepted.")
                user_state.chargeback_cnt += 1
                user_state.chargeback_total += data["event_properties"]["chargebacks"]
            else:
                log.info(f"User:{user_id} restricted from purchasing due to chargeback limit exceeding.")
                user_state = UserState.query.get(user_id)
                user_state.can_purchase = False
                update_tripwire_count("can_purchase", user_id)
                update_tripwire_count("purchase_restriction", user_id)
        db.session.commit()

    # Trigger tripwire checks after event handling
    total_user_count = UserState.query.distinct().count()
    log.debug("total_user_count", total_user_count)
    check_tripwire("message_restriction", total_user_count)
    check_tripwire("purchase_restriction", total_user_count)

    return jsonify({"status": "success"})
