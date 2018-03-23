from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import datetime

from flask import Flask
from flask import request
from flask import make_response, jsonify

import requests


# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():

    KEY = '43397658736754614d654a3134684733765139674c35416151562e734965534a54746b57736b4b37706c32'

    #エンドポイントの設定
    endpoint = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=REGISTER_KEY'
    url = endpoint.replace('REGISTER_KEY', KEY)

    #dialogflowから送られたユーザークエリから、テキストを抽出
    #contextはどうやって保持しようねー。同じフォルダに格納する？
    req = request.get_json(silent=True, force=True)
    result=req.get("result")
    parameters = result.get("parameters")
    query=parameters.get("any")

    #終わりか否か
    if query=='終了' or query=='終わり' or query=='止めて' or query=='とめて':
        expect_user_response=False
    else:
        expect_user_response=True

    #コンテキスト読み込み
    f=open('tmp/context.txt','r')
    context=f.read()
    f.close()

    #ドコモに接続して返事をもらう。
    payload = {'utt' : query, 'context':context,'nickname':'益子','nickname_y':'ますこ','sex':'男','age':'26'}
    headers = {'Content-type': 'application/json'}

    #送信
    if expect_user_response:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        data = r.json()
        #jsonの解析
        text = data['utt']
        context = data['context']
    else:
        text='楽しかったです。またお話しましょう。'
        context=''


    #contextの書き込み
    f=open('tmp/context.txt','w')
    f.write(context)
    f.close()


    #Google homeに返す
    r = make_response(jsonify({'speech':text,'displayText':text+context,'data':{'google':{'expect_user_response':expect_user_response,'no_input_prompts':[],'is_ssml':False}}}))
    r.headers['Content-Type'] = 'application/json'
    
    return r


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

