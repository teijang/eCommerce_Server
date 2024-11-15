from bs4 import BeautifulSoup
import requests
import pymssql
import json

# 네이버 쇼핑 메인
url = "https://shopping.naver.com/home/p/index.naver"
result = requests.get(url)
a = result.text
# print(a)
soup = BeautifulSoup(a, 'html.parser')

# 대분류
firstCategory = soup.select('#home_category_menu > ul > li > button')

conn = pymssql.connect(server='3.35.120.148', user='ecomm', password='Interstay$$2022', database='ecommerce', port=24700)
cursor = conn.cursor()

for i, item in enumerate(firstCategory, 1):
    cat_id = item['category-id']
    print(i, item['category-id'])
    img = item.find('img')
    print(img['alt'])

    params = (1, img['alt'], 0, '', 0, pymssql.output(str))
    msg_first = cursor.callproc('usp_Category_Update', params)
    new_first_id = msg_first[5]  # 생성된 대분류 ID

    # 중분류
    secondCategory = soup.select('#middleCategory_' + cat_id +' > ul > li > a')
    for j, sub_item in enumerate(secondCategory, 1):
        print(sub_item['href'])
        print(j, sub_item.string.strip())

        msg_second = cursor.callproc('usp_Category_Update', (1, sub_item.string.strip(), 1, sub_item['href'], new_first_id, pymssql.output(str)))
        new_second_id = msg_second[5]  # 생성된 중분류 ID

        # 해당 중분류 URL에서 소분류명 취합

        url = sub_item['href']
        result = requests.get(url)
        a = result.text
        soup_third = BeautifulSoup(a, 'html.parser')

        try:
            # 방법 1 : JSON으로부터 직접 추출
            result_json = soup_third.find('script', id='__NEXT_DATA__')
            # print(result_json)
            json_object = json.loads(result_json.string)

            for child in json_object['props']['pageProps']['initialState']['mainFilters'][0]['filterValues']:
                # 소분류명만 클릭했을 때
                # https://search.shopping.naver.com/search/category?catId=50000805&frm=NVSHCAT&origQuery&pagingIndex=1&pagingSize=40&productSet=total&query&sort=rel&timestamp=&viewType=list

                # 해외직구만 클릭했을 때
                # https://search.shopping.naver.com/search/category?catId=50000805&frm=NVSHOVS&origQuery&pagingIndex=1&pagingSize=40&productSet=overseas&query&sort=rel&timestamp=&viewType=list
                print(f'title = {child["title"]}, vlaue={child["value"]}')
                url = 'https://search.shopping.naver.com/search/category?catId=' + child["value"] + '&frm=NVSHOVS&origQuery&pagingIndex=1&pagingSize=40&productSet=overseas&query&sort=rel&timestamp=&viewType=list'
                params = (1, child["title"], 2, url, new_second_id, pymssql.output(str))
                msg_third = cursor.callproc('usp_Category_Update', params)
                new_third_id = msg_third[5]  # 생성된 소분류 ID
        except:
            # 방법 2 : li 요소로부터 텍스트 가져오기 : but CatId 값은 없음
            thirdCategory = soup_third.select('#__next > div > div.style_container__1YjHN > div > div.filter_finder__1Gtei > div.filter_finder_filter__1DTIN > div.filter_finder_col__3ttPW.filter_is_active__3qqoC > div.filter_finder_row__1rXWv > div > ul > li')
            # print(thirdCategory)

            for k, third_item in enumerate(thirdCategory, 1):
                # print(third_item)
                span = third_item.find('span')
                print(span.string)

                params = (1, str(span.string), 2, '', new_second_id, pymssql.output(str))
                msg_third = cursor.callproc('usp_Category_Update', params)
                new_third_id = msg_third[5]  # 생성된 소분류 ID

        # break

    # break

conn.commit()
conn.close()


