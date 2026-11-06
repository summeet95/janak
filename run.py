import os
import sys
import threading
import time
from dotenv import load_dotenv
from app import create_app

load_dotenv()

is_frozen = getattr(sys, 'frozen', False)
app = create_app('production' if is_frozen else None)


def run_server():
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)


def start_desktop_app():
    import webview

    server = threading.Thread(target=run_server, daemon=True)
    server.start()
    time.sleep(1.5)

    webview.create_window(
        'Inventory App',
        'http://127.0.0.1:5000',
        width=1280,
        height=800,
        min_size=(960, 640)
    )
    webview.start()


if __name__ == '__main__':
    if is_frozen:
        start_desktop_app()
    else:
        app.run(debug=True, use_reloader=False, host='localhost', port=5000)
