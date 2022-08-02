import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import telegram
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import telegram
import time

bot = telegram.Bot(token="5345350814:AAH6qL0ij2M-zdOGxNIcJxnFYwZybLqbMXc")

#t_date = datetime.datetime.now().strftime("%Y%m%d")
t_date = '20220522'
c_date = 0
next_date_flags = 0

def movie_alarm_telegram(areacode='01', theatercode='0013', date={t_date}, check_title='닥터 스트레인지-대혼돈의 멀티버스', chat_ids=['5152936169']):
    global c_date
    global t_date
    global next_date_flags
    if(c_date != 0):
        t_date = c_date
    calc_date = 0

    movie_dict = {}

    #options = webdriver.ChromeOptions()
    #options.add_argument("headless")
    
    url = f"http://www.cgv.co.kr/theaters/?areacode={areacode}&theatercode={theatercode}&date={t_date}"
    
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    driver.implicitly_wait(10)
    
    driver.switch_to.frame('ifrm_movie_time_table')
    
    r = driver.page_source

    url_soup = BeautifulSoup(r, 'html.parser')

    flags = 0
    
    movie_infos = url_soup.select("div.col-times > div.info-movie")
    
    if (movie_infos):
        for movie_info in movie_infos:
            screentype_list = []
            title = movie_info.select('a > strong')[0].text.strip()
            #print(movie_info.select('a > strong').get_text())

            screentypes = movie_info.parent.select("span.screentype")

            for screentype in screentypes:
                if(str(screentype.text) == 'IMAX'):
                    screentype_list.append(str(screentype.text))
                    movie_dict[title] = ", ".join(screentype_list)

        for movie in movie_dict.keys():
            movie_open_check_condition1 = (check_title == movie)
            if (check_title == movie):
                flags += 1
            if (flags >= 1) in {movie_open_check_condition1}: #IMAX 예매가 떳을때
                for chat_id in chat_ids: 
                    next_date_flags += 1
                    if(next_date_flags == 3):
                        calc_date = datetime.datetime.strptime(t_date, '%Y%m%d') + datetime.timedelta(days=1)
                        c_date = calc_date.strftime("%Y%m%d")
                        next_date_flags = 0
                    bot.sendMessage(chat_id=chat_id, text = f"{t_date} - {movie}의 {movie_dict[movie]} 예매가 오픈되었습니다.")
                    print(f"{movie}의 {movie_dict[movie]} 예매가 오픈되었습니다.")
        if(flags==0):
        #    bot.sendMessage(chat_id="5152936169",text = "아직 오픈된 예매가 없습니다.")
        #    print(datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S"))
            print(f"{t_date} 아직 오픈된 예매가 없습니다. 현재시간 : " + datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S"))

    driver.quit()

def processing_notify():
    bot.sendMessage(chat_id='5152936169', text = f"작동중 {datetime.datetime.now().strftime('%Y-%m-%d | %H:%M:%S')}")

#if __name__ == "__main__":
#    movie_alarm_telegram(areacode='01', theatercode='0013', date={t_date}, check_title='닥터 스트레인지-대혼돈의 멀티버스', chat_ids=['5152936169'])

sc = BlockingScheduler(timezone='Asia/Seoul')
sc.add_job(movie_alarm_telegram, 'interval', seconds = 30, id='job_1')
sc.add_job(processing_notify, 'cron', hour = '0', minute = '0', id='job_2')
sc.start()