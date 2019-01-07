import requests
from bs4 import BeautifulSoup

class Browsing:
    def __init__(self):
        self.url_list = []

    def GetUrls(self, url):
        r = requests.get(url)
        html_doc = r.text
        soup = BeautifulSoup(html_doc)
        temp_result = soup.find_all('a', 'search_result_row ds_collapse_flag ')
        urls = []
        for item in temp_result:
            urls.append(item['href'])
        return urls

    def GetAllUrls(self):
        root_search_url = 'https://store.steampowered.com/search/?'
        url_list = self.GetUrls(root_search_url)
        for i in range(2, 401):
            new_urls = []
            new_search_url = root_search_url + 'page=' + str(i)
            new_urls = self.GetUrls(new_search_url)
            url_list = [*url_list, *new_urls]
        return url_list

    def WriteUrls(self, url_list):
        f = open('urls.txt', 'w')
        for url in url_list:
            f.write(url + '\n')
        f.close()

if __name__ == '__main__':
    B = Browsing()
    url_list = B.GetAllUrls()
    B.WriteUrls(url_list)
