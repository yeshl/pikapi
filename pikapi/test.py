import threading
import asyncio
from time import sleep


async def hi(name, semaphore):
    async with semaphore:
        print('async begin...', name)
        await asyncio.sleep(1)
        1/0
        print('async end...', name)
    return name


def callback(task):
    print('Status:', task.result())


def run(num):
    try:
        1 / 0

    finally:
        print("finally")


if __name__ == '__main__':
    try:
        run(1)
    except Exception as e:
        print(e)
