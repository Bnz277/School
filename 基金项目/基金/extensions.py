from flask_socketio import SocketIO

# 与原逻辑一致：允许跨域
socketio = SocketIO(cors_allowed_origins="*")