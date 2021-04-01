import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from HelperFunctions import HelperMethods

pd.options.display.width = 0

class ElcomercioScrape():
    "Initialize the headers, and create a new dataframe"
    def __init__(self, URL):

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'referrer': 'https://google.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Pragma': 'no-cache'
        }

        self.URL = URL
        self.df = pd.DataFrame(columns={'author', 'title', 'content', 'source', 'url'})

    # Scrape the data from the webpage, append it to dataframe, determine
    # entities and sentiment score, and push to database
    def ScrapeData(self):
        self.page = requests.get(self.URL, headers=self.headers)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.base_url = 'https://elcomercio.pe'
        for a_tag in self.soup.find_all('a', href=True):
            if a_tag['href'].startswith('/economia'):
                if len(a_tag['href'].split('/')) == 5:

                    self.request_href = requests.get(self.base_url + a_tag['href'], headers = self.headers)
                    self.result = BeautifulSoup(self.request_href.content, 'html.parser')
                    self.content = self.result.find_all('div',class_='story-contents__content')
                    # print(self.content[0].text)
                    self.headline = self.result.find('h1',class_='sht__title')
                    # print(self.headline.text)
                    self.author = self.result.find('a',class_='story-contents__author-link')
                    # print(self.author.text)

                    try:
                        self.df = self.df.append({'content': self.content[0].text,
                                                  'title': self.headline.text,
                                                  'author': self.author.text,
                                                  'source': 'elcomercio',
                                                  'url': self.base_url + a_tag['href']},
                                                 ignore_index=True)
                    except Exception as e:
                        print("Exception occured, %s", e)
                    print(self.df.tail())
        self.helper_obj = HelperMethods()
        self.entity_df = self.helper_obj.GetEntities(self.df)
        self.sentiment_df = self.helper_obj.GetSentiment(self.entity_df)
        self.helper_obj.PushToES(self.sentiment_df)
        print("Data inserted")
        print(self.sentiment_df)

if __name__ == "__main__":
    URL = 'https://elcomercio.pe/economia/?ref=ecr'
    el_obj = ElcomercioScrape(URL)
    while True:
        el_obj.ScrapeData()
        time.sleep(86400)