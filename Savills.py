import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from HelperFunctions import HelperMethods

pd.options.display.width = 0

class SavillsScrape():

    "Initialize the headers, and create a new dataframe"
    def __init__(self, URL):
        self.headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache'}

        self.URL = URL
        self.df = pd.DataFrame(columns={'author', 'title', 'content', 'source', 'url'})

    # Scrape the data from the webpage, append it to dataframe, determine
    # entities and sentiment score, and push to database
    def ScrapeData(self):
        self.page = requests.get(self.URL, headers=self.headers)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.df_temp = pd.DataFrame()
        self.base_url = 'https://www.savills.com.mx'
        for a_tag in self.soup.find_all('a', href=True):
            if a_tag['href'].startswith('/research-and-opinion/savills-news/'):
                self.df_temp = self.df_temp.append({'href':a_tag['href']},ignore_index=True)
                self.df_temp = self.df_temp.drop_duplicates(keep='first')

        for i,row in self.df_temp.iterrows():
            self.request_href = requests.get(self.base_url + row['href'], headers=self.headers)
            self.result = BeautifulSoup(self.request_href.content, 'html.parser')
            self.content = self.result.find_all('div', class_='vx_drag vx_blocks_file_blocks_sv-4')
            self.title = self.result.find('div',class_='sv-article__intro')
            self.author = self.result.find('dd',class_='sv-author-panel__description')
            self.img = self.author.find('img', alt=True)

            try:
                self.df = self.df.append({'author':self.img['alt'],'content':self.content[0].text,
                                          'title':self.title.text,'url':self.base_url + row['href'],
                                          'source':'savillis'},ignore_index=True)
            except Exception as e:
                print("An exception has occured, %s",e)
            print(self.df.tail())

        self.df = self.df.drop_duplicates(subset=['author', 'title'], keep='first').reset_index().dropna(how='any')
        self.helper_obj = HelperMethods()
        self.entity_df = self.helper_obj.GetEntities(self.df)
        self.sentiment_df = self.helper_obj.GetSentiment(self.entity_df)
        self.helper_obj.PushToES(self.sentiment_df)
        print("Data inserted")

if __name__ == '__main__':
    URL = 'https://www.savills.com.mx/research-and-opinion/savills-news.aspx?rc=World&p=&f=date&q=&page=1'
    sa_obj = SavillsScrape(URL)
    while True:
        sa_obj.ScrapeData()
        time.sleep(86400)