import argparse
import logging
import sys
import pikapi

from pikapi.config import batch_set_config, get_config

CMD_DESCRIPTION = """pikapi command line mode
This command could start a scheduler for crawling and validating proxies.
In addition, a web server with APIs can also be launched.

"""

logger = logging.getLogger(pikapi.__package__)


def main(args) -> int:
    parser = argparse.ArgumentParser(description=CMD_DESCRIPTION,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--no-webserver', '-no-ws', action='store_true',
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
    parser.add_argument('--validation-pool', type=int, default=128,
                        help='The validation pool size (i.e. the limit of concurrent validation tasks for proxies)')

    parsed_args = parser.parse_args(args)
    parsed_args_dict = vars(parsed_args)
    batch_set_config(**vars(parsed_args))
    handle_special_flags(parsed_args_dict)

    from pikapi.database import create_db_tables
    from pikapi.scheduler import Scheduler
    from pikapi.web import start_web_server

    create_db_tables()
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
        print('v{}'.format(pikapi.__version__))
        sys.exit(0)


def app_main():
    sys.exit(main(sys.argv[1:]))
