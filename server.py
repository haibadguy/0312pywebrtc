import os
from flask import Flask, jsonify, request, send_from_directory
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaStreamTrack
import logging

app = Flask(__name__)

# Tạo một bộ peer connection
pcs = set()

# Tạo logger để theo dõi lỗi
logging.basicConfig(level=logging.INFO)

class VideoStreamTrack(MediaStreamTrack):
    """
    This class handles the video stream.
    You can replace this with real camera capture using OpenCV or another method.
    """
    def __init__(self):
        super().__init__()
        self._track = None  # Có thể thay thế bằng video stream thực tế từ camera

    async def recv(self):
        # Giả sử đây là cách xử lý video frame
        frame = None  # Gọi một phương thức nào đó để lấy frame video
        return frame

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/offer', methods=['POST'])
async def offer():
    params = request.json
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()
    pcs.add(pc)  # Thêm peer connection vào bộ pcs

    @pc.on('icecandidate')
    def on_icecandidate(candidate):
        if candidate:
            logging.info('New ICE candidate: %s', candidate)

    @pc.on('track')
    def on_track(track):
        logging.info('Received track: %s', track.kind)
        if track.kind == 'audio':
            # Chỉ phát âm thanh cho một peer duy nhất, không gửi lại cho cả hai
            pass  # Bạn có thể xử lý âm thanh ở đây
        elif track.kind == 'video':
            # Đảm bảo video được xử lý đúng, ví dụ thêm video track vào peer
            pass

    # Thiết lập remote description (dành cho offer)
    await pc.setRemoteDescription(offer)

    # Tạo answer (response)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Trả về SDP
    return jsonify({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

@app.route('/getIceCandidates', methods=['POST'])
async def get_ice_candidates():
    # Endpoint để lấy ICE candidates (nếu cần thiết)
    candidates = []  # Dữ liệu candidate sẽ được lấy từ ICE server (nếu có)
    return jsonify({'candidates': candidates})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

