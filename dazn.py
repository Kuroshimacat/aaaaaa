# 脚本名称：Dazn解锁检测脚本
# 作者：Telegram @FullTclash
# 日期：2023.2.19

import asyncio
import json

import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger

daznurl = "https://startup.core.indazn.com/misl/v5/Startup"


async def fetch_dazn(Collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    dazn解锁检测
    :param Collector: 采集器
    :param session:
    :param proxy:
    :param reconnection: 重连次数
    :return:
    """
    payload = json.dumps(
        {"LandingPageKey": "generic", "Languages": "zh-CN,zh,en", "Platform": "web", "PlatformAttributes": {},
         "Manufacturer": "", "PromoCode": "", "Version": "2"})
    _headers_json = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36", "Content-Type": 'application/json'}
    try:
        r = await session.post(url=daznurl, proxy=proxy, data=payload, timeout=5, headers=_headers_json)
        if r.status == 200:
            text = await r.json()
            Collector.info['dazn'] = text

    except ClientConnectorError as c:
        logger.warning("dazn请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_dazn(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['dazn'] = "连接错误"
            return
    except asyncio.exceptions.TimeoutError:
        if reconnection != 0:
            logger.warning("dazn请求超时，正在重新发送请求......")
            await fetch_dazn(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['dazn'] = "超时"
            return


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_dazn(Collector, session, proxy=proxy))


# cleaner section
def get_dazn_info(ReCleaner):
    """
    获得dazn解锁信息
    :param ReCleaner:
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'dazn' not in ReCleaner.data:
            logger.warning("采集器内无数据: Dazn")
            return "N/A"
        else:
            i1 = ReCleaner.data.get('dazn', '')
            if i1 == '连接错误' or i1 == '超时':
                logger.info("Dazn状态: " + i1)
                return i1
            try:
                info = ReCleaner.data['dazn']['Region']
                isAllowed = info['isAllowed']
                region = info['GeolocatedCountry']
            except KeyError as k:
                logger.error(str(k))
                return "N/A"
            if not isAllowed:
                logger.info("Dazn状态: " + "失败")
                return "失败"
            elif isAllowed:
                if region:
                    countrycode = region.upper()
                    logger.info("Dazn状态: " + "解锁({})".format(countrycode))
                    return "解锁({})".format(countrycode)
                else:
                    logger.info("Dazn状态: " + "解锁")
                    return "解锁"
            else:
                return "N/A"
    except Exception as e:
        logger.error(str(e))
        return "N/A"


SCRIPT = {
    "MYNAME": "Dazn",
    "TASK": task,
    "GET": get_dazn_info
}

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("Dazn")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
