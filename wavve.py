# 脚本名称：Wavve解锁检测脚本
# 检测地区：韩国（KR）
# 作者：Telegram @FullTclash
# 日期：2023.2.20
# 原项目: https://github.com/lmc999/RegionRestrictionCheck
import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger

wavveurl = "https://apis.wavve.com/fz/streaming?device=pc&partner=pooq&apikey=E5F3E0D30947AA5440556471321BB6D9&credential=none&service=wavve&pooqzone=none&region=kor&drm=pr&targetage=all&contentid=MV_C3001_C300000012559&contenttype=movie&hdr=sdr&videocodec=avc&audiocodec=ac3&issurround=n&format=normal&withinsubtitle=n&action=dash&protocol=dash&quality=auto&deviceModelId=Windows%2010&guid=1a8e9c88-6a3b-11ed-8584-eed06ef80652&lastplayid=none&authtype=cookie&isabr=y&ishevc=n"


async def fetch_wavve(Collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    wavve解锁检测
    :param Collector: 采集器
    :param session:
    :param proxy:
    :param reconnection: 重连次数
    :return:
    """
    try:
        async with session.get(url=wavveurl, proxy=proxy, timeout=5) as r:
            print(r.status)
            if r.status == 200:
                Collector.info['wavve'] = "解锁"
            else:
                Collector.info['wavve'] = "失败"

    except ClientConnectorError as c:
        logger.warning("wavve请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_wavve(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['wavve'] = "连接错误"
            return
    except asyncio.exceptions.TimeoutError:
        if reconnection != 0:
            logger.warning("wavve请求超时，正在重新发送请求......")
            await fetch_wavve(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['wavve'] = "超时"
            return


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_wavve(Collector, session, proxy=proxy))


# cleaner section
def get_wavve_info(ReCleaner):
    """
    获得wavve解锁信息
    :param ReCleaner:
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'wavve' not in ReCleaner.data:
            logger.warning("采集器内无数据: wavve")
            return "N/A"
        else:
            return ReCleaner.data.get('wavve', "N/A")
    except Exception as e:
        logger.error(str(e))
        return "N/A"


SCRIPT = {
    "MYNAME": "Wavve",
    "TASK": task,
    "GET": get_wavve_info
}

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    os.chdir(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("Wavve")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
