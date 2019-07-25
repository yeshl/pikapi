from pikapi.providers._66ip_provider import _66ipProvider
from pikapi.providers.mrhinkydink_provider import MrhinkydinkProvider
from .a2u_provider import A2uProvider
from .base_provider import BaseProvider
from .cool_proxy_provider import CoolProxyProvider
from .data5u_provider import Data5uProvider
from .free_proxy_list_provider import FreeProxyListProvider
from .http_proxy_provider import HttpProxyProvider
from .kuaidaili_provider import KuaidailiProvider
from .spys_me_provider import SpyMeProvider
from .spys_one_provider import SpysOneProvider
from .xici_provider import XiciProvider
from .ipaddress_provider import IpaddressProvider

all_providers = [
    A2uProvider,
    CoolProxyProvider,
    #Data5uProvider,
    FreeProxyListProvider,
    HttpProxyProvider,
    KuaidailiProvider,
    SpyMeProvider,
    SpysOneProvider,
    XiciProvider,
    IpaddressProvider,
    MrhinkydinkProvider,
    _66ipProvider
]

# all_providers = [
#     _66ipProvider
# ]

# Provider references:
# https://github.com/franklingu/proxypool/issues/2
