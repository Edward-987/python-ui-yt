"""
YouTube 视频下载与音频提取工具

描述：
    一个基于 yt-dlp 和 FFmpeg 的图形化工具，用于下载 YouTube 视频和提取音频。

作者: 王海
创建日期: 2025-07-29
版本: 1.0.0

版权 (c) 2025 王海. 保留所有权利。

本软件根据 MIT 许可证发布。

依赖:
    - Python 3.x
    - yt-dlp
    - FFmpeg
    - tkinter

注意：请确保 yt-dlp.exe 和 ffmpeg.exe 与程序位于同一目录下。
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 检查yt-dlp.exe和ffmpeg.exe是否存在
EXE_DIR = os.path.abspath(os.path.dirname(__file__))
YTDLP_PATH = os.path.join(EXE_DIR, 'yt-dlp.exe')
FFMPEG_PATH = os.path.join(EXE_DIR, 'ffmpeg.exe')

if not os.path.exists(YTDLP_PATH) or not os.path.exists(FFMPEG_PATH):
    tk.Tk().withdraw()
    messagebox.showerror('错误', '请将yt-dlp.exe和ffmpeg.exe放在本程序同一目录下！')
    exit(1)

# GUI主程序
class YTDLPGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('YouTube 视频下载与音频提取工具')
        self.geometry('500x320')
        self.resizable(False, False)
        self.current_mp3_path = None  # 当前实际mp3文件路径
        self.create_widgets()

    def create_widgets(self):
        # 视频链接输入
        tk.Label(self, text='YouTube视频链接:').place(x=20, y=30)
        self.url_entry = tk.Entry(self, width=50)
        self.url_entry.place(x=140, y=30)

        # 保存目录选择
        tk.Label(self, text='保存目录:').place(x=20, y=70)
        self.save_dir_var = tk.StringVar()
        self.save_dir_entry = tk.Entry(self, textvariable=self.save_dir_var, width=38)
        self.save_dir_entry.place(x=140, y=70)
        tk.Button(self, text='选择', command=self.choose_dir).place(x=420, y=66)

        # 文件名输入
        tk.Label(self, text='文件名:').place(x=20, y=100)
        self.filename_var = tk.StringVar()
        self.filename_entry = tk.Entry(self, textvariable=self.filename_var, width=28)
        self.filename_entry.place(x=140, y=100)
        self.rename_btn = tk.Button(self, text='重命名', command=self.rename_file)
        self.rename_btn.place(x=380, y=96)

        # 音质选择
        tk.Label(self, text='MP3音质:').place(x=20, y=140)
        self.quality_var = tk.StringVar(value='192')
        self.quality_combo = ttk.Combobox(self, textvariable=self.quality_var, values=['128', '192', '256', '320'], width=10, state='readonly')
        self.quality_combo.place(x=140, y=140)
        tk.Label(self, text='kbps').place(x=220, y=140)

        # 下载按钮
        self.download_btn = tk.Button(self, text='下载并提取MP3', command=self.start_download)
        self.download_btn.place(x=180, y=190)

        # 进度显示
        self.progress = tk.StringVar(value='')
        self.progress_label = tk.Label(self, textvariable=self.progress, fg='blue')
        self.progress_label.place(x=20, y=210)

        # 日志输出
        self.log_text = tk.Text(self, height=5, width=60, state='disabled')
        self.log_text.place(x=20, y=240)

    def choose_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)

    def start_download(self):
        url = self.url_entry.get().strip()
        save_dir = self.save_dir_var.get().strip()
        quality = self.quality_var.get()
        filename = self.filename_var.get().strip()
        if not url:
            messagebox.showwarning('提示', '请填写YouTube视频链接！')
            return
        if not save_dir:
            messagebox.showwarning('提示', '请选择保存目录！')
            return
        self.download_btn.config(state=tk.DISABLED)
        self.progress.set('开始下载...')
        self.log('开始下载...')
        threading.Thread(target=self.download_and_extract, args=(url, save_dir, quality, filename), daemon=True).start()

    def download_and_extract(self, url, save_dir, quality, filename):
        try:
            # 直接用yt-dlp下载并转换为MP3，只下载单个视频
            self.progress.set('正在下载并提取MP3...')
            self.log('正在调用yt-dlp下载并提取MP3...')
            mp3_template = os.path.join(save_dir, '%(title)s_%(id)s.%(ext)s')
            cmd = [YTDLP_PATH, url,
                   '-x', '--audio-format', 'mp3',
                   '--audio-quality', quality+'K',
                   '--no-playlist',
                   '-o', mp3_template]
            # 指定ffmpeg路径
            cmd += ['--ffmpeg-location', FFMPEG_PATH]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log(result.stdout)
            if result.returncode != 0:
                self.progress.set('下载或提取MP3失败！')
                self.download_btn.config(state=tk.NORMAL)
                return
            # 查找最新的mp3文件
            mp3_file = self.find_latest_mp3(save_dir)
            if not mp3_file:
                self.progress.set('未找到生成的MP3文件！')
                self.download_btn.config(state=tk.NORMAL)
                return
            # 下载完成后自动填入文件名文本框（不带扩展名）
            base_dir, old_name = os.path.split(mp3_file)
            name_wo_ext, ext = os.path.splitext(old_name)
            self.filename_var.set(name_wo_ext)
            self.current_mp3_path = mp3_file  # 保存当前实际mp3路径
            # 优先用用户自定义文件名重命名
            if filename:
                safe_filename = filename.replace('/', '_').replace('\\', '_').replace(' ', '_')
                new_name = safe_filename + ext
                new_path = os.path.join(base_dir, new_name)
                try:
                    os.rename(mp3_file, new_path)
                    mp3_file = new_path
                    self.current_mp3_path = mp3_file  # 更新路径
                    self.log(f'文件已重命名为：{mp3_file}')
                except Exception as e:
                    self.log(f'重命名失败：{e}')
            self.progress.set('完成！MP3已保存。')
            self.log(f'完成！MP3文件：{mp3_file}')

        except Exception as e:
            self.progress.set(f'出错：{e}')
            self.log(str(e))
        finally:
            self.download_btn.config(state=tk.NORMAL)

    def find_latest_mp3(self, save_dir):
        # 查找目录下最新的mp3文件
        files = [os.path.join(save_dir, f) for f in os.listdir(save_dir)
                 if f.lower().endswith('.mp3')]
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def rename_file(self):
        """
        按下重命名按钮，将当前mp3文件重命名为文本框中的新名字。
        """
        if not self.current_mp3_path or not os.path.exists(self.current_mp3_path):
            messagebox.showwarning('提示', '没有可重命名的文件！')
            return
        new_name = self.filename_var.get().strip()
        if not new_name:
            messagebox.showwarning('提示', '请输入新的文件名！')
            return
        base_dir, old_name = os.path.split(self.current_mp3_path)
        _, ext = os.path.splitext(old_name)
        safe_new_name = new_name.replace('/', '_').replace('\\', '_').replace(' ', '_') + ext
        new_path = os.path.join(base_dir, safe_new_name)
        if os.path.exists(new_path):
            messagebox.showerror('错误', '目标文件名已存在！')
            return
        try:
            os.rename(self.current_mp3_path, new_path)
            self.current_mp3_path = new_path
            self.log(f'文件已重命名为：{new_path}')
            messagebox.showinfo('成功', f'文件已重命名为：{safe_new_name}')
        except Exception as e:
            self.log(f'重命名失败：{e}')
            messagebox.showerror('错误', f'重命名失败：{e}')

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

if __name__ == '__main__':
    app = YTDLPGUI()
    app.mainloop()
