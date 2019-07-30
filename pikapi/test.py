import os

import pyppeteer.chromium_downloader

if __name__ == '__main__':
    os.environ.setdefault('PYPPETEER_DOWNLOAD_HOST','https://npm.taobao.org/mirrors')
    abc=os.environ.get('PYPPETEER_DOWNLOAD_HOST','---')
    print(abc)