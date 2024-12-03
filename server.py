from flask import Flask, send_file, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription

app = Flask(__name__)

@app.route('/')
def index():
    # Load index.html từ thư mục chính
    return send_file('index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    params = request.json
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()

    @pc.on('icecandidate')
    def on_icecandidate(candidate):
        if candidate:
            print('New ICE candidate:', candidate)

    @pc.on('track')
    def on_track(track):
        print('Received track:', track.kind)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
