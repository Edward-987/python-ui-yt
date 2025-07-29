# YouTube 视频下载与音频提取工具

## 功能简介
- 输入YouTube链接，自动下载视频（需yt-dlp.exe）。
- 自动调用ffmpeg.exe提取音频并转换为MP3。
- 可自选音质（128/192/256/320kbps）。
- 操作简单，界面友好。

## 使用方法
1. 将`yt-dlp.exe`和`ffmpeg.exe`放在本程序同一目录下。
2. 安装Python 3.7+。
3. 安装依赖（tkinter，通常Python自带）。
4. 运行`main.py`：
   ```bash
   python main.py
   ```
5. 按界面提示操作。

## 注意事项
- 下载与转换均在本地执行，无需外网API。
- 若遇到权限或文件夹问题，请以管理员身份运行。
-下载资源：https://github.com/BtbN/FFmpeg-Builds/releases
         https://github.com/yt-dlp/yt-dlp/releases