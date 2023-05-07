# server sides
import time
from datetime import datetime
from datetime import timezone, timedelta
import smtplib

import requests
from bs4 import BeautifulSoup as bs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from setting import *

# 메일 초기설정
TW = timezone(timedelta(hours=9)) # 서버시간 = UTC 기준 이므로 시차보정
now = datetime.now(TW)
titleText = NAME + "님의 " + str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) + "일 예약 결과"
contentText = ""
# 크롤링 초기설정
login_info = {
    'ms_id': MAIL_ID, # id
    'ms_password': MAIL_PW #pw
}
session = requests.session()

def mailSend(title, contents): # 메일전송 함수
    smtp_server = smtplib.SMTP( # 1
        host='smtp.gmail.com',
        port=587
    )
    str_cc = ','.join(list_cc)
    
    smtp_server.ehlo() # 2
    smtp_server.starttls() # 2
    smtp_server.ehlo() # 2
    smtp_server.login(sender, sender_pw) # 3
    
    msg = MIMEMultipart() # 4
    msg['From'] = sender # 보내는이
    msg['To'] = recipient # 받는이
    msg['Cc'] = str_cc # 참조
    msg['Subject'] = contents # 5
    msg.attach(MIMEText(contents, 'plain')) # 6
    
    smtp_server.send_message(msg) # 메세지 전송
    smtp_server.quit() # stmp 종료
    
def login(login_url, login_info): # 해당 url에 로그인 패킷 전송
    res = session.post(login_url, data = login_info) #
    res.raise_for_status() # 오류 발생하면 예외 발생

def getText(soup, path): # 해당하는 element의 내부 텍스트값 반환
    return soup.select_one(path).text

def res(url): # 해당에 url에 html 정보 요청
    res = session.get(url)
    res.raise_for_status()
    return res

def timer(timeUnit, w, h):
    switch = False # 하루에 한번 초기화 (True == 그날 이미 크롤링, 메일전송 완료
    now = datetime.now(TW)
    weeker = now.day # 최종 크롤링 성공 날짜
    while(True):
        now = datetime.now(TW) 
        if not switch: # 크롤링, 메일전송 한 적 없을 경우
            if ((datetime.now(TW).weekday() == w) and (now.hour == h)): # 현재 요일 = 설정한 요일, 현재 날짜 = 설정한 날짜일 경우
                login(login_url, login_info)
                soup = bs(res(reserv_url).content, "html.parser") # html 요소 파싱
                reserv = getText(soup, TARGET1)
                if(reserv == '○'): # 당일 예약 성공 시
                    soup = bs(res(reserv_url).text, "html.parser")
                    mydate = getText(soup, TARGET2)
                    contentText = str(now.month) + "월" + str(now.day)+ "일 수행결과 : 예약 성공 - 예약 날짜: " + mydate
                else: # 당일 예약 실패 시
                    soup = bs(res(point_url).text, "html.parser")
                    mypoint = getText(soup, TARGET3)
                    contentText = str(now.month) + "월" + str(now.day)+ "일 수행결과 : 예약 실패 - 보유포인트: " + str(mypoint)
                
                weeker = now.day # 크롤링 성공 -> weeker 갱신
                mailSend(titleText, contentText) # 메일 전송
                print("mail send success")
                switch = True # 스위치 = true 일 때, 오늘 하루동안 크롤링을 하지 않음
            else:
                print("switch off: sleep... zzz at " + str(now.day) +'/'+ str(now.hour) +':'+ str(now.minute), datetime.now(TW).weekday())
                time.sleep(timeUnit)
        else:
            if (weeker != now.day): # 하루가 지났을 때
                weeker = now.day # weeker 에 오늘 할당
                switch = False # 스위치 초기화
                print("switch on: new day!!")
            else:
                print("switch on: sleep... zzz at " + str(now.day) +'/'+ str(now.hour) +':'+ str(now.minute), datetime.now(TW).weekday())
                time.sleep(timeUnit) # timeunit 초 마다 한번씩 작동
                
                      
timer(1200, 1, 17) # 대기시간(n초에 한번 함수 실행), 요일(월 = 0 ~ 일 = 6), 시간