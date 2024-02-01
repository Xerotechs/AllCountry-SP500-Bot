import datetime
import json
import requests
import sys
import tweepy

# jsonファイルを読み取る
with open('data.json') as f:
    jsonfile = json.load(f)

# Tweepy
API_Key = jsonfile['API_Key']
API_Key_Secre = jsonfile['API_Key_Secre']
Access_Token = jsonfile['Access_Token']
Access_Token_Secret = jsonfile['Access_Token_Secret']
client = tweepy.Client(consumer_key=API_Key, consumer_secret=API_Key_Secre, access_token=Access_Token, access_token_secret=Access_Token_Secret)

def fundAPI(cd, name):
    # エンドポイントの組み立て
    url_fund = f'https://developer.am.mufg.jp/fund_information_latest/fund_cd/{cd}'
    # 協会コードの場合のリクエスト
    fund_response = requests.get(url_fund, headers = {'Content-Type':'application/json'}).json()

    # 騰落率
    percent = fund_response['datasets'][0]['percentage_change_1m']
    percent = f'{float(percent):.02f}'

    if '-' not in percent:
        comparison = '\U0001F4C8騰落率:'
        percent = f'+{percent}'
    else:
        comparison = '\U0001F4C9騰落率:'
    percentage = f'{comparison}{percent}%\n'

    # URL
    url = f'https://emaxis.jp/fund/{cd}.html\n'
    
    # Tweet文作成
<<<<<<< HEAD
    text = f'{name}\n{percentage}{url}'
=======
    text = f'{name}\n\U0001F4B9騰落率:{percent}%\n'
>>>>>>> 95edd62f311b1754cd5fe33f0f64ab5e86021334
    
    return text

today = datetime.date.today() 

# 今年
year = today.year
# 今月
month = today.month

AC = fundAPI('253425', '\U0001F30FeMAXIS Slim 全世界株式(オールカントリー)') #オルカン
SP = fundAPI('253266', '\U0001F1FA\U0001F1F8eMAXIS Slim 米国株式(S&P500)') #SP500

tweet = f'\U0001F4B9{year}年{month}月の結果(1ヶ月)\n\n{AC}\n{SP}\n#投資 #NISA #オルカン #SP500'
print(tweet)
#client.create_tweet(text = tweet)

# 年末以外は終了
if today.month != 12:
    sys.exit()

def yearAPI(cd, name):
    # エンドポイントの組み立て
    url_fund = f'https://developer.am.mufg.jp/fund_information_latest/fund_cd/{cd}'
    # 協会コードの場合のリクエスト
    fund_response = requests.get(url_fund, headers = {'Content-Type':'application/json'}).json()

    # 騰落率
    percent = fund_response['datasets'][0]['percentage_change_1y']
    percent = f'{float(percent):.02f}'

    if '-' not in percent:
        comparison = '\U0001F4C8騰落率:'
        percent = f'+{percent}'
    else:
        comparison = '\U0001F4C9騰落率:'
    percentage = f'{comparison}{percent}%\n'

    # リスク
    risk = fund_response['datasets'][0]['risk_1y']
    risk = f'{float(risk):.02f}'

    # シャープレシオ(リターン÷リスク)
    sharpratio = fund_response['datasets'][0]['risk_return_1y']
    sharpratio = f'{float(sharpratio):.02f}'

    # URL
    url = f'https://emaxis.jp/fund/{cd}.html\n'

    # Tweet文作成
    text = f'{name}\n{percentage}\u26A0リスク:{risk}%\n\U0001F4CAシャープレシオ:{sharpratio}\n{url}'
    
    return text

AC = yearAPI('253425', '\U0001F30FeMAXIS Slim 全世界株式(オールカントリー)') #オルカン
SP = yearAPI('253266', '\U0001F1FA\U0001F1F8eMAXIS Slim 米国株式(S&P500)') #SP500

tweet = f'\U0001F4B9{year}年の結果\n\n{AC}\n{SP}\n#投資 #NISA #オルカン #SP500'
print(tweet)
#client.create_tweet(text = tweet)
