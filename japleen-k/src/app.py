from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import threading
import time
from pycloudflared import try_cloudflare
import qrcode

app = Flask(__name__)

last_check_in = datetime.now()
CHECKIN_INTERVALS = 1       # In hours

request_logs = []
MAX_LOGS = 50

def log_request(device_id, req_type, status):
    timestamp = datetime.now().strftime("%d%m%y %H%M%S")
    log_entry = {
        "timestamp": timestamp,
        "device": device_id,
        "type": req_type,
        "status": status
    }
    request_logs.insert(0, log_entry)
    if len(request_logs) > MAX_LOGS:
        request_logs.pop()

def send_notification(reason, timestamp, device_id):
    print(f"\n[ALERT NOTIFICATION TRIGGERED]")
    print(f" -> Device ID  : {device_id}")
    print(f" -> Reason     : {reason}")
    print(f" -> Timestamp  : {timestamp}\n")
    log_entry = {
        "timestamp": timestamp,
        "device": device_id,
        "type": "ALERT",
        "status": reason
    }
    request_logs.insert(0, log_entry)

def check_in_monitor():
    global last_check_in

    while True:
        time.sleep(30)
        if datetime.now() - last_check_in > timedelta(hours=CHECKIN_INTERVALS):
            formatted_time = datetime.now().strftime("%d%m%y %H%M%S")
            send_notification(
                reason="MISSED CHECKIN!!",
                timestamp=formatted_time,
                device_id="SERVER NOTIFICATION"
            )

            last_check_in = datetime.now()

@app.route('/')
def dashboard():
    return render_template('index.html', logs=request_logs, last_check_in_iso=last_check_in.isoformat())

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "last_check_in": last_check_in.isoformat()
    }), 200

@app.route('/button', methods=["POST"])
def handle_press():
    global last_check_in
    data = request.json
    button_type = data.get('type')
    device_id = data.get('device', 'Unknown Device')

    timestamp = datetime.now().strftime("%d%m%y %H%M%S")

    if button_type == 'checkin':
        last_check_in = datetime.now()
        log_request(device_id, 'checkin', 'Check-in recorded successfully')
        print(f"[{timestamp}] Check-in received from {device_id}")
        return jsonify({
            "status": "success", 
            "message": "Check-in recorded",
            "last_check_in": last_check_in.isoformat()
        }), 200

    elif button_type == 'emergency':
        log_request(device_id, 'emergency', 'Panic / Emergency button pressed!')
        send_notification(
            reason="Panic / Emergency button pressed!",
            timestamp=timestamp,
            device_id=device_id
        )
        return jsonify({"status": "alert_received", "message": "Emergency logged"}), 200

    return jsonify({"status": "error", "message": "Invalid button type"}), 400


if __name__ == '__main__':
    thread = threading.Thread(target=check_in_monitor, daemon=True)
    thread.start()

    tunnel = try_cloudflare(port=3030)
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(tunnel.tunnel)
    qr.make(fit=True)
    print(f"\n\n{'*' * 50}\nDashboard URL: {tunnel.tunnel}\nAPI Endpoint: {tunnel.tunnel}/button\n\n")
    qr.print_ascii(invert=True)
    print(f"{'*' * 50}\n")

    app.run(host='0.0.0.0', port=3030)