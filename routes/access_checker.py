from flask import Blueprint, jsonify, request
from models.user_state import UserState
from services.tripwire import track_tripwire, is_restriction_active

bp = Blueprint('access_checker', __name__)


@bp.route('/canmessage', methods=['GET'])
def can_message():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_state = UserState.query.get(user_id)
    if not user_state:
        return jsonify({"error": "User not found"}), 404

    # Check if restriction is active and if the user is blocked
    if is_restriction_active("message_restriction") or not user_state.can_message:
        track_tripwire("message_restriction", user_id)
        return jsonify({"can_message": False})

    return jsonify({"can_message": True})


@bp.route('/canpurchase', methods=['GET'])
def can_purchase():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_state = UserState.query.get(user_id)
    if not user_state:
        return jsonify({"error": "User not found"}), 404

    # Check if restriction is active and if the user is blocked
    if is_restriction_active("purchase_restriction") or not user_state.can_purchase:
        track_tripwire("purchase_restriction", user_id)
        return jsonify({"can_purchase": False})

    return jsonify({"can_purchase": True})
