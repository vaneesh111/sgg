from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import json
import os
from datetime import datetime
import re

app = Flask(__name__)
# Заменяем async_mode='asyncio' на async_mode='gevent'
socketio = SocketIO(app, async_mode='gevent', engineio_logger=True, logger=True)

data_dir = "ping_data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_history')
def get_history():
    history = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(data_dir, filename), 'r') as f:
                    file_data = json.load(f)
                    for entry in file_data:
                        if 'timestamp' not in entry:
                            date_match = re.search(r'ping_log_(\d{4}-\d{2}-\d{2})\.json', filename)
                            if date_match:
                                date_str = date_match.group(1)
                                entry['timestamp'] = f"{date_str}T00:00:00"
                    history.extend(file_data)
            except json.JSONDecodeError:
                print(f"Ошибка чтения {filename}: Неверный JSON")
            except Exception as e:
                print(f"Ошибка чтения {filename}: {str(e)}")
    history.sort(key=lambda x: x.get('timestamp', ''))
    return jsonify(history)

# Изменяем обработчик событий для работы с gevent
@socketio.on('ping_data')
def handle_ping(data):
    print(f"Получены данные пинга: {data}")
    data['timestamp'] = datetime.now().isoformat()
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(data_dir, f"ping_log_{date_str}.json")
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []
    existing_data.append(data)
    with open(filename, 'w') as f:
        json.dump(existing_data, f)
    # Используем emit вместо await socketio.emit
    socketio.emit('update_chart', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, debug=True, use_reloader=False)
