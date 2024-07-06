import base64
import hashlib
import hmac
import time
import urllib.parse

import requests

import json
from telegram import Bot
from chanlun.cl_interface import *
from chanlun.db import db
from chanlun import config


async def send_telegram_message(market, title, contents: Union[str, list]):
    """发送Telegram消息"""
    # 创建Telegram Bot实例
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    msg_contents = ''
    if  isinstance(contents, str):
        msg_contents = contents
    else:
        for c in contents:
            msg_contents += c
    await bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=title + msg_contents)

async def send_telegram_photo(photo_path: str, caption: str = ''):
    """发送Telegram照片"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    with open(photo_path, 'rb') as photo:
        await bot.send_photo(chat_id=config.TELEGRAM_CHAT_ID, photo=photo, caption=caption)

def config_get_proxy():
    db_proxy = db.cache_get("req_proxy")
    if db_proxy is not None and db_proxy["host"] != "" and db_proxy["port"] != "":
        return db_proxy
    return {
        "host": config.PROXY_HOST,
        "port": config.PROXY_PORT,
    }

def config_get_dingding_keys(market):
    db_dd_key = db.cache_get("dd_keys")
    if db_dd_key is not None and db_dd_key["token"] != "" and db_dd_key["secret"] != "":
        return db_dd_key
    if market == "a":
        return config.DINGDING_KEY_A
    if market == "a":
        return config.DINGDING_KEY_HK
    if market == "us":
        return config.DINGDING_KEY_US
    if market == "futures":
        return config.DINGDING_KEY_FUTURES
    if market == "currency":
        return config.DINGDING_KEY_CURRENCY

    return None

def send_dd_msg(market: str, msg: Union[str, dict]):
    """
    发送钉钉消息
    https://open.dingtalk.com/document/robots/custom-robot-access

    :param market:
    :param msg: 如果类型是 str 则发送文本消息，dict 发送 markdown 消息 (dict demo {'title': '标题', 'text': 'markdown内容'})
    :return:
    """
    dd_info = config_get_dingding_keys(market)
    if dd_info is None or dd_info["token"] == "" or dd_info["secret"] == "":
        return True

    url = "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s"

    def sign():
        timestamp = str(round(time.time() * 1000))
        secret = dd_info["secret"]
        secret_enc = secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        _sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, _sign

    t, s = sign()
    url = url % (dd_info["token"], t, s)
    if isinstance(msg, str):
        res = requests.post(
            url,
            json={
                "msgtype": "text",
                "text": {"content": msg},
            },
        )
    else:
        res = requests.post(url, json={"msgtype": "markdown", "markdown": msg})

    # print(res.text)
    return True

# 旧版的API接口已经下架，不能新增了，后续使用 飞书的 消息接口
def send_fs_msg(market, title, contents: Union[str, list]):
    """
    发送飞书消息
    """
    fs_key = config_get_feishu_keys(market)
    if (
        fs_key is None
        or fs_key["app_id"] == ""
        or fs_key["app_secret"] == ""
        or fs_key["chat_id"] == ""
    ):
        return True
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(fs_key["app_id"])
        .app_secret(fs_key["app_secret"])
        .log_level(lark.LogLevel.WARNING)
        .build()
    )
    # https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json
    if isinstance(contents, str):
        msg_content = {
            "zh_cn": {
                "title": title,
                "content": [[{"tag": "text", "text": f"{contents} \n"}]],
            }
        }
    else:
        msg_content = {
            "zh_cn": {
                "title": title,
                "content": [[]],
            }
        }
        for _c in contents:
            if _c.startswith("img_"):  # 支持图片消息
                msg_content["zh_cn"]["content"][0].append(
                    {"tag": "img", "image_key": f"{_c}"}
                )
            else:
                msg_content["zh_cn"]["content"][0].append(
                    {"tag": "text", "text": f"{_c} \n"}
                )

    msg_content = json.dumps(msg_content, ensure_ascii=False)
    # 构造请求对象
    request: CreateMessageRequest = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(fs_key["chat_id"])
            .msg_type("post")
            .content(msg_content)
            .build()
        )
        .build()
    )

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)
    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
    return True


def send_http_msg(market, title, contents: Union[str, list]):
    msg_contents = ''
    if  isinstance(contents, str):
        msg_contents = contents
    else:
        for c in contents:
            msg_contents += c
    res = requests.get(f'http://10.2.0.11/?msg={msg_contents}')

    return True


if __name__ == "__main__":
    # 示例发送Telegram消息
    async def main():
        # await send_telegram_message('currency', 'test',['test msg', 'test msg1'])
        send_http_msg('currency', 'currency', 'test msg')
    import asyncio
    asyncio.run(main())
