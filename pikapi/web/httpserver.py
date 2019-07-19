
from http.server import HTTPStatus, HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from pikapi.database import ProxyIP, ProxyWebSite
from pikapi.loggings import logger
from threading import Thread
from datetime import datetime, timedelta
import json

_valid_proxies_query = ProxyIP.select()\
                      .where(ProxyIP.updated_at > datetime.now() - timedelta(minutes=30)) \
                      .where(ProxyIP.http_weight + ProxyIP.https_weight > 0)\
                      # .where()


def api_v1_proxies():
    ps = _valid_proxies_query.order_by(ProxyIP.https_weight.desc()).limit(50)
    return ps


def api_v1_sumary():
    total_count = ProxyIP.select().count()
    valid_count = _valid_proxies_query.count()
    return total_count, valid_count


def api_v1_stats():
    ws = ProxyWebSite.select().order_by(ProxyWebSite.this_fetch.desc())
    return ws


class ResquestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        # /api?format=json
        params = parse.parse_qs(parse.urlparse(self.path).query)

        if params.get('format') and 'json' == params['format'][0]:
            jtxt = {p.ip: p.port for p in api_v1_proxies()}
            self.wfile.write(json.dumps(jtxt).encode("utf-8"))
        else:
            stat = api_v1_sumary()
            ul = '''<div style='margin-left:20px'><h3> hi:{0}</h3></div>
                    <ul><li><b>{1}</b> proxy ips in total</li>
                    <li><b>{2}</b> of them are valid</li></ul>'''.format(self.client_address, stat[0], stat[1])

            arr = []
            for x in api_v1_stats():
                arr.append('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format(x.site_name,
                                                                                                          x.proxy_count,
                                                                                                          x.last_fetch.strftime(
                                                                                                              "%Y-%m-%d %H:%M:%S") if x.last_fetch else '',
                                                                                                          x.this_fetch.strftime(
                                                                                                              "%Y-%m-%d %H:%M:%S"),
                                                                                                          x.stats))
            sites = ''.join(arr)

            arr.clear()
            for i, p in enumerate(api_v1_proxies()):
                # <td nowrap='nowrap'></td>
                arr.append(
                    "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td>"
                    "<td>{6}</td><td>{7}</td><td nowrap='nowrap'>{8}</td><td>{9}</td><td>{10}</td></tr>".format(
                        i + 1, '%s:%s' % (p.ip, p.port),
                        p.http_pass_proxy_ip, p.https_pass_proxy_ip,
                        p.http_anonymous, p.https_anonymous,
                        p.http_weight, p.https_weight,
                        p.updated_at.strftime("%Y-%m-%d %H:%I:%S"),
                        p.country, p.city
                    ))
            ips = ''.join(arr)

            html = '''<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                                 <title>http/pikapi</title></head>
                <body>{0}
                <table width="800" style="margin-left:20px; border-collapse:collapse; padding-left:10px"  border="1"  cellPadding=3 bordercolor="#BBBBBB">
                <thead bgcolor="#DDDDDD"><tr><th>site</th><th>proxy</th><th>last crawl</th><th>this crawl</th><th>state</th></tr></thead>
                <tbody>{1}
                </tbody></table></br>
                <table width="900" style="margin-left:20px; border-collapse:collapse; padding-left:10px"  border="1"  cellPadding=3 bordercolor="#BBBBBB">
                <thead bgcolor="#DDDDDD"><tr><th>row</th><th>proxy</th>
                  <th>http_pass_ip</th><th>https_pass_ip</th>
                  <th>http_ano</th><th>https_ano</th>
                  <th>http_weight</th><th>https_weight</th>
                  <th>updated_at</th><th>country_name</th><th>city</th></tr></thead>
                <tbody>{2}</tbody></table>
                </body></html>'''.format(ul, sites, ips)
            self.wfile.write(html.encode('utf-8'))
            # self.close_connection()

    def do_POST(self):
        self.do_HEAD()
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        # post_data = urllib.parse.parse_qs(self.data_string)
        print("receiver POST data:", str(self.data_string, "UTF-8"))
        resp_date = r'{"code":0,"msg":2,"test":{"code":2,"msg":"提交成功"},"cost":{"status":1}}'
        self.wfile.write(bytes(resp_date, "utf-8"))
        return


def start_httpd(host='0.0.0.0', port=8899):
    server = HTTPServer((host, port), ResquestHandler)
    server.serve_forever()


def start_web_server(host='0.0.0.0', port=8899):
    th = Thread(target=start_httpd, args=(host, port))
    th.start()
    logger.info("http server start, listen on: %s:%s" % (host, port))
