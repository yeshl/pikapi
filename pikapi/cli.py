import argparse
import asyncio
import logging
import sys

from pyppeteer import launch, chromium_downloader

import pikapi
from pikapi.config import batch_set_config, get_config
import pikapi.store

CMD_DESCRIPTION = """pikapi command line mode
This command could start a scheduler for crawling and validating proxies.
In addition, a web server with APIs can also be launched.

"""

logger = logging.getLogger(pikapi.__package__)


async def get_html(url):
    browser = await launch(headless=True,
                           args=['--no-sandbox'])
    pages = await browser.pages()
    page = pages[0]
    # await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
    logger.info('goto: %s' % url)
    await page.goto(url, options={'timeout': int(10 * 1000)})
    # await page.waitForNavigation({'timeout': 1000 * 30})
    # html = await page.content()
    html = await page.title()
    await page.close()
    logger.info('close chrome now...')
    await browser.close()
    logger.info('chrome closed')
    return html


def main(args) -> int:
    parser = argparse.ArgumentParser(description=CMD_DESCRIPTION,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--browser-test', '-bt', action='store_true',
                        help='test browser for pyppeteer')
    parser.add_argument('--no-webserver', '-nw', action='store_true',
                        help='Prevent starting a web server for JSON API')
    parser.add_argument('--web-port', '-wp', type=int, default=8899,
                        help='The port number for the web server')
    parser.add_argument('--web-host', '-wh', type=str, default='0.0.0.0',
                        help='The hostname for the web server')
    parser.add_argument('--skip-scheduler', action='store_true',
                        help='Prevent the scheduler from crawling')
    parser.add_argument('--version', '-v', action='store_true',
                        help='Print the version of pikapi')
    parser.add_argument('--db-path', type=str, default='./pikapi.db',
                        help='The sqlite database file location')
    parser.add_argument('--no-validate', '-nv', action='store_true',
                        help='Prevent starting validation)')
    parser.add_argument('--squid', '-s', action='store_true',
                        help='reconfigure squid')

    parsed_args = parser.parse_args(args)
    parsed_args_dict = vars(parsed_args)
    batch_set_config(**vars(parsed_args))

    logger.info('chromium version %s', chromium_downloader.REVISION)
    logger.info('local path %s', chromium_downloader.chromiumExecutable)
    logger.info('download url %s', chromium_downloader.downloadURLs)
    handle_special_flags(parsed_args_dict)

    from pikapi.scheduler import Scheduler
    from pikapi.web import start_web_server

    s = Scheduler()

    try:
        if not get_config('skip_scheduler'):
            s.start()
        # web server
        if not get_config('no_webserver'):
            logger.info('Start the web server')
            start_web_server(host=parsed_args_dict['web_host'], port=parsed_args_dict['web_port'])
        s.join()
    except (KeyboardInterrupt, SystemExit):
        logger.info('catch KeyboardInterrupt, exiting...')
        s.stop()
        sys.exit(0)
    return 0


def handle_special_flags(args: dict):
    if args['version']:
        logger.debug('v{}'.format(pikapi.__version__))
        sys.exit(0)
    if args['browser_test']:
        text = asyncio.get_event_loop().run_until_complete(get_html("https://www.baidu.com"))
        logger.info(text)
        sys.exit(0)


def app_main():
    sys.exit(main(sys.argv[1:]))
