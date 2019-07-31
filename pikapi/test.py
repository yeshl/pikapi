from pyquery import PyQuery

if __name__ == '__main__':
    with open(r'C:\Users\Administrator\Desktop\a.html', 'r') as f:
        txt = f.read()
        doc = PyQuery(txt)
        trs = doc("div.table-container > table:nth-child(1) > tbody:nth-child(3) > tr")
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            print(ip, port)
