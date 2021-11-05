from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By 

from bs4 import BeautifulSoup
import requests
import time
import pandas
import datetime
import yaml

# 예약한 화면을 캡쳐하는 시간(년, 월, 일, 시, 분, 초)으로 파일 이름 생성
def create_time_name():
    time_now = datetime.datetime.now()
    time_name = str(time_now.year) + str(time_now.month) + str(time_now.day) + str(time_now.hour) + str(time_now.minute) + str(time_now.second)
    return time_name

# 날짜와 날짜(년, 월, 일) 사이의 남은 일 수를 리턴하는 함수
def date_range(start, end):
    start = datetime.datetime.strptime(start, "%Y%m%d")
    end = datetime.datetime.strptime(end, "%Y%m%d")
    dates = [date.strftime("%Y%m%d") for date in pandas.date_range(start, periods=(end-start).days+1)]
    return dates

# 요일을 리턴하는 함수
def getDay_c(year,month,day):
    daylist = ['월', '화', '수', '목', '금', '토', '일']
    return daylist[datetime.date(year,month,day).weekday()]

# 예약 가능한 날짜 리턴하는 함수
def search_reservation(searching_start_date, searching_end_date):
    start_time = datetime.datetime.now()

    dates = date_range(str(info["searching_start_date"]), str(info["searching_end_date"]))
    possible_list = list()
    print("< 남당피싱 >")
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
    
    end_time = datetime.datetime.now()
    print("검색 소요 시간: ", end_time - start_time)
    
    return possible_list

def auto_reservation(possible_list, date, info):
    if date in possible_list:
        options = webdriver.ChromeOptions()

        """
        # 창 숨기는 옵션 추가
        options.add_argument("--headless")
        """
        
        options.add_argument("--headless")
        # 크롬드라이버가 설치된 경로로 크롬 웹 드라이버 객체 생성
        # driver = webdriver.Chrome('C:/kss/crawling/chromedriver', options=options)
        driver = webdriver.Chrome('crawling/chromedriver', options=options)

        try:
            start_time = datetime.datetime.now()
            # 남당피시 url Get
            driver.get(f'https://www.namdangfishing.com/_core/module/reservation_boat_v3/popup.step1.php?date={date}&PA_N_UID=563')
            
            # 캡쳐할 화면의 크기 설정
            driver.set_window_size(800, 1150)
            # 체크박스 클릭
            driver.find_element(By.NAME, 'PS_N_UID').click()

            # 인원 수 입력
            select = Select(driver.find_element(By.ID, "BI_IN"))
            select.select_by_value(str(info["persons"]))

            # 예약자 이름 입력
            driver.find_element(By.NAME, 'BI_NAME').send_keys(info["name"])

            # 입금자 이름 입력
            driver.find_element(By.ID, 'BI_BANK').send_keys(info["depositor"])

            # 핸드폰 번호 입력
            driver.find_element(By.ID, 'BI_TEL2').send_keys(info["cell_num"].split('-')[1])
            driver.find_element(By.ID, 'BI_TEL3').send_keys(info["cell_num"].split('-')[2])

            # 전체 동의 라디오 박스 클릭
            driver.find_element(By.NAME, 'all_agree').click()

            # 첫 번째 페이지의 제일 아래 예약버튼 클릭
            driver.find_element(By.XPATH, '//*[@id="submit"]').click()

            # 팝업창 클릭
            Alert(driver).accept()

            # 두번째 페이지의 예약 신청하기 클릭
            if (info["payment"]):
                driver.find_element(By.XPATH, '//*[@id="submit"]').click()
            
            # 스크린샷 파일 저장
            driver.save_screenshot(f"screenshot/screenshot{create_time_name()}.png")
            
            # for debugging
            # time.sleep(5)

            driver.close()
            end_time = datetime.datetime.now()
            print("예약 소요 시간: ", end_time - start_time)
            
            return True

        except:
            pass

    else:
        print("예약 가능한 날짜가 아닙니다.")
        print("예약할 날짜를 다시 한 번 확인해 주세요.")

        return False

if __name__ == "__main__":
    info = dict()

    with open('C:\kss\crawling\info.yaml', 'r', encoding='UTF8') as f:
        config = yaml.safe_load(f)
        info["searching_start_date"] = config["searching_start_date"]
        info["searching_end_date"] = config["searching_end_date"]
        info["persons"] = config["persons"]
        info["name"] = config["name"]
        info["depositor"] = config["depositor"]
        info["cell_num"] = config["cell_num"]
        info["payment"] = config["payment"]

        # print("< 낚시 예약 사이트 리스트 >")
        # print("1. 남당피싱")
        # print("2. 대천항 아인스월드")
        # site_num = int(input())
        # print("뒤로가기 : 0")

        # if ord(input()) == 48:
        #     # print("test")
        #     continue
    while True: 
        print("----------예약 가능한 날짜 리스트----------")
        possible_list = search_reservation(info["searching_start_date"], info["searching_end_date"])
        print("----------예약 가능 날짜 검색 종료----------")
        print("예약하실 날짜를 입력해주세요")
        date = input().replace('-', '')
        if auto_reservation(possible_list, date, info):
            break
        else:
            continue
    