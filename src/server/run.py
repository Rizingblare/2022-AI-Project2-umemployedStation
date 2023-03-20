'''
    입력받은 텍스트를 기반으로
    해당 감정에 맞는 음악 추천 서비스를 제공하는 웹서비스
    flask 기반
    사전학습된 Kobert 다중분류 모델을 사용하여 감정을 분류한 후 해당하는 음악을 응답하는 방식
'''

from flask import Flask, render_template, request
import os
import json
import urllib.parse
import urllib.request
import numpy as np
import pandas as pd

# step 2
app = Flask(__name__)
print( __name__ )

def txtGenerator(emotion):
    fList = ['입력하신 문장에서']
    bList = ['이 느껴집니다. 어떤 노래가 필요하신가요?', '가 느껴집니다. 어떤 노래가 필요하신가요?']
    commentDict = {
        'SAD': ['지금 내 상황에 맞는', '슬픈 음악'],
        'MILD': ['지친 마음을 달래주는', '따뜻한 음악'],
        'NATURE': ['복잡한 마음을 비워주는', '자연의 소리'],
        'LOUD': ['스트레스를 날려주는', '시끄러운 노래'],
        'SENTIMENTAL': ['가끔 혼자 있고 싶을 때', '센치한 노래'],
        'FUNNY': ['기분이 좋아지는', '신나는 음악'],
        'LOVELY': ['연애 세포를 자극하는', '사랑 노래'],
    } 
    if emotion == "SCARED":
        f = fList[0]
        e = "공포"
        b = bList[1]
        c = [ ['선택지 1:'] + commentDict['FUNNY'] + ['FUNNY'] , ['선택지 2'] + commentDict['MILD'] + ['MILD'] ]
    elif emotion == "AMAZE":
        f = fList[0]
        e = "놀람"
        b = bList[0]
        c = [ ['선택지 1:'] + commentDict['NATURE'] + ['NATURE'], ['선택지 2'] + commentDict['MILD'] + ['MILD'] ]
    elif emotion == "ANGRY":
        f = fList[0]
        e = "분노"
        b = bList[1]
        c = [ ['선택지 1:'] + commentDict['NATURE'] + ['NATURE'], ['선택지 2'] + commentDict['LOUD'] + ['LOUD'] ]
    elif emotion == "SAD":
        f = fList[0]
        e = "슬픔"
        b = bList[0]
        c = [ ['선택지 1:'] + commentDict['SAD'] + ['SAD'], ['선택지 2'] + commentDict['MILD'] + ['MILD'] ]
    elif emotion == "NEUTRALITY":
        f = fList[0]
        e = "덤덤함"
        b = bList[0]
        c = [ ['선택지 1:'] + commentDict['SENTIMENTAL'] + ['SENTIMENTAL'], ['선택지 2'] + commentDict['LOVELY'] + ['LOVELY'] ]
    elif emotion == "HAPPY":
        f = fList[0]
        e = "행복"
        b = bList[0]
        c = [ ['선택지 1:'] + commentDict['FUNNY'] + ['FUNNY'], ['선택지 2'] + commentDict['LOVELY'] + ['LOVELY'] ]
    elif emotion == "DISGUST":
        f = fList[0]
        e = "혐오"
        b = bList[1]
        c = [ ['선택지 1:'] + commentDict['SENTIMENTAL'] + ['SENTIMENTAL'], ['선택지 2'] + commentDict['LOUD'] + ['LOUD']]

    return f, e, b, c
 
def playlistGenerator(selection):
    df = pd.read_csv('data/trackInfo/{}_TRACKINFO.csv'.format(selection))    
    return df.sample(13)     
        
        
# step 3 : 라우팅 : 요청이 들어오면 누가 응답할지 패턴 설정
# @ -> 데코레이터 -> 함수 안에 함수를 구현하는 클로저가 적용된 기술
@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/sendTxt', methods=['POST'])
def sendTxt():
    
    # Index 페이지의 요청을 담은 result
    result = request.form
    
    # userText에 기록된 텍스트 양옆 공백 제거 
    userText = result.get('userText').strip()

    print("Client 입력:",userText)
    # Google Corab 환경의 ngrok 서버로 predict 요청
    details = urllib.parse.urlencode({'userText': userText})
    details = details.encode('UTF-8')
    
    ngrokServerURI = 'http://63e4-34-105-60-98.ngrok.io'
    requestURL = '/predictKOBERT'
    url = urllib.request.Request(ngrokServerURI + requestURL, details)
    
    url.add_header("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13")
    
    ResponseData = urllib.request.urlopen(url).read().decode("UTF-8")
    emotion = json.loads(ResponseData)['emotion']
    
    print('(ngrok Server) 응답:', emotion)
    frontPart, emotion, backPart, comment = txtGenerator(emotion)
    # frontPart, emotion, backPart, comment = txtGenerator("DISGUST")
    # print(frontPart, emotion, backPart, comment)
    return render_template('select.html', frontPart = frontPart, emotion =  emotion, backPart  = backPart, comment = comment)

@app.route('/userSelection', methods=['POST'])
def result():
    result = request.form
    selection = result.get('select')
    emotion = result.get('emotion')
    
    print("(select)", selection)
    df = playlistGenerator(selection)
    return render_template('res.html', main = df.iloc[0], other = df.iloc[1:], emotion = emotion)

# step 4 : 엔트리 포인트 : 프로그램의 시작점
if __name__ == '__main__':
    app.run(debug=True)