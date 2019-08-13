import logging
import subprocess
from datetime import datetime, timedelta

from pikapi.database import ProxyIP

logger = logging.getLogger(__name__)
#logger = logging.getLogger('pikapi.Squid')


class Squid:
    HOME = '/etc/squid'
    # HOME = '.'
    SQUID_CONF_TPL = HOME + "/squid.conf.backup"
    SQUID_CONF = HOME + "/squid.conf"
    PEER = "cache_peer {} parent {} 0 no-query weighted-round-robin weight={} " \
           "connect-fail-limit=2 allow-miss max-conn=5 name=p{}\n"
    HIDE = ['acl acl_p443 port 443', 'never_direct allow all', 'request_header_access Via deny all',
            'request_header_access X-Forwarded-For deny all',
            'request_header_access From deny all']

    def reconfigure(self):
        ps = ProxyIP.select() \
            .where(ProxyIP.updated_at > datetime.now() - timedelta(minutes=60)) \
            .where(ProxyIP.https_anonymous > 0).where(ProxyIP.http_anonymous > 0) \
            .where(ProxyIP.https_weight > 0) \
            .where(ProxyIP.latency < 25) \
            .order_by(ProxyIP.https_weight.desc(), ProxyIP.https_anonymous.desc(),
                      ProxyIP.http_weight.desc(), ProxyIP.http_anonymous.desc(), ProxyIP.latency) \
            .limit(300)
        logger.info('squid reconfigure...')
        with open(self.SQUID_CONF_TPL, "r") as f:
            squid_conf = f.readlines()

        for c in self.HIDE:
            squid_conf.append(c + '\n')
        i = 0
        for i, p in enumerate(ps):
            if p.http_weight == 0:
                squid_conf.append(self.PEER.format(p.ip, p.port, p.http_weight + p.https_weight, i))
                squid_conf.append('cache_peer_access p{} deny acl_p443\n'.format(i))
            else:
                squid_conf.append(self.PEER.format(p.ip, p.port, p.http_weight + p.https_weight, i))
        squid_conf.append('#%s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if i > 20:
            with open(self.SQUID_CONF, "w") as f:
                f.writelines(squid_conf)
            subprocess.call(['squid', '-k', 'reconfigure'], shell=False)
            logger.info('squid reconfigured !!')
        else:
            logger.info('squid reconfigure cancel !!')


if __name__ == '__main__':
    Squid().reconfigure()
