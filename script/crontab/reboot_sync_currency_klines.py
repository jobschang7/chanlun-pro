#:  -*- coding: utf-8 -*-
from chanlun.exchange.exchange_binance import ExchangeBinance
from chanlun.exchange.exchange_db import ExchangeDB
import traceback
from tqdm.auto import tqdm

"""
同步数字货币行情到数据库中
"""

exchange = ExchangeDB("currency")
line_exchange = ExchangeBinance()

# 创建表
#stocks = line_exchange.all_stocks()
#codes = [s["code"] for s in stocks]
# codes = ['BTC/USDT']
codes = ['ROSE/USDT', 'AAVE/USDT', 'FLOW/USDT', 'XMR/USDT', '1INCH/USDT', 'KLAY/USDT', 
         'XLM/USDT', 'EOS/USDT', 'MANTA/USDT', 'LINK/USDT', 'PYTH/USDT', 'ALT/USDT', 'ZRX/USDT', 
         'FTM/USDT', 'BAND/USDT', 'RNDR/USDT', 'LPT/USDT', 'SSV/USDT', '1000SHIB/USDT', 
         'DOGE/USDT', 'MEME/USDT', 'AI/USDT', 'NEAR/USDT', 'AR/USDT', 'WLD/USDT', 'GMT/USDT', 
         'GALA/USDT', 'IMX/USDT', 'SAND/USDT', 'AXS/USDT', 'XAI/USDT', 'BIGTIME/USDT', 'STRK/USDT', 
         'OP/USDT', 'ARB/USDT', 'MATIC/USDT', 'CELO/USDT', 'LRC/USDT', 'UNI/USDT', 'ENA/USDT', 'KAVA/USDT', 
         'SSV/USDT', 'SUI/USDT', 'APT/USDT', 'SEI/USDT', 'DOT/USDT', 'BCH/USDT', 'TNSR/USDT', 'NFP/USDT', 
         'W/USDT', 'JUP/USDT', 'STX/USDT', 'CAKE/USDT', 'ICP/USDT', 'IOTX/USDT', 'GRT/USDT', 'FIL/USDT', 
         'UMA/USDT', 'SUSHI/USDT', 'LTC/USDT', '1000LUNC/USDT', '1000XEC/USDT', 'LDO/USDT', 'PENDLE/USDT', 
         'NOT/USDT', 'ONDO/USDT', 'TRB/USDT', '1000BONK/USDT', 'BOME/USDT', '1000PEPE/USDT', 'WIF/USDT', 
         'PEOPLE/USDT', 'TURBO/USDT', 'MEW/USDT', 'ARKM/USDT', '1000RATS/USDT', '1000SATS/USDT', 'ORDI/USDT', 
         'BNX/USDT', 'ENS/USDT', 'MKR/USDT', 'SOL/USDT', 'JTO/USDT', 'BB/USDT', 'CKB/USDT', '1000FLOKI/USDT', 
         'JASMY/USDT', 'TON/USDT', 'LEVER/USDT', 'BOND/USDT', 'ONG/USDT', 'IO/USDT', 'LISTA/USDT', 'BTC/USDT', 'BNB/USDT', 'ETH/USDT',
         'ZRO/USDT', 'UNFI/USDT', 'ZK/USDT', 'AEVO/USDT', 'MAVIA/USDT', 'TOKEN/USDT', 'BEL/USDT', 'JOE/USDT', 'PHB/USDT']

sync_frequencys = ["w", "d", "4h", "60m", "30m", "15m", "10m", "5m", "1m"]

# TODO 同步各个周期的起始时间
f_start_time_maps = {
    "w": "2000-01-01 00:00:00",
    "d": "2000-01-01 00:00:00",
    "4h": "2000-01-01 00:00:00",
    "60m": "2000-01-01 00:00:00",
    "30m": "2000-01-01 00:00:00",
    "15m": "2000-01-01 00:00:00",
    "10m": "2000-01-01 00:00:00",
    "5m": "2000-01-01 00:00:00",
    "1m": "2000-01-01 00:00:00",
}

if __name__ == "__main__":
    for code in tqdm(codes):
        try:
            for f in sync_frequencys:
                while True:
                    try:
                        last_dt = exchange.query_last_datetime(code, f)
                        if last_dt is None:
                            klines = line_exchange.klines(
                                code,
                                f,
                                end_date=f_start_time_maps[f],
                                args={"use_online": True},
                            )
                            if len(klines) == 0:
                                klines = line_exchange.klines(
                                    code,
                                    f,
                                    start_date=f_start_time_maps[f],
                                    args={"use_online": True},
                                )
                        else:
                            klines = line_exchange.klines(
                                code, f, start_date=last_dt, args={"use_online": True}
                            )

                        tqdm.write(
                            "Run code %s frequency %s klines len %s"
                            % (code, f, len(klines))
                        )
                        exchange.insert_klines(code, f, klines)
                        if len(klines) <= 1:
                            break
                    except Exception as e:
                        tqdm.write("执行 %s 同步K线异常" % code)
                        tqdm.write(traceback.format_exc())
                        break

        except Exception as e:
            tqdm.write("执行 %s 同步K线异常" % code)
            tqdm.write(e)
            tqdm.write(traceback.format_exc())
