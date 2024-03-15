print('项目地址：https://github.com/EdmundFu-233/Qubic_revenue_calculator')
print('如果你是花钱购买的本程序，那么你被骗了，请申请退款。')
myHashrate = int(input("\n请输入您的算力："))
print("正在获取信息，请稍等")

import requests
import datetime
import locale
import json
from datetime import datetime, timedelta
import pytz
from pycoingecko import CoinGeckoAPI
from currency_converter import CurrencyConverter
from rich.console import Console
from rich.table import Table
locale.setlocale(locale.LC_ALL, '')

rBody = {'userName': 'guest@qubic.li', 'password': 'guest13@Qubic.li', 'twoFactorCode': ''}
rHeaders = {'Accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
r = requests.post('https://api.qubic.li/Auth/Login', data=json.dumps(rBody), headers=rHeaders)
token = r.json()['token']
rHeaders = {'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
r = requests.get('https://api.qubic.li/Score/Get', headers=rHeaders)
networkStat = r.json()

epochNumber = networkStat['scoreStatistics'][0]['epoch']
epoch97Begin = date_time_obj = datetime.strptime('2024-02-21 12:00:00', '%Y-%m-%d %H:%M:%S')
curEpochBegin = epoch97Begin + timedelta(days=7 * (epochNumber - 97))
curEpochEnd = curEpochBegin + timedelta(days=7) - timedelta(seconds=1)
curEpochProgress = (datetime.utcnow() - curEpochBegin) / timedelta(days=7)

netHashrate = networkStat['estimatedIts']
netAvgScores = networkStat['averageScore']
netSolsPerHour = networkStat['solutionsPerHour']

crypto_currency = 'qubic-network'
destination_currency = 'usd'
cg_client = CoinGeckoAPI()
prices = cg_client.get_price(ids=crypto_currency, vs_currencies=destination_currency)
qubicPrice = prices[crypto_currency][destination_currency]
poolReward = 0.85
incomerPerOneITS = poolReward * qubicPrice * 1000000000000 / netHashrate / 7 / 1.06
curSolPrice = 1479289940 * poolReward * curEpochProgress * qubicPrice / (netAvgScores * 1.06)

def convert_utc_to_china(utc_time):
    utc_datetime = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc_timezone = pytz.timezone('UTC')
    china_timezone = pytz.timezone('Asia/Shanghai')
    utc_datetime = utc_timezone.localize(utc_datetime)
    china_datetime = utc_datetime.astimezone(china_timezone)
    return china_datetime.strftime('%Y-%m-%d %H:%M:%S')

def currency_convert_cny(amount_usd):
    convert_rate = CurrencyConverter().convert(1,'USD','CNY')
    cny = amount_usd * convert_rate
    return round(cny,2)

def past_score_info(data,table_name):
    for entry in data["scoreStatistics"]:
        date = entry["daydate"]
        date = datetime.strptime(date, "%m/%d/%Y")
        date = date.strftime("%m月%d日")
        max_score = entry["maxScore"]
        min_score = entry["minScore"]
        avg_score = entry["avgScore"]
        table_name.add_row(date,str(max_score),str(min_score),str(avg_score))

def sol_convert_qus(curSolPrice):
    qus_quantity = curSolPrice / qubicPrice
    return int(qus_quantity)

def day_per_sol_warning(table_name):
    if 24 * myHashrate * netSolsPerHour / netHashrate < 1:
        table_name.add_row('预测获取sol的周期', str(round(1 / (24 * myHashrate * netSolsPerHour / netHashrate),2)) + " 天")
        if 7 < 1 / (24 * myHashrate * netSolsPerHour / netHashrate):
            table_name.add_row("⚠  获得 sol 周期超过 1 纪元，请注意风险⚠","⚠  获得 sol 周期超过 1 纪元，请注意风险⚠")

table_epoch_info = Table(title="⌛ 目前纪元信息⌛")
table_epoch_info.add_column('信息类型', style="cyan")
table_epoch_info.add_column('数值', justify="right", style="green")
table_epoch_info.add_row('目前纪元',str(epochNumber))
table_epoch_info.add_row('目前纪元开始的中国时间',convert_utc_to_china(str(curEpochBegin)))
table_epoch_info.add_row('目前纪元结束的中国时间',convert_utc_to_china(str(curEpochEnd)))
table_epoch_info.add_row('纪元进度','{:.1f}%'.format(100 * curEpochProgress))
Console().print(table_epoch_info)

table_network_info = Table(title="🌐 网络信息🌐")
table_network_info.add_column('信息类型', style="cyan")
table_network_info.add_column('数值', justify="right", style="green")
table_network_info.add_row('估测的网络算力', '{0:,} it/s'.format(netHashrate).replace(',', ' '))
table_network_info.add_row('平均分',  '{:.1f}'.format(netAvgScores))
table_network_info.add_row('sol/每小时',  '{:.1f}'.format(netSolsPerHour))
Console().print(table_network_info)

table_past_score_info = Table(title="📆 往期分数📆")
table_past_score_info.add_column('日期', style="cyan")
table_past_score_info.add_column('最高分', style="green")
table_past_score_info.add_column('最低分', style="green")
table_past_score_info.add_column('平均分', style="green")
past_score_info(networkStat,table_past_score_info)
Console().print(table_past_score_info)

table_revenue_estimate = Table(title="💰 收益预计💰( 85% 收益池)")
table_revenue_estimate.add_column('信息类型', style="cyan")
table_revenue_estimate.add_column('数值', justify="right", style="green")
table_revenue_estimate.add_row('Qubic 价格', '{:.8f}$'.format((qubicPrice)))
table_revenue_estimate.add_row('预测的每 1 it/s 每日的收入', '{:.2f}￥'.format(currency_convert_cny(incomerPerOneITS)))
table_revenue_estimate.add_row('预测的每日收入', '{:.2f}￥'.format(currency_convert_cny((myHashrate * incomerPerOneITS))))
table_revenue_estimate.add_row('预测的每 sol 的收入', '{:.2f}￥'.format(currency_convert_cny(curSolPrice)))
table_revenue_estimate.add_row('预测的每日 sol 数量', '{:.3f}'.format(24 * myHashrate * netSolsPerHour / netHashrate))
table_revenue_estimate.add_row('预测的每 sol 的币量', '{0:,}'.format(sol_convert_qus(curSolPrice)))
day_per_sol_warning(table_revenue_estimate)
Console().print(table_revenue_estimate)

print('↑上方可能有信息被遮盖住，请注意窗口大小↑')
print('项目地址：https://github.com/EdmundFu-233/Qubic_revenue_calculator')
print('如果你是花钱购买的本程序，那么你被骗了，请申请退款。')
input("\n按回车退出")