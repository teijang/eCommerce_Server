from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pymssql
import time
import AWS_SMTP as ses

def perform_research():
    driver = webdriver.Chrome("c:\\projects\eCommerce\\chromedriver")

    # 네이버 쇼핑을 연다
    driver.get("https://datalab.naver.com/")
    driver.implicitly_wait(5)

    time.sleep(3)

    # DB Connect
    # startDate update
    conn = pymssql.connect(server=db_server, user=user_id, password=user_pwd, database=db_name, port=port_number)
    cursor = conn.cursor()

    # find select button
    select_button = driver.find_element(By.CLASS_NAME, 'select_btn')
    select_button.click()

    cat_index = 0
    while cat_index < 10:
        cat_index += 1

        if cat_index == 1:
            css_selector = '#content > div.spot.section_keyword > div.section.main_tab_opt > div.select.depth._dropdown > ul > li.active > a'
        else:
            select_button.click()
            css_selector = '#content > div.spot.section_keyword > div.section.main_tab_opt > div.select.depth._dropdown > ul > li:nth-child(' + str(cat_index) + ') > a'

        a = driver.find_element(By.CSS_SELECTOR, css_selector)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))).click()

        # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located, '#content')
        # a.click()
        time.sleep(2)

        category_name = a.get_attribute("text")
        print('category='+category_name)



        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'keyword_rank')))
        ranks = driver.find_elements(By.CLASS_NAME, 'keyword_rank')
        # print(len(ranks))

        for rank in ranks:
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'title_cell')))
                title_cell = rank.find_element(By.CLASS_NAME, 'title_cell')
                date_string = ''

                if len(title_cell.text) > 0:
                    date_string = title_cell.text[0:10].replace('.', '-')
                    print(date_string)  # 2022.01.14.(금)

                    # 만약 중복된 정보가 있다면 skip
                    cursor.execute("select * from NaverTrends where research_date='" + date_string
                                   + "' and category_name='" + category_name + "'")

                    existing_no = len(cursor.fetchall())
                    print(existing_no)
                    if existing_no > 0:
                        continue

                    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'title')))
                    titles = rank.find_elements(By.CLASS_NAME, 'title')
                    ranking_no = 0
                    for title in titles:
                        ranking_no += 1
                        if len(title.text) > 0:
                            print('db insert:' + str(ranking_no) + ', title.text')

                            #DB Insert
                            try:
                                params = (date_string, category_name, ranking_no, title.text)
                                msg = cursor.callproc('usp_NaverTrends_Add', params)
                            except:
                                print("Error:", params)
            except:
                pass

        conn.commit()

    conn.close()
    driver.quit() # 브라우저를 닫음


def send_result_email():
    conn = pymssql.connect(server=db_server, user=user_id, password=user_pwd, database=db_name, port=port_number)
    cursor = conn.cursor()
    params = ()
    cursor.execute("exec usp_NaverTrends_GetLatestStatus")

    row = cursor.fetchone()
    body_html = "<!DOCTYPE html><body>"
    first = True
    category_name = ""
    while row:
        if first:
            body_html += "<h1>" + row[0] + "</h1>"
            body_html += "<table style='border: 1px solid gray;border-collapse: collapse;font-size:20px' width=100%>"
            first = False

        body_html += "<tr>"

        if category_name != row[1]:
            body_html += "<td rowspan='10' style='border: 1px solid gray;border-collapse: collapse;'>" + row[1] + "</td>"

        category_name = row[1]
        body_html += "<td style='border: 1px solid gray;border-collapse: collapse;text-align: center;'>" + str(row[2]) + "</td>"
        body_html += "<td style='border: 1px solid gray;border-collapse: collapse;'>" + str(row[3]) + "</td>"

        if str(row[4]) == "New":
            body_html += "<td style='border: 1px solid gray;border-collapse: collapse;background-color:red; text-align: center;'><font color=white>" + str(row[4]) + "</font></td>"
        elif str(row[4]).find('↑') >= 0:
            body_html += "<td style='border: 1px solid gray;border-collapse: collapse;text-align: center;'><font color=red>" + str(row[4]) + "</font></td>"
        else:
            body_html += "<td style='border: 1px solid gray;border-collapse: collapse;text-align: center;'>" + str(row[4]) + "</td>"
        body_html += "</tr>"
        print(row[0], row[1], row[2], row[3], row[4])
        row = cursor.fetchone()

    body_html += "</table></body></html>"
    conn.close()

    print(body_html)
    recipients = ["info@inter-stay.com"]
    bcc_recipients = ["soowoomi@gmail.com"]
    ses.send_email("일일 네이버 트렌드", body_html, "info@inter-stay.com", recipients, bcc_recipients)

if __name__ == '__main__':
    # db_server = '127.0.0.1'
    db_server = '127.0.0.1'
    db_name = 'ecommerce'
    user_id = 'ecomm'
    user_pwd = 'Interstay$$2022'
    port_number = 24700
    perform_research()
    send_result_email()


