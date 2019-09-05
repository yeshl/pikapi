免费ip代理采集
=======
[![](https://img.shields.io/badge/language-Python-green.svg)](https://github.com/yeshl/pikapil)

    ______                        ______             _
    | ___ \_                      | ___ \           | |
    | |_/ / \__ __   __  _ __   _ | |_/ /___   ___  | |
    |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | |
    | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___
    \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____\
                           __ / /
                          /___ /

##### [介绍文档](https://github.com/yeshl/pikapil/readme.md)
* 支持版本: ![](https://img.shields.io/badge/Python-3.x-blue.svg)

#打包源码发布版.tar.gz
python3 setup.py sdist  
# 创建环境venv1
python3 -m venv venv1
source venv1/bin/activate
执行安装
pip install pikapi-1.3.0.tar.gz -i https://pypi.tuna.tsinghua.edu.cn/simple
chrome依赖包
yum install -y libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 pango.x86_64 atk.x86_64 gtk3.x86_64 psmisc

运行浏览器测试，自动下载chrome
python -m pikapi -bt
运行
python -m pikapi或者 python ./venv1/lib64/python3.6/site-packages/pikapi/__main__.py

后台运行并定时更新squid
nohup python -m pikapi -s >/dev/null 2>&1 &
