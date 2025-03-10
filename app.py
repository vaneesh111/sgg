from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('ping_data')
def handle_ping(data):
    socketio.emit('update_chart', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=443, debug=True)
