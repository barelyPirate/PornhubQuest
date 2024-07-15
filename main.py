# barelyPirate

import subprocess
import json
import sys
import os
import stat
from ftplib import FTP
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import threading
import time
import queue

class YtDlp:

    def __init__(self, SaveDirectory: str, FtpDetails: dict):
        self.__CurrentDirectory = os.getcwd().replace("\\", "/")
        self.__SaveDirectory = SaveDirectory
        self.__FtpDetails = FtpDetails

    def dump(self, link: str) -> dict:
        Type = ".exe" if sys.platform == "win32" else ""
        Result = subprocess.getoutput(f"{self.__CurrentDirectory}/yt-dlp/yt-dlp{Type} --dump-json {link}")
        
        if not Result.startswith("ERROR"):
            return json.loads(Result)
        return None

    def download_and_upload(self, link: str, sort_by_uploader: bool, quality: str):
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
            self.upload_to_ftp(file_path, Filename)
        return ExitCode

    def upload_to_ftp(self, file_path, filename):
        try:
            with FTP(self.__FtpDetails['host']) as ftp:
                ftp.login(self.__FtpDetails['user'], self.__FtpDetails['passwd'])
                ftp.cwd(self.__FtpDetails['dir'])
                with open(file_path, 'rb') as file:
                    ftp.storbinary(f'STOR {filename}', file)
            print(f"Successfully uploaded {filename} to FTP server.")
        except Exception as e:
            print(f"Failed to upload {filename} to FTP server. Error: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

app = Flask(__name__)
link_queue = queue.Queue()
downloader = YtDlp("./Download", {
    'host': 'FTP_host, #Whatever host your FTP is connected to
    'user': 'FTP_username',
    'passwd': 'FTP_password',
    'dir': './path/to/storage'
})

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
            downloader.download_and_upload(link, sort_by_uploader=False, quality="720") #Quality really doesnt matter in this code, it'll download the highest quality available
            link_queue.task_done()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=process_queue, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
