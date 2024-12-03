import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global set to manage peer connections
pcs = set()

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    params = request.json
    if not params or 'sdp' not in params or 'type' not in params:
        return jsonify({'error': 'Invalid request'}), 400

    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on('icecandidate')
    def on_icecandidate(event):
        if event.candidate:
            logging.info('New ICE candidate: %s', event.candidate)

    @pc.on('track')
    def on_track(track):
        logging.info('Received track: %s', track.kind)
        if track.kind == 'audio' or track.kind == 'video':
            pc.addTrack(track)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Dùng biến môi trường PORT
    app.run(debug=True, host='0.0.0.0', port=port)
