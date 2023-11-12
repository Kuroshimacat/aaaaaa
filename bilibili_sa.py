import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger


# collector section
async def fetch_bilibili_sa(collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    bilibili解锁测试，先测仅限台湾地区的限定资源，再测港澳台的限定资源
    :param collector:
    :param reconnection:
    :param session:
    :param proxy:
    :return:
    """
    _headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/102.0.5005.63 Safari/537.36',
        'Accept-Language': 'en',
    }
    bilibili_sa_url1 = "https://www.bilibili.tv"
    bilibili_sa_url2 = "https://www.bilibili.tv/en/live"
    try:
        async with session.get(bilibili_sa_url1, headers=_headers, proxy=proxy, timeout=5) as resq:
            if resq.status != 200:
                collector.info['bilibilisa'] = "N/A"
                return
            texts1 = await resq.text()
        async with session.get(bilibili_sa_url2, headers=_headers, proxy=proxy, timeout=5) as resq2:
            if resq2.status != 200:
                collector.info['bilibilisa'] = "N/A"
                return
            texts2 = await resq2.text()
        if texts1:
            if texts2:
                collector.info['bilibilisa'] = "直播串流解锁"
            else:
                collector.info['bilibilisa'] = "视频串流解锁"
        else:
            collector.info['bilibilisa'] = "失败"
    except ClientConnectorError as c:
        logger.warning("bilibili东南亚请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_bilibili_sa(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['bilibilisa'] = "连接错误"
    except asyncio.exceptions.TimeoutError:
        logger.warning("bilibili东南亚超时，正在重新发送请求......")
        if reconnection != 0:
            await fetch_bilibili_sa(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
        else:
            collector.info['bilibilisa'] = "超时"


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_bilibili_sa(Collector, session, proxy=proxy))


# cleaner section
def get_bilibilisa_info(self):
    """

        :return: str: 解锁信息: [解锁(台湾)、解锁(港澳台)、失败、N/A]
        """
    try:
        if 'bilibilisa' not in self.data:
            logger.warning("采集器内无数据: bilibili东南亚")
            return "N/A"
        else:
            try:
                info = self.data['bilibilisa']
                if info is None:
                    logger.warning("无法读取bilibili东南亚解锁信息")
                    return "N/A"
                else:
                    logger.info("bilibili东南亚情况: " + info)
                    return info
            except KeyError:
                logger.warning("无法读取bilibili东南亚解锁信息")
                return "N/A"
    except Exception as e:
        logger.error(e)
        return "N/A"


SCRIPT = {
    "MYNAME": "Bilibili东南亚",
    "TASK": task,
    "GET": get_bilibilisa_info
}

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("Bilibili东南亚")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
