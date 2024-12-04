import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)

# Global set to manage peer connections
pcs = set()

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    try:
        params = request.json
        if not params or 'sdp' not in params or 'type' not in params:
            return jsonify({'error': 'Invalid request'}), 400

        # Create peer connection
        offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on('icecandidate')
        def on_icecandidate(event):
            if event.candidate:
                logging.info('New ICE candidate: %s', event.candidate)
            else:
                logging.info('All ICE candidates have been sent.')

        @pc.on('track')
        def on_track(track):
            logging.info('Received track: %s', track.kind)
            if track.kind == 'video':
                logging.info("Handling video track...")
                # Here you can process or forward the video track
            elif track.kind == 'audio':
                logging.info("Handling audio track...")
            else:
                logging.warning("Unsupported track type received.")

        # Set remote description
        await pc.setRemoteDescription(offer)
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        logging.info("Generated SDP answer for the offer.")

        # Prepare response
        response = jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})
        response.headers['Cache-Control'] = 'no-store, must-revalidate'
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    except Exception as e:
        logging.error("Error processing offer: %s", e)
        return jsonify({'error': 'Failed to process offer'}), 500


@app.route('/cleanup', methods=['POST'])
async def cleanup():
    logging.info("Cleaning up peer connections.")
    for pc in pcs:
        await pc.close()
    pcs.clear()
    return jsonify({'status': 'Cleaned up'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Use PORT from environment variable
    app.run(debug=True, host='0.0.0.0', port=port)
