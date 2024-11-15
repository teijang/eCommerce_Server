class Product:
    id = ''
    rank = ''
    name = ''
    image_url = ''
    isOverseaProduct = '0'
    hasLowestCardPrice = '0'
    isBrandStore = '0'
    price = '0'
    delivery_price = '0'
    total_price = '0'
    mall_name = ''
    mallCount = '0'
    reg_date = ''
    purchase_count = '0'
    review_score = '0.0'
    review_count = '0'
    keepCnt = '0'

    cat3_id = ''
    cat2_id = ''
    cat1_id = ''

    cat3_total_products = '0'
    cat3_overseas_products = '0'

    def __init__(self, _product_id='', _product_name=''):
        self.product_id = _product_id
        self.product_name = _product_name