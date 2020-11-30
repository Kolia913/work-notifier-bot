import requests
from bs4 import BeautifulSoup as bs
import os.path


class KworkParser:
    url = "https://kwork.ru/projects?c=11"
    headers = {
        # "origin": "https://kwork.ru",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.66 Safari/537.36 "
    }
    lastkey = ""
    lastkey_file = ""

    def __init__(self, lastkey_file):
        self.lastkey_file = lastkey_file
        if os.path.exists(lastkey_file):
            self.lastkey = open(lastkey_file, 'r').read()
        else:
            f = open(lastkey_file, 'w')
            self.lastkey = self.get_lastkey()
            f.write(self.lastkey)
            f.close()

    def new_kworks(self):
        r = requests.get(self.url, headers=self.headers)
        html = bs(r.content, 'html.parser')

        new = ''
        try:
            item = html.select('.wants-card__header-title > a')[0]
        except:
            item = {'href': ''}
        if self.lastkey != item.get('href'):
            new = item.get('href')
        return new

    def kwork_info(self, uri):
        r = requests.get(uri, headers=self.headers)
        html = bs(r.content, 'html.parser')

        try:
            title = html.select(".wants-card__left > h1")[0].text
        except:
            title = ''
        try:
            desc = html.find(class_="wants-card__description-text").find('div').text
        except:
            desc = ''
        try:
            green_payment = html.find(class_='wants-card__header-price wants-card__price').text
        except:
            green_payment = ''
        try:
            gray_payment = html.find(class_="wants-card__description-higher-price").text
        except:
            gray_payment = ''
        try:
            link = self.get_lastkey()
        except:
            link = ''

        return {
            "title": title,
            "desc": desc,
            "green_payment": green_payment,
            "gray_payment": gray_payment,
            "link": link
        }

    def get_lastkey(self):
        r = requests.get(self.url, headers=self.headers)
        html = bs(r.content, 'html.parser')

        try:
            item = html.select('.wants-card__header-title > a')[0].get('href')
        except:
            item = ''
        return str(item)

    def update_lastkey(self, new_key):
        self.lastkey = new_key

        with open(self.lastkey_file, 'r+') as f:
            data = f.read()
            f.seek(0)
            f.write(str(new_key))
            f.truncate()

        return new_key
