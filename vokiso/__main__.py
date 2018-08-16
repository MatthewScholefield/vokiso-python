import json

from vokiso.audio_manager import AudioManager
from vokiso.connection_manager import DirectConnection
from vokiso.ui_manager import UiManager


def ask_to_connect(conn: DirectConnection):
    input_str = input('Enter ip address to connect to: ')
    if input_str:
        ip, port = input_str.split(':')
        port = int(port)
        conn.connect(ip, port)
        return ip, port
    else:
        print('Waiting for external connection...')
        conn.wait()
        return None, None


def main():
    conn = DirectConnection()
    ip, port = ask_to_connect(conn)
    print('Connected!')

    audio_manager = AudioManager(conn)
    user_pos = (0, 0)

    def handle_position_message(message):
        nonlocal user_pos
        x, y = message['position']
        audio_manager.pos = (x, y)
        user_pos = x, y

    def on_new_pos(pos):
        conn.send(json.dumps({
            'type': 'position',
            'position': list(pos)
        }))

    def process_message(message):
        message = json.loads(message)
        {
            'audio': audio_manager.process_audio_message,
            'position': handle_position_message
        }[message['type']](message)

    conn.start(process_message)
    audio_manager.create_stream()
    ui_manager = UiManager(on_new_pos)
    while True:
        if conn.connected_event.is_set() and conn.sock.status != 'Nominal':
            print(conn.sock.status.pop(0))
            conn.connected_event.clear()
            if not ip and not port:
                print('Waiting for peer to reconnect...')
                conn.wait()
            else:
                print('Reconnecting to {}:{}...'.format(ip, port))
                conn.connect(ip, port)
        audio_manager.update()
        ux, uy = ui_manager.pos
        aud_scale = audio_manager.audio_scale
        audio_manager.sink.listener.position = (ux * aud_scale, 0., uy * aud_scale)
        ui_manager.update()
        ui_manager.render([user_pos])
