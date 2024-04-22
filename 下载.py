import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import threading
import json

class ResizingText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.bind("<Key>", self.on_key)
        self.bind("<Configure>", self.on_configure)
        self._master = args[0]

    def on_key(self, event=None):
        self.update_size()

    def on_configure(self, event=None):
        self.update_size()

    def update_size(self):
        lines = self.get(1.0, tk.END).count('\n')
        self._master.after(100, self.config(height=lines+1))

class DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Downloader")

        self.url_label = tk.Label(master, text="网页链接:")
        self.url_label.pack()

        self.url_entry = ResizingText(master, width=60, height=1)
        self.url_entry.pack()

        self.path_label = tk.Label(master, text="下载路径:")
        self.path_label.pack()

        self.path_var = tk.StringVar()
        self.path_var.set(os.getcwd())  # 默认下载路径为当前工作目录
        self.path_entry = tk.Entry(master, textvariable=self.path_var, width=60)
        self.path_entry.pack()

        self.path_button = tk.Button(master, text="选择下载路径", command=self.select_download_path)
        self.path_button.pack()

        self.start_button = tk.Button(master, text="开始", command=self.start_download)
        self.start_button.pack()

        self.pause_button = tk.Button(master, text="暂停", command=self.pause_download, state=tk.DISABLED)
        self.pause_button.pack()

        self.progress_bar = Progressbar(master, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack()

        self.cancelled = False
        self.progress_file = "progress.json"

    def select_download_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def get_page(self, url):
        response = requests.get(url)
        return response.content

    def parse_page(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        title = soup.title.string.strip()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.mp4') or href.endswith('.jpg') or href.endswith('.jpeg') or href.endswith('.png'):
                links.append(href)
        return title, links

    def clean_title(self, title):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        return title

    def create_folder(self, title, download_path):
        cleaned_title = self.clean_title(title)
        folder_name = os.path.join(download_path, cleaned_title)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name

    def download_file(self, url, folder_name):
        file_name = os.path.basename(urlparse(url).path)
        file_path = os.path.join(folder_name, file_name)
        response = requests.get(url, stream=True)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        progress = 0
        with open(file_path, 'wb') as file:
            for data in response.iter_content(block_size):
                if self.cancelled:
                    break
                file.write(data)
                progress += len(data)
                self.progress_bar['value'] = (progress / total_size_in_bytes) * 100
                self.progress_bar.update()
        if not self.cancelled:
            print(f"下载完成：{file_name}")
        else:
            os.remove(file_path)
        self.cancelled = False

    def start_download(self):
        self.cancelled = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        urls = self.url_entry.get("1.0", tk.END).split()
        path = self.path_var.get()

        if not urls:
            print("请输入网页链接！")
            return

        if not os.path.exists(path):
            print("下载路径不存在！")
            return

        threading.Thread(target=self.download, args=(urls, path)).start()

    def pause_download(self):
        self.cancelled = True
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def download(self, urls, path):
        progress_data = self.load_progress_data()
        for url in urls:
            page_content = self.get_page(url)
            title, links = self.parse_page(page_content)
            folder_name = self.create_folder(title, path)
            for link in links:
                if link in progress_data:
                    if progress_data[link] == 100:
                        continue
                absolute_url = urljoin(url, link)
                self.download_file(absolute_url, folder_name)
                progress_data[link] = 100
                self.save_progress_data(progress_data)

        self.show_completion_popup()

    def load_progress_data(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_progress_data(self, data):
        with open(self.progress_file, 'w') as f:
            json.dump(data, f)

    def show_completion_popup(self):
        messagebox.showinfo("完成", "下载完成！")

def main():
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
