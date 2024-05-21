import requests
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import telegram
import asyncio

async def main():

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(main())


def save_and_extract_keywords():
    url = "https://trends.google.co.kr/trends/trendingsearches/daily?geo=KR&hl=ko"

    # Chrome WebDriver 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 헤드리스 모드로 실행 (브라우저 창 없이 실행)

    # Chrome WebDriver 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)



    # 현재 날짜와 시간 생성
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # HTML 파일 저장
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"google_trends_{timestamp}.html"
    folder_path = "google_trends_data"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    # 키워드 추출
    soup = BeautifulSoup(driver.page_source, "html.parser")
    date_element = soup.select_one(".content-header-title")
    date = date_element.text.strip() if date_element else ""
    index_elements = soup.select(".index")
    keyword_elements = soup.select(".details-top")
    keywords = [(index.text.strip(), element.text.strip(), date) for index, element in zip(index_elements, keyword_elements)]

    # JSON 파일로 저장
    json_filename = f"google_trends_{timestamp}.json"
    json_file_path = os.path.join(folder_path, json_filename)
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(keywords, file, ensure_ascii=False, indent=4)

    print(f"저장된 HTML 파일: {file_path}")
    print(f"저장된 JSON 파일: {json_file_path}")
    print("추출된 키워드:")
    for index, keyword, date in keywords:
        print(f"{index}. {keyword} - {date}")

    # 워드 클라우드 생성
    text = " ".join([keyword for _, keyword, _ in keywords])
    wordcloud = WordCloud(width=800, height=800, background_color="white", font_path="C:/Windows/Fonts/malgun.ttf").generate(text)

    # 워드 클라우드 PNG 파일로 저장
    wordcloud_png_filename = f"wordcloud_{timestamp}.png"
    wordcloud_png_file_path = os.path.join(folder_path, wordcloud_png_filename)
    wordcloud.to_file(wordcloud_png_file_path)
    print(f"저장된 워드 클라우드 PNG 파일: {wordcloud_png_file_path}")

    # PDF 파일 생성
    pdf = FPDF()
    pdf.add_page()

    # 한글 폰트 추가
    pdf.add_font('NanumGothic', '', 'C:/Windows/Fonts/malgunbd.ttf', uni=True)
    pdf.set_font('NanumGothic', size=16)

    # 추출된 날짜 추가
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=current_datetime.encode('utf-8').decode('latin-1'), ln=1, align="C")

    # 워드 클라우드 이미지 추가
    pdf.image(wordcloud_png_file_path, x=10, y=30, w=190)

    # PDF 파일로 저장
    wordcloud_pdf_filename = f"wordcloud_{timestamp}.pdf"
    wordcloud_pdf_file_path = os.path.join(folder_path, wordcloud_pdf_filename)
    pdf.output(wordcloud_pdf_file_path)
    print(f"저장된 워드 클라우드 PDF 파일: {wordcloud_pdf_file_path}")

    # Chrome WebDriver 종료
    driver.quit()

    # 워드 클라우드 PNG 파일 경로
    wordcloud_png_file_path = os.path.join(folder_path, wordcloud_png_filename)

    token = "6414607293:AAF8UQ8pr_-7QGw1rbM26-wHsCqOEJnxf74"
    bot = telegram.Bot(token)

    bot.send_message(chat_id="6327129513", text="hello")

    print("Finished")


# 바로 실행
save_and_extract_keywords()


# 매일 저녁 11시에 실행
schedule.every().day.at("23:00").do(save_and_extract_keywords)

while True:
    schedule.run_pending()
    time.sleep(1)
