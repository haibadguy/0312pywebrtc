import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
CORS(app)  # Cho phép CORS

logging.basicConfig(level=logging.INFO)

# Quản lý các kết nối PeerConnection
pcs = set()

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/offer', methods=['POST'])
def offer():
    try:
        params = request.get_json()
        if not params or 'sdp' not in params or 'type' not in params:
            return jsonify({'error': 'Invalid request'}), 400

        # Tạo PeerConnection
        pc = RTCPeerConnection()
        pcs.add(pc)

        # Lắng nghe sự kiện ICE candidate
        @pc.on('icecandidate')
        def on_icecandidate(event):
            if event.candidate:
                logging.info('New ICE candidate: %s', event.candidate)
            else:
                logging.info('All ICE candidates have been sent.')

        # Xử lý track nhận được
        @pc.on('track')
        def on_track(track):
            logging.info('Received track: %s', track.kind)
            if track.kind == 'video':
                logging.info("Handling video track...")
            elif track.kind == 'audio':
                logging.info("Handling audio track...")
            else:
                logging.warning("Unsupported track type received.")

        # Đặt SDP từ offer và tạo answer
        offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
        pc.setRemoteDescription(offer)

        answer = pc.createAnswer()
        pc.setLocalDescription(answer)

        logging.info("Generated SDP answer for the offer.")

        # Trả về SDP answer
        return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

    except Exception as e:
        logging.error("Error processing offer: %s", e)
        return jsonify({'error': 'Failed to process offer'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    logging.info("Cleaning up peer connections.")
    for pc in pcs:
        pc.close()
    pcs.clear()
    return jsonify({'status': 'Cleaned up'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Sử dụng PORT từ biến môi trường
    app.run(debug=True, host='0.0.0.0', port=port)
