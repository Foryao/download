import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from ttkthemes import ThemedStyle

def fetch_links(url, base_url, exclude_urls):
    links = set()

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)

            # 排除特定格式的链接
            if any(exclude_url in full_url for exclude_url in exclude_urls):
                print(f"Excluded link: {full_url}")
                continue

            # 如果链接为相对路径，则转换为绝对路径
            if not urlparse(full_url).scheme:
                full_url = urljoin(base_url, full_url)
            
            # 检查链接是否以指定的地址开头
            if full_url.startswith(base_url):
                links.add(full_url)
            else:
                print(f"Ignored link: {full_url}")

    except Exception as e:
        print(f"Error fetching links: {e}")

    return links

def fetch_and_write_links():
    urls = urls_text.get("1.0", "end").splitlines()
    base_url = base_url_entry.get()

    if not urls or not base_url:
        messagebox.showerror("错误", "请输入URL和基本URL。")
        return

    exclude_urls = [
        "https://kemono.su/fantia/user/*/links",
        "https://kemono.su/fantia/user/*?o=*"
    ]

    try:
        output_file = "output_links.txt"
        with open(output_file, "w") as f:
            for url in urls:
                f.write(f"从 {url} 抓取链接:\n")
                links = fetch_links(url, base_url, exclude_urls)
                if len(links) > 0:
                    f.write("以指定的基URL开头的链接:\n")
                    for link in links:
                        f.write(link + "\n")
                else:
                    f.write("未找到以指定的基URL开头的链接。\n")
                f.write("\n")
        messagebox.showinfo("成功", f"链接已写入 {output_file}")
    except Exception as e:
        messagebox.showerror("错误", f"写入文件时出错: {e}")

# 创建主窗口
root = tk.Tk()
root.title("链接抓取器")

# 使用 ttkthemes 库创建主题样式
style = ThemedStyle(root)
style.set_theme("arc")  # 设置主题样式

# 创建输入框和标签
urls_label = ttk.Label(root, text="输入URL（每行一个）:")
urls_label.grid(row=0, column=0, sticky="e")
urls_text = scrolledtext.ScrolledText(root, width=50, height=5)
urls_text.grid(row=0, column=1, padx=5, pady=5)

base_url_label = ttk.Label(root, text="基本URL:")
base_url_label.grid(row=1, column=0, sticky="e")
base_url_entry = ttk.Entry(root, width=50)
base_url_entry.grid(row=1, column=1, padx=5, pady=5)

# 创建按钮
fetch_button = ttk.Button(root, text="抓取链接", command=fetch_and_write_links)
fetch_button.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
