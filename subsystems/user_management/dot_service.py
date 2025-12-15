from flask import Blueprint, request, jsonify
import re
import time

dot_bp = Blueprint("dot_service", __name__)

@dot_bp.route("/external/dot/check", methods=["POST"])
def check_license():
    data = request.get_json()
    license_number = data.get("license")

    time.sleep(1.2)

    pattern = r"^[A-Z]{1,2}[0-9]{5,8}$"
    if not re.match(pattern, license_number.upper()):
        return jsonify({
            "status": "invalid",
            "reason": "Invalid license format",
            "source": "DOT"
        }), 400

    if license_number.upper().startswith("A"):
        return jsonify({
            "status": "valid",
            "message": "License confirmed by DOT",
            "source": "DOT"
        }), 200

    return jsonify({
        "status": "invalid",
        "reason": "DOT rejected the license",
        "source": "DOT"
    }), 400
