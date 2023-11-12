import asyncio
import aiohttp
from aiohttp import ClientConnectorError
from loguru import logger
from pyrogram.types import InlineKeyboardButton


async def fetch_pjsk(Collector, session: aiohttp.ClientSession, proxy=None, reconnection=2):
    """
    Project Sekai封锁检测
    :param Collector: 采集器
    :param session:
    :param proxy:
    :param reconnection: 重连次数
    :return:
    """
    pjskurl1 = "https://game-version.sekai.colorfulpalette.org"  # pjskurl
    try:
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/102.0.5005.63 Safari/537.36',
        }
        async with session.get(pjskurl1, headers=_headers, proxy=proxy, timeout=10) as res:
            if res.status == 403:
                text = await res.text()
                index = text.find("AccessDenied")
                if index > 0:
                    Collector.info['Project Sekai'] = "解锁"
                else:
                    Collector.info['Project Sekai'] = "失败"
            else:
                Collector.info['Project Sekai'] = "失败"

    except ClientConnectorError as c:
        logger.warning("Project Sekai请求发生错误:" + str(c))
        if reconnection != 0:
            await fetch_pjsk(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['Project Sekai'] = "连接错误"
            return
    except asyncio.exceptions.TimeoutError:
        if reconnection != 0:
            logger.warning("Project Sekai请求超时，正在重新发送请求......")
            await fetch_pjsk(Collector, session, proxy=proxy, reconnection=reconnection - 1)
        else:
            Collector.info['Project Sekai'] = "超时"
            return


def task(Collector, session, proxy):
    return asyncio.create_task(fetch_pjsk(Collector, session, proxy=proxy))


# cleaner section
def get_pjsk_info(ReCleaner):
    """
    获得Project Sekai解锁信息
    :param ReCleaner:
    :return: str: 解锁信息: [解锁、失败、N/A]
    """
    try:
        if 'Project Sekai' not in ReCleaner.data:
            logger.warning("采集器内无数据")
            return "N/A"
        else:
            # logger.info("Project Sekai解锁：" + str(ReCleaner.data.get('Project Sekai', "N/A")))
            return ReCleaner.data.get('Project Sekai', "N/A")
    except Exception as e:
        logger.error(e)
        return "N/A"

SCRIPT = {
    "MYNAME": "Pjsk JP",
    "TASK": task,
    "GET": get_pjsk_info
}

# bot_setting_board

button = InlineKeyboardButton("✅Pjsk JP", callback_data='✅Pjsk JP')

if __name__ == "__main__":
    "this is a test demo"
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir)))
    from libs.collector import Collector as CL, media_items

    media_items.clear()
    media_items.append("Project Sekai")
    cl = CL()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cl.start(proxy="http://127.0.0.1:1111"))
    print(cl.info)
