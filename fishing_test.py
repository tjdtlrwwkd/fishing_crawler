import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert

import requests
from bs4 import BeautifulSoup
import pandas
import datetime

info = {
    "searching_start_date": 20211107,
    "searching_end_date": 20211120,
    "persons": 1,
    "name": "김성식",
    "depositor": "김성식",
    "cell_num": "010-9026-6563",
    "payment": False
}

def date_range(start, end):
    start = datetime.datetime.strptime(start, "%Y%m%d")
    end = datetime.datetime.strptime(end, "%Y%m%d")
    dates = [date.strftime("%Y%m%d") for date in pandas.date_range(start, periods=(end-start).days+1)]
    return dates

def getDay_c(year,month,day):
    daylist = ['월', '화', '수', '목', '금', '토', '일']
    return daylist[datetime.date(year,month,day).weekday()]
# https://www.einsho.com/_core/module/reservation_boat_v3/popu2.step1.php?date=20211107&PA_N_UID=2730&PH_N_UID=0&PS_N_UID=15366&scr=0
def search_reservation():
    dates = date_range(str(info["searching_start_date"]), str(info["searching_end_date"]))
    possible_list = list()

    print("<남당피싱>")
    for date in dates:
        url = f'https://www.namdangfishing.com/_core/module/reservation_boat_v3/popup.step1.php?date={date}&PA_N_UID=563'
        webpage = requests.get(url)
        soup = BeautifulSoup(webpage.content, "html.parser")
        txt = str(soup).replace(" ", "")
        if "예약할수없는" in txt:
            # print(f'impossible: {date}')
            pass
        else:
            possible_list.append(date)
            print(f'{date[:4]}-{date[4:6]}-{date[6:]} ({getDay_c(int(date[:4]), int(date[4:6]), int(date[6:]))})')
    return possible_list

def auto_reservation(possible_list, date):
    if date in possible_list:
        options = webdriver.ChromeOptions()

        """
        # 창 숨기는 옵션 추가
        options.add_argument("headless")
        """

        driver = webdriver.Chrome('C:/kss/crawling/chromedriver', options=options)

        try:
            driver.get(f'https://www.namdangfishing.com/_core/module/reservation_boat_v3/popup.step1.php?date={date}&PA_N_UID=563')
            driver.find_element_by_name('PS_N_UID').click() 
            
            select = Select(driver.find_element_by_id("BI_IN"))
            select.select_by_value(str(info["persons"]))

            driver.find_element_by_name("BI_NAME").send_keys(info["name"])
            driver.find_element_by_id("BI_BANK").send_keys(info["depositor"])
            
            driver.find_element_by_id("BI_TEL2").send_keys(info["cell_num"].split('-')[1])
            driver.find_element_by_id("BI_TEL3").send_keys(info["cell_num"].split('-')[2])
            
            driver.find_element_by_name("all_agree").click() 
            

            driver.find_element_by_xpath('//*[@id="submit"]').click()

            Alert(driver).accept()
            
            if (info["payment"]):
                driver.find_element_by_xpath('//*[@id="submit"]').click()

            time.sleep(5)

        except:
            pass

    else:
        print("예약 가능한 날짜가 아닙니다.")
        print("예약할 날짜를 다시 한 번 확인해 주세요.")

if __name__ == "__main__":
    print("----------예약 가능한 날짜 리스트----------")
    possible_list = search_reservation()
    print("----------예약 가능 날짜 검색 종료----------")
    print()
    print("예약하실 날짜를 입력해주세요")
    date = input().replace('-', '')
    auto_reservation(possible_list, date)