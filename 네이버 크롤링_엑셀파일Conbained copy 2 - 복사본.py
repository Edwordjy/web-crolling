import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 셀레니움 웹드라이버 실행
driver = webdriver.Chrome()

# 데이터를 저장할 빈 리스트 생성
product_names = []
product_prices = []
product_reviews = []
product_purchase_counts = []
product_dates = []
product_links = []

# 페이지 수 설정
start_page = 1
end_page = 2

for page in range(start_page, end_page + 1):
    # 네이버 쇼핑 페이지로 이동
    url = f"https://search.shopping.naver.com/search/category/100004229?adQuery&agency=true&catId=50000021&npayType=2&origQuery&pagingIndex=1&pagingSize=80&productSet=checkout&query&sort=review&timestamp=&viewType=list"
    driver.get(url)
    time.sleep(3)  # 페이지가 로딩될 때까지 잠시 대기합니다.

    # 무한 스크롤
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 페이지 맨 아래까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 스크롤 후 새로운 상품이 로딩되도록 대기합니다.

        # 새로운 높이 계산 및 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 상품 정보 저장
    product_elements = driver.find_elements(By.CLASS_NAME, "product_link__TrAac")
    price_elements = driver.find_elements(By.CLASS_NAME, "price_num__S2p_v")
    tracking_elements = driver.find_elements(By.CSS_SELECTOR, "a.product_etc__LGVaW.linkAnchor")
    date_elements = driver.find_elements(By.CSS_SELECTOR, "div.product_info_area__xxCTi > div.product_etc_box__ElfVA > span:nth-child(2)")
    link_elements = driver.find_elements(By.CLASS_NAME, "thumbnail_thumb__Bxb6Z")

    for product, price, tracking, date, link in zip(product_elements, price_elements, tracking_elements, date_elements, link_elements):
        product_names.append(product.text)
        product_prices.append(price.text)
        
        # 트래킹 코드에서 리뷰 수와 구매 건수를 추출합니다.
        tracking_text = tracking.text
        # 리뷰 수와 구매 건수를 추출합니다.
        review_count, purchase_count = "", ""
        for item in tracking_text.split(" · "):
            if "리뷰" in item:
                review_count = item
            elif "구매" in item:
                purchase_count = item
        product_reviews.append(review_count)
        product_purchase_counts.append(purchase_count)
        
        product_dates.append(date.text)
        product_links.append(link.get_attribute('href'))

# 누락된 값이 있는 경우 빈 문자열로 대체
product_reviews = [review if review else "" for review in product_reviews]
product_purchase_counts = [purchase if purchase else "" for purchase in product_purchase_counts]

# 데이터프레임 생성
data = {
    "상품명": product_names,
    "가격": product_prices,
    "리뷰": product_reviews,
    "구매건수": product_purchase_counts,
    "등록일": product_dates,
    "링크": product_links
}
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv("product_info_combined.csv", index=False, encoding='utf-8-sig')

# 브라우저 종료
driver.quit()
