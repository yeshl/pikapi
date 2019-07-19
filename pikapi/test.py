import asyncio
from pyppeteer import launch


async def get_html(url):
    # exepath = 'C:/Users/tester02/AppData/Local/Google/Chrome/Application/chrome.exe'
    # browser = await launch({'executablePath': exepath, 'headless': False, 'slowMo': 30})
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    #await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
    await page.goto('http://www.66ip.cn/1.html', options={'timeout': int(8 * 1000)})
    await page.waitForNavigation({'waitUntil': 'load'})#66ip第一次访问会返回521，这里wait即可，或者再调用一次goto也行
    html = await page.content()
    # cookies = await page.cookies()
    # for ck in cookies:
    #     print(ck['name'], ck['value'])
    # eles = await page.xpath('//*[@id="main"]/div/div[1]/table/tbody/tr')
    ips = await parse_by_browser(page)
    await browser.close()
    return ips


async def parse_by_browser(page):
    eles = await page.querySelectorAll('#main > div > div:nth-child(1) > table > tbody > tr')
    ips = []
    for it in eles:
        ip = await (await (await it.querySelector(':nth-child(1)')).getProperty('textContent')).jsonValue()
        port = await (await (await it.querySelector(':nth-child(2)')).getProperty('textContent')).jsonValue()
        ips.append((ip, port))
    return ips


if __name__ == '__main__':
    # url = 'http://www.66ip.cn/1.html'
    # ips = asyncio.get_event_loop().run_until_complete(get_html(url))
    # print(ips)
    urls = ['http://www.66ip.cn/1.html', 'http://www.66ip.cn/2.html']
    tasks = [get_html(url) for url in urls]
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))
    for res in results:
        print(res)

