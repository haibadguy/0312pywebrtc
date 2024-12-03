from flask import Flask, render_template, request, jsonify
from aiortc import RTCPeerConnection, RTCSessionDescription
from urllib.parse import quote as url_quote

app = Flask(__name__)

# Khai báo pcs là một tập hợp chứa các kết nối peer
pcs = set()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    params = request.json
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()
    pcs.add(pc)  # Thêm đối tượng RTCPeerConnection vào pcs

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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
