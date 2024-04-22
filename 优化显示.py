import tkinter as tk
import re

def extract_links():
    # 打开文件
    with open("output_links.txt", "r") as file:
        # 读取文件内容
        lines = file.readlines()

    # 使用正则表达式提取网页链接
    links = []
    for line in lines:
        link = re.search(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
        if link:
            links.append(link.group())

    return links

def display_links():
    # 提取链接
    links = extract_links()

    # 创建一个新的Tkinter窗口
    window = tk.Tk()
    window.title("Links")

    # 创建一个文本框来显示链接
    text_box = tk.Text(window)
    text_box.pack()

    # 在文本框中显示链接
    for link in links:
        text_box.insert(tk.END, link + "\n")

    # 运行Tkinter事件循环
    window.mainloop()

# 调用函数显示链接
display_links()
