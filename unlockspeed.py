import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger


# collector section
async def fetch_speedtest(collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    speedtest解锁测试,检查测速是否被ban
    :param collector:
    :param reconnection:
    :param session:
    :param proxy:
    :return:
    """
    checkurl = "https://www.speedtest.net/"
    try:
        async with session.get(checkurl, proxy=proxy, timeout=5) as resq:
            if resq.status == 200:
                collector.info['speedtest'] = "允许测速"
    except ClientConnectorError as c:
        logger.warning("speedtest请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_speedtest(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['speedtest'] = "禁止测速"
    except asyncio.exceptions.TimeoutError:
        logger.warning("speedtest请求超时，正在重新发送请求......")
        if reconnection != 0:
            await fetch_speedtest(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['speedtest'] = "超时"


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_speedtest(Collector, session, proxy=proxy))


# cleaner section
def get_speedtest_info(ReCleaner):
    """
    获取speedtest解锁信息
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'speedtest' not in ReCleaner.data:
            logger.warning("采集器内无数据")
            return "N/A"
        else:
            logger.info("Speedtest解锁：" + str(ReCleaner.data.get('speedtest', "N/A")))
            return ReCleaner.data.get('speedtest', "N/A")
    except Exception as e:
        logger.error(e)
        return "N/A"


SCRIPT = {
    "MYNAME": "Speedtest",
    "TASK": task,
    "GET": get_speedtest_info
}

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("Speedtest")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
