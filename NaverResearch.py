# 소분류 URL을 받아서 top 3 page의 제품 리스트 작성
from bs4 import BeautifulSoup
import requests
import pymssql
import json
import Product as pds

# 전역 변수
source_id = 1  # Naver


def get_Naver_Top_3_page_products(url, page_count=3, search_type='total'):
    # overseas
    # page 1: 'https://search.shopping.naver.com/search/category?catId=50000117&frm=NVSHOVS&origQuery&pagingIndex=1&pagingSize=40&productSet=overseas&query&sort=rel&timestamp=&viewType=list'
    # page 2: 'https://search.shopping.naver.com/search/category?catId=50000117&frm=NVSHOVS&origQuery&pagingIndex=2&pagingSize=40&productSet=overseas&query&sort=rel&timestamp=&viewType=list'

    # total : 전체상품
    # page 1: 'https://search.shopping.naver.com/search/category?catId=50000117&frm=NVSHOVS&origQuery&pagingIndex=1&pagingSize=40&productSet=total&query&sort=rel&timestamp=&viewType=list'

    if search_type == 'overseas':
        if 'productSet=total' in url:
            url = url.replace('productSet=total', 'productSet=checkout&agency=true')

    # print(url)
    # return

    product_list = []
    url_temp = url.replace("pagingIndex=1", "PgIndex")

    # 주어진 페이지 수 만큼 반복
    for i in range(1, page_count+1):
        result = requests.get(url_temp.replace("PgIndex", "pagingIndex=" + str(i)))
        a = result.text
        # print(a)
        soup = BeautifulSoup(a, 'html.parser')

        result_json = soup.find('script', id='__NEXT_DATA__')
        # print(result_json)
        json_object = json.loads(result_json.string)

        total_products = '0'
        total_overseas_products = '0'

        # 해당 카테고리의 전체 상품 수 vs 해외 상품 수
        try:
            for child in json_object['props']['pageProps']['initialState']['subFilters'][0]['filterValues']:
                if child['title'] == '전체':
                    # print('전체상품' + str(child['productCount']))
                    total_products = str(child['productCount'])
                elif child['title'] == '해외직구':
                    # print('해외직구' + str(child['productCount']))
                    total_overseas_products = str(child['productCount'])
        except:
            pass


        # 해당 페이지의 상품 세부 정보

        for child in json_object['props']['pageProps']['initialState']['products']['list']:
            # print(child)
            p = pds.Product()

            try:
                p.product_id = child['item']['id']
            except:
                p.product_id = ''

            try:
                p.rank = child['item']['rank']
            except:
                p.rank = '999'

            try:
                p.product_name = child['item']['productTitle']
            except:
                p.product_name = ''

            try:
                p.image_url = child['item']['imageUrl']
            except:
                p.image_url = ''

            try:
                p.isOverseaProduct = child['item']['overseaTp']
            except:
                p.isOverseaProduct = '0'

            try:
                p.hasLowestCardPrice = child['item']['hasLowestCardPrice']
            except:
                p.hasLowestCardPrice = '0'

            try:
                p.isBrandStore = child['item']['isBrandStore']
            except:
                p.isBrandStore = '0'

            try:
                p.price = str(child['item']['price'])
            except:
                p.price = '0'

            try:
                p.delivery_price = str(child['item']['deliveryFeeContent'])
            except:
                p.delivery_price = '0'

            try:
                p.mall_name = child['item']['mallName']
            except:
                p.mall_name = ''

            try:
                p.mallCount = child['item']['mallCount']
            except:
                p.mallCount = '0'

            try:
                p.reg_date = child['item']['openDate']
            except:
                p.reg_date = ''

            try:
                p.purchase_count = child['item']['purchaseCnt']
            except:
                p.purchase_count = '0'

            try:
                p.review_count = child['item']['reviewCount']
            except:
                p.review_count = '0'

            try:
                p.review_score = child['item']['scoreInfo']
            except:
                p.review_score = ''

            try:
                p.keepCnt = child['item']['keepCnt']
            except:
                p.keepCnt = '0'

            try:
                p.cat3_id = child['item']['category3Id']
                p.cat2_id = child['item']['category2Id']
                p.cat1_id = child['item']['category1Id']
            except:
                p.cat3_id = '0'
                p.cat2_id = '0'
                p.cat1_id = '0'

            try:
                p.cat3_total_products = total_products
                p.cat3_overseas_products = total_overseas_products
            except:
                p.cat3_total_products = '0'
                p.cat3_overseas_products = '0'

            product_list.append(p)


    return product_list

