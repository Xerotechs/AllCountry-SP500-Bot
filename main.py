import datetime
import jpholiday 
import json
import requests
import sys
import time
import tweepy

# 今日が祝日かどうか判定する
now = datetime.date.today()
holiday = jpholiday.is_holiday(now)
if holiday == True:
    sys.exit()

# カスタム休日
target_days = ['01-01', '01-02', '01-03', '12-30', '12-31']
for target_day in target_days:
    if now.strftime('%m-%d') == target_day:
        sys.exit()

# jsonファイルを読み取る
with open('data.json') as f:
    jsonfile = json.load(f)

try:
    # Tweepy
    API_Key = jsonfile['API_Key']
    API_Key_Secre = jsonfile['API_Key_Secre']
    Access_Token = jsonfile['Access_Token']
    Access_Token_Secret = jsonfile['Access_Token_Secret']
    client = tweepy.Client(consumer_key=API_Key, consumer_secret=API_Key_Secre, access_token=Access_Token, access_token_secret=Access_Token_Secret)

    # ファンド情報取得
    def fundAPI(cd, max, name, tag):
        # エンドポイントの組み立て
        url_fund = f'https://developer.am.mufg.jp/fund_information_latest/fund_cd/{cd}'
        # 協会コードの場合のリクエスト
        fund_response = requests.get(url_fund, headers = {'Content-Type':'application/json'}).json()

        # 騰落率
        percent_data = fund_response['datasets'][0]['percentage_change']
        # 前日と騰落率が同じならdef抜け
        if jsonfile[cd] == percent_data:
            return 0
        
        # 基準価額最高値
        nav_max_dt = fund_response['datasets'][0]['nav_max_full_dt']
        max_date = jsonfile[max]
        # 更新されていたら記載
        if max_date != nav_max_dt:
            nav_max = f'\U0001F451最高値更新(前回:{max_date[:4]}/{max_date[4:6]}/{max_date[6:]})\n'
            jsonfile[max] = nav_max_dt
            with open('data.json', 'w') as f:
                json.dump(jsonfile, f, indent = 2)
        else:
            nav_max = ''
        
        # 基準価額
        nav = fund_response['datasets'][0]['nav']
        nav = f'基準価格:{nav:,}円\n\n' # 3桁区切りで表示

        # 前日比
        cmp = fund_response['datasets'][0]['cmp_prev_day']
        percent = f'{float(percent_data):.02f}'
        if '-' not in cmp:
            comparison = '\U0001F534前日比:'
            cmp = f'+{cmp}'
            percent = f'+{percent}'
        else:
            comparison = '\U0001F535前日比:'
        change = f'{comparison}{cmp}円({percent}%)\n\n'

        # 基準日
        date = fund_response['datasets'][0]['base_date']
        base = f'基準日:{date[:4]}/{date[4:6]}/{date[6:]}\n\n'

        # 決算日(4月25日)
        today = datetime.date.today() 
        if today.month == 4 and today.day == 25: # 25日
            closing = '\U0001F4C5本日は決算日です\n\n'
        elif today.month == 4 and today.day == 26 and today.weekday() == 0: # 26日
            closing = '\U0001F4C5本日は決算日です\n\n'
        elif today.month == 4 and today.day == 27 and today.weekday() == 0: # 27日
            closing = '\U0001F4C5本日は決算日です\n\n'
        else: # 通常時
            closing = ''

        # URL
        url = f'https://emaxis.jp/fund/{cd}.html\n\n'

        # Tweet文作成
        tweet = f'{name}{nav_max}{nav}{change}{base}{closing}{url}{tag}'
        
        # jsonファイルを書き込む
        jsonfile[cd] = percent_data
        with open('data.json', 'w') as f:
            json.dump(jsonfile, f, indent = 2)

        print(tweet)
        #client.create_tweet(text = tweet) # 動作時はコメントを外す
        return 1

    SP_num = 0
    AC_num = 0
    # 1分ごとに実行、210分経過で終了
    for i in range(1, 211):
        # 引数 1:ファンドコード 2:最高値データ 3:ファンド名 4:ツイートハッシュタグ
        if SP_num == 0:
            SP_num = fundAPI('253266', 'SP_Max', '\U0001F1FA\U0001F1F8eMAXIS Slim 米国株式(S&P500)\n\n', '#投資 #NISA #SP500') # SP500
        if AC_num == 0:
            AC_num = fundAPI('253425', 'AC_Max', '\U0001F30FeMAXIS Slim 全世界株式(オールカントリー)\n\n', '#投資 #NISA #オルカン') # オルカン
        
        # 両方のファンドがツイートすると終了
        if SP_num + AC_num == 2:
            break
        # 1分間待機
        time.sleep(60)

# エラーコードをjsonファイルに保存
except Exception as e:
    import traceback
    error_code = traceback.extract_tb(e.__traceback__)
    jsonfile['error'] = f'{error_code}'
    with open('data.json', 'w') as f:
        json.dump(jsonfile, f, indent = 2)
