from pikapi.validators.icanhazip_validator import IcanhazipValidator
from .ipify_validator import IpifyValidator
from .sohu_validator import SohuValidator

all_validators = [
    IpifyValidator,
    IcanhazipValidator,
    SohuValidator
]
