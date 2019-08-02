from pikapi.validators.baidu_validator import BaiduValidator
from pikapi.validators.icanhazip_validator import IcanhazipValidator
from .ipify_validator import IpifyValidator
from .sohu_validator import SohuValidator
from .ysl_validator import YslValidator

all_validators = [
    BaiduValidator,
    SohuValidator,
    IpifyValidator,
    # IcanhazipValidator,
    # YslValidator
]
