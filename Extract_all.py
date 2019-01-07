import requests
from bs4 import BeautifulSoup
import time

class ExtractOneGame:
    def __init__(self, url):
        self.url = url

    def get_soup(self):
        cookies = { 'birthtime': '283993201', 'mature_content': '1' }
        r = requests.get(self.url, cookies=cookies)
        html_doc = r.text
        soup = BeautifulSoup(html_doc)
        return soup

    def get_name(self, soup):
        # Game name
        game = soup.title.string[:-9]
        return game

    def get_price(self, soup):
        # Price
        temp_result = soup.find_all(attrs={"itemprop": "price"})
        try:
            price = temp_result[0]['content']
        except IndexError:
            price = 'Not Available'
        return price

    def get_Mem_Gra_Sto(self, soup):
        # Memory, Graphics, Storage
        try:
            temp_result = soup.find_all('div', 'game_area_sys_req_full')[0]
        except IndexError:
            try:
                temp_result = soup.find_all('div', 'game_area_sys_req_leftCol')[0]
            except IndexError:
                return 'Not available', 'Not available', 'Not available'
        temp_result = temp_result.ul.select('ul > li')
        memory = 0
        graphics = ''
        storage = 0
        for item in temp_result:
            item = item.get_text(strip=True)
            if 'Memory' in item:
                item = item.replace('Memory:', '')
                item = item.replace('RAM', '')
                item = item.split(' ')
                for w in item:
                    try:
                        memory = float(w)
                    except ValueError:
                        pass
                if 'GB' not in item:
                    memory /= 1024
            elif 'Graphics' in item:
                graphics = item[9:]
            elif 'Storage' in item:
                item = item.replace('Storage:', '')
                item = item.split(' ')
                for w in item:
                    try:
                        storage = float(w)
                    except ValueError:
                        pass
                if 'GB' not in item:
                    storage /= 1024
        return str(memory), graphics, str(storage)

    def get_tags(self, soup):
        # Game tag
        temp_result = soup.find_all('a', 'app_tag')
        tags = []
        for item in temp_result:
            tag = item.get_text(strip=True)
            tags.append(tag)
        return ' '.join(tags)

    def get_date(self, soup):
        # Release date
        temp_result = soup.find_all('div', 'date')
        release = temp_result[0].get_text(strip=True)
        return release

    def get_reviews(self, soup):
        # Reviews
        temp_result = soup.find_all('span', 'game_review_summary positive')
        s = ''
        for item in temp_result:
            try:
                if '30 days' not in item['data-tooltip-text']:
                    s = item['data-tooltip-text']
            except KeyError:
                pass
        s = s.replace(' user reviews for this game are positive.', '')
        s = s.replace('of the ', '')
        s = s.replace(',', '')
        try:
            pos_reviews, no_reviews = s.split(' ')
            pos_reviews = pos_reviews[:-1]
            no_reviews = no_reviews
        except ValueError:
            no_reviews = s.split(' ')[0]
            pos_reviews = '0'
        return pos_reviews, no_reviews

    def extract(self):
        soup = self.get_soup()
        temp_result = soup.find_all('div', 'blockbg')
        s = temp_result[0].get_text(strip=True)
        if s[:9] == 'All Games':
            name = self.get_name(soup)
            price = self.get_price(soup)
            memory, graphics, storage = self.get_Mem_Gra_Sto(soup)
            tags = self.get_tags(soup)
            try:
                release = self.get_date(soup)
            except IndexError:
                release = ''
            pos_reviews, no_reviews = self.get_reviews(soup)
            return [name, price, memory, graphics, storage, tags, release, no_reviews, pos_reviews]
        else:
            return 'Not a game'


class ExtractAll:

    def get_df(self):
        f = open('urls.txt', 'r')
        url_list = []
        for line in f:
            url_list.append(line)
        f.close()
        f = open('game_data.csv', 'a', encoding='utf-8')
        for i, url in enumerate(url_list):
            if i%2 == 1:
                time.sleep(5)
            if 'https://store.steampowered.com/app' in url:
                E = ExtractOneGame(url)
                new_game = E.extract()
                if new_game != 'Not a game':
                    f.write(','.join(new_game) + '\n')
        f.close()

if __name__ == '__main__':
    Ex = ExtractAll()
    Ex.get_df()
