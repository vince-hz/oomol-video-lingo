import os
import sys

if not sys.version.startswith("3.10"):
    print("Python 版本不正确. 请使用 Python 3.10.")
    exit(1)


downloaded = os.path.exists("VideoLingo") & os.path.isdir("VideoLingo")

if downloaded:
    print("VideoLingo 文件夹已存在.")
else:
    print("VideoLingo 文件夹不存在. 开始下载.")
    os.system("git clone https://github.com/vince-hz/VideoLingo.git")
    print("VideoLingo 文件夹已下载.")