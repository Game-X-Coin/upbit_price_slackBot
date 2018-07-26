import urllib.request, json
import time
import datetime
import schedule
import os

from env import UPBIT_URL
from urllib.request import Request, urlopen
from slackclient import SlackClient

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL']
slack_client = SlackClient(slack_bot_token)

print(slack_bot_token, slack_channel)

def get_message_attachment(symbol, name):
	REQUEST_URL = UPBIT_URL + '/days/?code=CRIX.UPBIT.KRW-' + symbol + '&count=10'

	response = Request(REQUEST_URL, headers={'User-Agent': 'Mozilla/5.0'})
	data = json.loads(urlopen(response).read())

	yesterday = data[1]
	
	high_price = yesterday.get('highPrice')
	low_price = yesterday.get('lowPrice')
	price = yesterday.get('tradePrice')
	time = yesterday.get('timestamp') / 1000
	change_status = yesterday.get('change')
	change_rate = round(yesterday.get('changeRate') * 100, 1)

	change = '변화 없음'
	state = '#2b2b2b'

	if change_status == 'RISE':
		change = str(change_rate) + '% 상승'
		state = '#ff3434'
	elif change_status == 'FALL':
		change = str(change_rate) + '% 하락'
		state = '#115dcb'

	high_price_field = {
		'title': '고가',
		'value': '%.1f 원' % ( high_price ),
		'short': True,
	}

	low_price_field = {
		'title': '저가',
		'value': '%.1f 원' % ( low_price, ),
		'short': True,
	}

	average_price_field = {
		'title': '평균가',
		'value': '%.1f 원' % ( (high_price + low_price) / 2 ),
	}

	attachment = {
		'title': name,
		'title_link': 'https://upbit.com/exchange?code=CRIX.UPBIT.KRW-' + symbol,
		'text': '1%s 당 %.1f 원 (전일대비 %s)' % (symbol, price, change ),
		'thumb_url': 'https://static.upbit.com/logos/' + symbol + '.png',
		'fallback': symbol + '가격 보기 (평균가/고가/시가)',
		'ts': time,
		'color': state,
		'footer': 'Upbit API',
		'fields': [high_price_field, low_price_field, average_price_field]
	}

	return attachment

def send_price_message():
	ETH = get_message_attachment('ETH', '이더리움')
	# EOS = get_message_attachment('EOS', '이오스')

	print(ETH)

	# Sends the response back to the channel
	slack_client.api_call(
		"chat.postMessage",
		channel=slack_channel,
		attachments=[ETH]
	)

send_price_message()
schedule.every().day.at("10:00").do(send_price_message)

while True:
	schedule.run_pending()
	time.sleep(1)
