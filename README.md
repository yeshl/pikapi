免费ip代理采集
=======
[![Build Status](https://travis-ci.org/jhao104/proxy_pool.svg?branch=master)](https://travis-ci.org/pikapi/pikapi)
[![](https://img.shields.io/badge/Powered%20by-@yeshl-green.svg)](https://blog.csdn.net/anacan)
[![Requirements Status](https://requires.io/github/jhao104/proxy_pool/requirements.svg?branch=master)](https://requires.io/github/pikapi/proxy_pool/requirements/?branch=master)
[![Packagist](https://img.shields.io/packagist/l/doctrine/orm.svg)](https://github.com/jhao104/proxy_pool/blob/master/LICENSE)
[![GitHub contributors](https://img.shields.io/github/contributors/jhao104/proxy_pool.svg)](https://github.com/yeshl/pikapi/graphs/contributors)
[![](https://img.shields.io/badge/language-Python-green.svg)](https://github.com/yeshl/pikapil)

    ______                        ______             _
    | ___ \_                      | ___ \           | |
    | |_/ / \__ __   __  _ __   _ | |_/ /___   ___  | |
    |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | |
    | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___
    \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____\
                           __ / /
                          /___ /

##### [介绍文档](https://github.com/jhao104/proxy_pool/blob/master/doc/introduce.md)

* 支持版本: ![](https://img.shields.io/badge/Python-3.x-blue.svg)

#打包源码发布版.tar.gz
python3 setup.py sdist  
# 创建环境venv1
python3 -m venv venv1
source venv1/bin/activate
执行安装
pip3 install pikapi-1.2.5.tar.gz
chrome依赖包
yum install -y libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 pango.x86_64 atk.x86_64 gtk3.x86_64 psmisc

运行浏览器测试，自动下载chrome
python -m pikapi -bt
运行
python -m pikapi或者 python ./venv1/lib64/python3.6/site-packages/pikapi/__main__.py

后台运行并定时更新squid
nohup python -m pikapi -s >/dev/null 2>&1 &

1.浏览器chrome无法close
2.peewee出现peewee.OperationalError: database is locked
3.代理验证时导致httpserver的tcp连接无法释放
4.在非主线程使用chrome浏览器，异步操作在非主线程使用的问题
5.pyppeteer下载chrome翻墙的问题
6.统一日志配置，多进程日志文件问题