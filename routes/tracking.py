from flask import Blueprint, request, jsonify

tracking_bp = Blueprint("tracking", __name__)

# Simple in-memory store for now
CHANNEL_TRACKING = {}  # key: channel_id, value: True/False

@tracking_bp.route("/tracking/start", methods=["POST"])
def tracking_start():
    data = request.get_json(force=True) or {}
    channel_id = data.get("channel_id")
    if not channel_id:
        return jsonify({"ok": False, "error": "channel_id required"}), 400

    CHANNEL_TRACKING[channel_id] = True
    return jsonify({"ok": True, "tracking": True, "channel_id": channel_id})


@tracking_bp.route("/tracking/stop", methods=["POST"])
def tracking_stop():
    data = request.get_json(force=True) or {}
    channel_id = data.get("channel_id")
    if not channel_id:
        return jsonify({"ok": False, "error": "channel_id required"}), 400

    CHANNEL_TRACKING[channel_id] = False
    return jsonify({"ok": True, "tracking": False, "channel_id": channel_id})


@tracking_bp.route("/tracking/status/<channel_id>", methods=["GET"])
def tracking_status(channel_id):
    tracking = bool(CHANNEL_TRACKING.get(channel_id, False))
    return jsonify({"ok": True, "tracking": tracking, "channel_id": channel_id})
