from PIL import Image
from pytesseract import pytesseract
import requests
import random
from bs4 import BeautifulSoup
import urllib.request
import urllib
import glob, os
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yaml
import spacy
import time

pd.options.display.width = 0

class UrcacpScrape():

    def __init__(self):
        self.df = pd.DataFrame()

    #Read config value for ES
    def read_args(self):
        self.values = {}
        with open('config.yaml', 'r') as stream:
            try:
                self.values = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        return self.values

    #Download the images from the webpage
    def GetImages(self):
        self.page = requests.get("https://www.urcacp.com.br/grid")
        self.soup = BeautifulSoup(self.page.content)
        self.newpath = 'images/'
        if not os.path.exists(self.newpath):
            os.makedirs(self.newpath)
        for a_tag in self.soup.find_all('img'):
            try:
                self.row = ((str(a_tag).split('=')[2].split(' ')[0]))
                print(self.row.split('v1')[0][1:-1])
                try:
                    urllib.request.urlretrieve(self.row.split('v1')[0][1:-1],"images/" + str(random.randint(1,100000)) + ".jpg")
                    print('image saved')
                except Exception as e:
                    print('image could not be saved', e)
                # print(row)
            except Exception as e:
                print("Exception occured, ", e)

    #Read text from images using pytesseract, append title, sentiment score and entities
    def ReadText(self):
        self.path = glob.glob('images/*')
        self.nlp = spacy.load('en_core_web_sm')
        self.analyzer = SentimentIntensityAnalyzer()
        # image_path = "images/a.webp"
        for image_path in self.path:
            self.img = Image.open(image_path)

            self.text = pytesseract.image_to_string(self.img)
            print(self.text[:-1])
            self.title = (max(self.text[:-1].split('\n'), key=len))
            print(self.title)
            self.df = self.df.append({'content':self.text[:-1],
                                      'source':'urcacp',
                                      "title":self.title},
                                     ignore_index=True)
        self.df['sentiment_score'] = self.df['content'].apply(lambda x:self.analyzer.polarity_scores(x)['compound'])
        self.df['entities'] = self.df['content'].apply(lambda x: [(e.text, e.label_) for e in self.nlp(x).ents])
        print(self.df)
        return self.df

    #Push to ES
    def PushToES(self, df):
        self.conn_string = self.read_args()['conn']
        self.es = Elasticsearch([self.conn_string])
        self.data = []
        for i, row in df.iterrows():
            self.data.append({
                "_index": 'demo',
                "_source": {
                    'content': row['content'],
                    'source': row['source'],
                    'title': row['title'],
                    'entities': row['entities'],
                    'sentiment_score': row['sentiment_score']
                }
            })
        print(self.data)
        helpers.bulk(self.es, self.data)
        print("data inserted")

if __name__ == '__main__':
    ur_obj = UrcacpScrape()
    while True:
        ur_obj.GetImages()
        df = ur_obj.ReadText()
        ur_obj.PushToES(df)
        time.sleep(86400)