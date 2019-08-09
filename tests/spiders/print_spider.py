import inspect
import pikapi.spiders.spider_by_req
from pikapi.spiders.spider_by_req import  *

if __name__ == '__main__':
    for name, obj in inspect.getmembers(pikapi.spiders.spider_by_req):
        if inspect.isclass(obj):
            if issubclass(obj,Spider):
                print(obj.name)