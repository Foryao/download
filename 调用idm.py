import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import re
import os
import subprocess
import datetime

def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    image_links = []
    video_links = []

    # 提取图片链接
    image_formats = ('.jpg', '.jpeg', '.png', '.gif')
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not re.search(r'loading', src) and src.endswith(image_formats):
            image_links.append(src)

    # 提取视频链接
    video_formats = ('.mp4', '.avi', '.mov', '.wmv')
    for source in soup.find_all('source'):
        src = source.get('src')
        if src and not re.search(r'loading', src) and src.endswith(video_formats):
            video_links.append(src)

    # 获取网页标题
    title = soup.title.string.strip()

    return image_links, video_links, title

def create_download_command(url, local_path, filename):
    return f'idman /d "{url}" /p "{local_path}" /f "{filename}" /n /a /q'  # 添加 /q 参数

def clean_folder_name(name):
    # 移除非法字符并替换为空格
    return re.sub(r'[\\/:"*?<>|]', '', name).strip()

def download_images_and_videos(url, download_directory):
    image_links, video_links, title = extract_links(url)

    # 创建文件夹并下载图片和视频
    folder_name = clean_folder_name(title)
    folder_path = os.path.join(download_directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    downloaded_links = []

    # 调用 IDM 下载图片
    for idx, image_link in enumerate(image_links):
        image_filename = f"image_{idx + 1}.jpg"  # 可以根据需要修改命名规则
        if not image_link.startswith("http"):
            image_link = "https:" + image_link    #发现无法成功添加任务，修改此处
        download_command = create_download_command(image_link, folder_path, image_filename)
        subprocess.run(download_command, shell=True)
        downloaded_links.append(image_link)

    # 调用 IDM 下载视频
    for idx, video_link in enumerate(video_links):
        video_filename = f"video_{idx + 1}.mp4"  # 可以根据需要修改命名规则
        if not video_link.startswith("http"):
            video_link = "https://" + video_link    #发现无法成功添加任务，修改此处
        download_command = create_download_command(video_link, folder_path, video_filename)
        subprocess.run(download_command, shell=True)
        downloaded_links.append(video_link)

    return downloaded_links, folder_path

def browse_button():
    filename = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def download_button():
    urls = url_entry.get("1.0", "end").split('\n')  # 将多个链接按行分割成列表
    download_directory = entry.get()
    all_links = []
    all_folders = []
    for url in urls:
        url = url.strip()  # 去除链接首尾的空白字符
        if url:  # 检查链接是否为空
            links, folder = download_images_and_videos(url, download_directory)
            all_links.extend(links)
            all_folders.append(folder)
    output_links(all_links)
    messagebox.showinfo("下载完成", f"文件已保存在以下文件夹中:\n\n{', '.join(all_folders)}")

def output_links(links):
    links_window = tk.Toplevel()
    links_window.title("下载链接")

    scrollbar = tk.Scrollbar(links_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text = tk.Text(links_window, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text.pack(expand=True, fill=tk.BOTH)

    for link in links:
        text.insert(tk.END, link + "\n")

    scrollbar.config(command=text.yview)

    # 记录链接到日志文件
    log_links(links)

def log_links(links):
    log_filename = "download_links.log"
    with open(log_filename, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Timestamp: {timestamp}\n")
        for link in links:
            f.write(f"{link}\n")
        f.write("\n")

# 创建主窗口
root = tk.Tk()
root.title("网页图片和视频下载器")

# 创建标签和输入框
url_label = tk.Label(root, text="网页链接:")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

url_entry = tk.Text(root, width=50, height=4)
url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

directory_label = tk.Label(root, text="下载目录:")
directory_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

entry = tk.Entry(root, width=40)
entry.grid(row=1, column=1, padx=5, pady=5)

browse_button = tk.Button(root, text="浏览", command=browse_button)
browse_button.grid(row=1, column=2, padx=5, pady=5)

# 创建下载按钮
download_button = tk.Button(root, text="下载", command=download_button)
download_button.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

root.mainloop()
