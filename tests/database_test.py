import logging
import random
import socket
import struct

from pikapi.database import create_connection, create_db_tables, ProxyIP

# Add logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def gen_random_ip() -> str:
    """
    Generate random ip
    From: https://stackoverflow.com/questions/21014618/python-randomly-generated-ip-address-of-the-string
    """
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


def create_test_ip() -> str:
    ip_str = gen_random_ip()
    ip = ProxyIP(ip=ip_str, port=3306, latency=200.00, stability=100.0, is_valid=True)
    ip.save()
    return ip_str


def delete_test_ip(ip_str: str):
    ProxyIP.delete().where(ProxyIP.ip == ip_str).execute()


def delete_test_ips(ip_strs: [str]):
    for ip in ip_strs:
        delete_test_ip(ip)


def test_create_connection():
    db = create_connection()
    print(db)


def test_create_db_tables():
    create_db_tables()


def test_create_ip():
    ip_str = create_test_ip()

    count = ProxyIP.select().count()
    assert count > 0

    delete_test_ip(ip_str)


def test_delete_ip():
    ret = ProxyIP.delete().execute()
    print(ret)


def test_create_ip_floor_latency():
    ip_str = gen_random_ip()
    ip = ProxyIP(ip=ip_str, port=3306, latency=100.66, stability=100.0, is_valid=True)
    ip.save()

    assert ip.latency == 100.0

    delete_test_ip(ip_str)
