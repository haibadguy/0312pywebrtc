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

    # Logging ICE candidates
    @pc.on('icecandidate')
    def on_icecandidate(event):
        if event.candidate:
            logging.info('New ICE candidate: %s', event.candidate)

    # Logging media tracks
    @pc.on('track')
    def on_track(track):
        logging.info('Received track: %s', track.kind)
        if track.kind == 'audio' or track.kind == 'video':
            pc.addTrack(track)  # Ensure the track is added back to the peer

    # Set remote description and create answer
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Return SDP answer
    return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Close all peer connections
    logging.info("Shutting down server...")
    for pc in pcs:
        pc.close()
    pcs.clear()
    return jsonify({'status': 'Server shutdown completed.'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