def perform_research(research_id, search_type='total', _db_server='', _db_name='',_user_id='',_user_pwd='',_port_number=1443):
    # startDate update
    conn = pymssql.connect(server=_db_server, user=_user_id, password=_user_pwd, database=_db_name,
                           port=_port_number)
    cursor = conn.cursor()
    cursor.execute('update Research set startedDate = getdate(), finishedDate=null	where research_id=' + str(research_id))
    conn.commit()
    conn.close()

    conn = pymssql.connect(server=_db_server, user=_user_id, password=_user_pwd, database=_db_name, port=_port_number)
    cursor = conn.cursor()

    # 1	1	0	패션의류
    # 64	1	0	패션잡화
    # 175	1	0	화장품/미용
    # 320	1	0	디지털/가전
    # 587	1	0	가구/인테리어
    # 725	1	0	출산/육아
    # 835	1	0	식품
    # 996	1	0	스포츠/레저
    # 1111	1	0	생활/건강
    # 1291	1	0	여가/생활편의
    # 1336	1	0	면세점
    # 1397	1	0	도서
    cursor.execute('select cat_id, cat_URL from research_detail where research_id=' + str(research_id) + ' and finishedDate is null')

    cat3_list = []
    for row in cursor:
        cat3_list.append([row[0], row[1]])

    conn.commit()
    conn.close()

    conn = pymssql.connect(server=_db_server, user=_user_id, password=_user_pwd, database=_db_name,
                           port=_port_number)
    cursor = conn.cursor()
    for c3 in cat3_list:
        print(c3[0], c3[1])  # cat_id , cat_URL
        rst = get_Naver_Top_3_page_products(c3[1], 3, search_type)

        if len(rst) > 0:
            pd = rst[0]     # update category's current total products, overseas products
            params = (research_id, c3[0], pd.cat3_total_products, pd.cat3_overseas_products)
            msg = cursor.callproc('usp_Category_UpdateProductCounts', params)
            # print("Execute SQL", c3[0])

        for pd in rst:
            params = (research_id, source_id, c3[0], pd.rank, pd.product_id, pd.product_name, pd.image_url,
                      pd.isOverseaProduct, pd.hasLowestCardPrice, pd.isBrandStore,
                      pd.price, pd.delivery_price, pd.mall_name, pd.mallCount,
                      pd.reg_date, pd.purchase_count, pd.review_count, pd.review_score, pd.keepCnt,
                      pd.cat3_id, pd.cat2_id, pd.cat1_id)
            # print(params)

            try:
                msg = cursor.callproc('usp_Products_Insert', params)
                # print(row[0], pd.product_name, pd.cat3_total_products, pd.cat3_overseas_products)
                # break
            except:
                print("Error, Params:", params)

        conn.commit()
        # break

    conn.close()

    # finishedDate update
    conn = pymssql.connect(server=_db_server, user=_user_id, password=_user_pwd, database=_db_name, port=_port_number)
    cursor = conn.cursor()
    cursor.execute('update research set finishedDate=getdate() where research_id=' + str(research_id))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # search_type = 'total' # db에 저잔된 url은 해외가 기준이나 total(전체)를 보고싶을 때에는 이 값을 total 로 해준다.

    db_server = '127.0.0.1'
    db_name = 'ecommerce'
    user_id = 'ecomm'
    user_pwd = 'Interstay$$2022'
    port_number = 24700
    perform_research(12, 'total', db_server, db_name, user_id, user_pwd, port_number)


