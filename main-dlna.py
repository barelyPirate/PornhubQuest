import subprocess
import json
import sys
import os
import stat
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import threading
import time
import queue
import shutil

source = str(input("Enter the Destination DLNA Folder"))

class YtDlp:

    def __init__(self, SaveDirectory: str, FinalDirectory: str):
        self.__CurrentDirectory = os.getcwd().replace("\\", "/")
        self.__SaveDirectory = SaveDirectory
        self.__FinalDirectory = FinalDirectory

    def dump(self, link: str) -> dict:
        Type = ".exe" if sys.platform == "win32" else ""
        Result = subprocess.getoutput(f"{self.__CurrentDirectory}/yt-dlp/yt-dlp{Type} --dump-json {link}")
        
        if not Result.startswith("ERROR"):
            return json.loads(Result)
        else:
            print("Error: Link not Supported. " + link)
        return None

    def download_and_move(self, link: str, sort_by_uploader: bool, quality: str):
        dump = self.dump(link)
        if dump is None:
            return 1
        
        Filename = dump["filename"]
        Uploader = "/" + dump["uploader"] if sort_by_uploader else ""
        local_save_path = f"{self.__SaveDirectory}{Uploader}"
        os.makedirs(local_save_path, exist_ok=True)
        os.chmod(local_save_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        file_path = f"{local_save_path}/{Filename}"

        ExitCode = os.system(f"{self.__CurrentDirectory}/yt-dlp/yt-dlp -o \"{file_path}\" {link}")
        if ExitCode == 0:
            print("Moving to final directory")
            self.move_to_final_directory(file_path, Filename, Uploader)
            print("Move Done")
        return ExitCode
    
    def move_to_final_directory(self, file_path, filename, uploader):
        try:
            final_save_path = f"{self.__FinalDirectory}{uploader}"
            os.makedirs(final_save_path, exist_ok=True)
            shutil.move(file_path, f"{final_save_path}/{filename}")
            print(f"Successfully moved {filename} to {final_save_path}.")
        except Exception as e:
            print(f"Failed to move {filename} to {self.__FinalDirectory}. Error: {e}")

app = Flask(__name__)
link_queue = queue.Queue()
downloader = YtDlp("./Download", source)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        link_queue.put(link)
        return redirect(url_for('index'))
    return render_template_string('''
        <form method="post">
            Video Link: <input type="text" name="link">
            <input type="submit" value="Add to Queue">
        </form>
        <a href="{{ url_for('show_queue') }}">View Queue</a>
    ''')

@app.route('/queue', methods=['GET'])
def show_queue():
    return jsonify(list(link_queue.queue))

def process_queue():
    while True:
        if not link_queue.empty():
            link = link_queue.get()
            downloader.download_and_move(link, sort_by_uploader=False, quality="720")
            link_queue.task_done()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=process_queue, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
