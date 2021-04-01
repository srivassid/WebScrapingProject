import requests, time
from bs4 import BeautifulSoup
import pandas as pd
from HelperFunctions import HelperMethods

pd.options.display.width = 0

class BloombergScrape():

    "Initialize the headers, and create a new dataframe"
    def __init__(self, URL):

        self.headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://duckduckgo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache'
        }
        self.URL = URL
        self.df = pd.DataFrame(columns={'author','title','content','source','url'})

    #Scrape the data from the webpage, append it to dataframe, determine
    #entities and sentiment score, and push to database
    def ScrapeData(self):

        self.page = requests.get(self.URL,headers=self.headers)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.results = self.soup.find_all('section',class_='hub-zone-righty')

        self.base_url = 'https://bloomberg.com'
        for a_tag in self.soup.find_all('a', href=True):
            if a_tag['href'].startswith('/news/articles/'):
                self.request_href = requests.get(self.base_url + a_tag['href'],
                                                 headers = self.headers)
                self.result = BeautifulSoup(self.request_href.content, 'html.parser')
                self.content = self.result.find_all('div',class_='body-copy-v2 fence-body')
                self.headline = self.result.find('h1', class_='lede-text-v2__hed')
                self.author = self.result.find('a', class_='author-v2__byline')
                try:
                    self.df = self.df.append({'content':self.content[0].text,
                                         'title':self.headline.text,
                                          'author':self.author.text,
                                          'source':'bloomberg',
                                          'url':self.base_url + a_tag['href']},
                                         ignore_index=True)
                except Exception as e:
                    print("Exception occured, %s",e)

                print(self.df.tail(5))
        self.df = self.df.drop_duplicates(subset=['url'], keep='first').dropna(how='any')
        self.df['sentiment_score'] = self.df['content'].apply(lambda x: self.analyzer.polarity_scores(x)['compound'])
        self.df['entities'] = self.df['content'].apply(lambda x: [(e.text, e.label_) for e in self.nlp(x).ents])
        self.helper_obj = HelperMethods()
        self.helper_obj.PushToES(self.df)
        print("Data inserted")

if __name__ == '__main__':
    URL = 'https://www.bloomberg.com/technology'
    bloom_obj = BloombergScrape(URL)
    while True:
        bloom_obj.ScrapeData()
        time.sleep(86400)