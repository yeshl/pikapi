from datetime import datetime, timedelta

from pikapi.database import ProxyIP


class Squid:
    # HOME = '/etc/squid'
    HOME = '.'
    SQUID_CONF_TPL = HOME + "/squid.conf.backup"
    SQUID_CONF = HOME + "/squid.conf"
    PEER = "cache_peer {} parent {} 0 no-query weighted-round-robin weight={} " \
           "connect-fail-limit=2 allow-miss max-conn=5 name=p{}\n"
    HIDE = ['acl acl_p443 port 443', 'never_direct allow all', 'request_header_access Via deny all',
            'request_header_access X-Forwarded-For deny all',
            'request_header_access From deny all']

    PROXIES = ProxyIP.select() \
        .where(ProxyIP.updated_at > datetime.now() - timedelta(minutes=60)) \
        .where(ProxyIP.http_weight + ProxyIP.https_weight > 0).limit(2000)

    def update_conf(self):
        with open(self.SQUID_CONF_TPL, "r") as f:
            squid_conf = f.readlines()

        for c in self.HIDE:
            squid_conf.append(c + '\n')

        for i, p in enumerate(self.PROXIES):
            if p.http_weight == 0:
                squid_conf.append(self.PEER.format(p.ip, p.port, p.http_weight + p.https_weight, i))
                squid_conf.append('cache_peer_access p{} deny acl_p443\n'.format(i))
            else:
                squid_conf.append(self.PEER.format(p.ip, p.port, p.http_weight + p.https_weight, i))

        with open(self.SQUID_CONF, "w") as f:
            f.writelines(squid_conf)
        # os.system("squid -k reconfigure")
        # subprocess.call([squid, '-k', 'reconfigure'], shell=False)

    def conf(cls):
        print(cls.HOME)


if __name__ == '__main__':
    print(Squid.SQUID_CONF)
