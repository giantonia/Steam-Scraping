from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import pandas as pd


class ExtractOne:
    def __init__(self, url):
        self.soup = BeautifulSoup()
        self.url = url
        self.name = ''
        self.helpful = []
        self.hours = []
        self.date = []
        self.recommended = []
        self.review = []
        self.products = []

    def get_soup(self, current):
        driver = webdriver.Chrome('E:\Download\chromedriver.exe')
        driver.get(self.url)
        try:
            driver.find_element_by_partial_link_text('All Games')
        except Exception:
            return current+1
        try:
            select = Select(driver.find_element_by_id('ageDay'))
            select.select_by_value('1')
            select = Select(driver.find_element_by_id('ageMonth'))
            select.select_by_value('January')
            select = Select(driver.find_element_by_id('ageYear'))
            select.select_by_value('1990')
            button = driver.find_element_by_partial_link_text('View Page')
            button.click()
            time.sleep(1)
        except Exception:
            pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            button = driver.find_element_by_class_name('class="broadcast_embeddable_PopOutVideoCloseButton_2gi7o btnv6_blue_hoverfade"')
            button.click()
        except Exception:
            pass
        driver.implicitly_wait(15)
        try:
            button = driver.find_element_by_partial_link_text('Browse all')
            button.click()
            driver.implicitly_wait(15)
            try:
                select = Select(driver.find_elements_by_xpath("//*[contains(text(), 'Content posted in this community')]"))
                button = driver.find_element_by_partial_link_text('View Page')
                button.click()
                time.sleep(3)
            except Exception:
                pass
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.soup = BeautifulSoup(driver.page_source)
            driver.close()
        except Exception:
            return current+1

    def get_name(self):
        temp_result = self.soup.title.get_text(strip=True)
        self.name = temp_result[19:]

    def get_review(self):
        temp_result = self.soup.find_all('div', 'apphub_UserReviewCardContent')

        for i in range(len(temp_result)):
            self.helpful.append(temp_result[i].find_all('div', 'found_helpful')[0].get_text(strip=True).split(' ')[0])
            self.hours.append(temp_result[i].find_all('div', 'hours')[0].get_text(strip=True).split(' ')[0])
            self.date.append(temp_result[i].find_all('div', 'date_posted')[0].get_text(strip=True)[8:])
            self.recommended.append(1 if temp_result[i].find_all('div', 'title')[0].get_text(strip=True)=='Recommended' else 0)
            self.review.append(temp_result[i].find_all('div', 'apphub_CardTextContent')[0].get_text().splitlines()[-1].replace('\t', ''))

    def get_products(self):
        temp_result = self.soup.find_all('div', 'apphub_CardContentMoreLink ellipsis')
        for item in temp_result:
            try:
                self.products.append(item.string.split(' ')[0])
            except AttributeError:
                self.products.append(0)

    def construct(self, current):
        temp = self.get_soup(current)
        if temp == current+1:
            return current+1
        else:
            self.get_name()
            self.get_review()
            self.get_products()
            df = pd.DataFrame({"Game": [self.name]*len(self.recommended), "Hours": self.hours, "Recommended": self.recommended, "Date": self.date,
                              "Helpful": self.helpful, "Review":self.review, "Products": self.products})
            return df

class ExtractAllReviews:
    def __init__(self):
        self.url_list = []

    def get_url_list(self):
        f = open('urls.txt', 'r')
        for line in f:
            self.url_list.append(line)
        f.close()

    def extract(self):
        self.get_url_list()
        current_url = 2038
        while True:
            try:
                for i, url in enumerate(self.url_list[current_url:]):
                    if i%3 == 1:
                        time.sleep(2)
                    if 'https://store.steampowered.com/app' in url:
                        EO = ExtractOne(url)
                        new_reviews = EO.construct(current_url)
                        if type(new_reviews) == type(1):
                            pass
                        else:
                            new_reviews.to_csv('game_review.csv', mode='a', sep=',', encoding='utf-8', header=False)
                        current_url += 1
            except Exception as e:
                current_url += 1
                print(e)
                pass


if __name__ == '__main__':
    EAR = ExtractAllReviews()
    EAR.extract()
