免费ip代理采集

#打包源码发布版.tar.gz
python3 setup.py sdist  
# 创建环境venv1
python3 -m venv venv1
执行安装
pip3 install pikapi-2.1.1.tar.gz
运行
python -m pikapi或者 python /tmp/app/venv1/lib64/python3.6/site-packages/pikapi/__main__.py

1.浏览器chrome无法close
2.peewee出现peewee.OperationalError: database is locked
3.代理验证时导致httpserver的tcp连接无法释放
4.在非主线程使用chrome浏览器，异步操作在非主线程使用的问题
5.pyppeteer下载chrome翻墙的问题
6.统一日志配置，多进程日志文件问题