import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger
from pyrogram.types import InlineKeyboardButton


# collector section
async def fetch_iqiyi(collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    iqiyi解锁测试，先测仅限台湾地区的限定资源，再测港澳台的限定资源
    :param collector:
    :param reconnection:
    :param session:
    :param proxy:
    :return:
    """
    iqiyiurl = "https://www.iq.com/?lang=en_us"
    try:
        async with session.get(iqiyiurl, proxy=proxy, timeout=5) as resq:
            if resq.status == 200:
                texts = await resq.text()
        collector.info['iqiyi'] = texts
    except ClientConnectorError as c:
        logger.warning("iqiyi请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_iqiyi(collector, session=session, proxy=proxy, reconnection=reconnection - 1)
    except asyncio.exceptions.TimeoutError:
        logger.warning("iqiyi请求超时，正在重新发送请求......")
        if reconnection != 0:
            await fetch_iqiyi(collector, session=session, proxy=proxy, reconnection=reconnection - 1)


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_iqiyi(Collector, session, proxy=proxy))


# cleaner section
def get_iqiyi_info(self):
    """
    获取iqiyi解锁信息
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'iqiyi' not in self.data:
            logger.warning("采集器内无数据: iqiyi")
            return "N/A"
        else:
            try:
                info = self.data['iqiyi']
                index = info.find("intlPageInfo.pbInfos = {")
                if index > 0:
                    sinfo = info[index:index + 110]
                    index2 = sinfo.find("mod:", )
                    sinfo2 = sinfo[index2 + 98:]
                    r = sinfo2.split('"')
                    region = r[0] if r else "NOT FOUND"
                    if region == "ntw":
                        region = "TW"
                    elif region == "intl":
                        region = "国际"
                    else:
                        region = region.upper()
                    return f"解锁({region})"
                else:
                    return "未知"
            except KeyError:
                logger.warning("无法读取iqiyi解锁信息")
                return "N/A"
    except Exception as e:
        logger.error(e)
        return "N/A"


SCRIPT = {
    "MYNAME": "iqiyi测试",
    "TASK": task,
    "GET": get_iqiyi_info
}

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("iqiyi测试")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
