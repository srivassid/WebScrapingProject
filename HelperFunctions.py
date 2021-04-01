import pandas as pd
import yaml
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from elasticsearch import Elasticsearch, helpers

class HelperMethods():

    def __init__(self):
        pass

    #Read config file for value of connection string of ES
    def read_args(self):
        self.values = {}
        with open('config.yaml', 'r') as stream:
            try:
                self.values = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        return self.values

    #Use spacy to determine entitites, append those to original dataframe
    def GetEntities(self,df):
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp_df = pd.DataFrame()
        for i, row in df.iterrows():
            self.sentence = row['content']

            self.doc = self.nlp(self.sentence)
            self.text = [(e.text) for e in self.doc.ents]
            self.labels = [(e.label_) for e in self.doc.ents]
            self.nlp_df = self.nlp_df.append({'entities':
                                                  [(e.text,e.label_) for e in self.doc.ents],
                                              'title':row['title']},
                                                ignore_index=True)
        # df['entities'] = self.nlp_df['entities']
        try:
            df = df.merge(self.nlp_df, left_on='title', right_on='title')
        except Exception as e:
            print("Exception merging datasets ", e)
        print(df)
        return df

    #Use vaderSentiment to determine sentiment score of text, append it to original dataframe
    def GetSentiment(self,df):
        self.analyzer = SentimentIntensityAnalyzer()
        self.sent_df = pd.DataFrame()
        for i, row in df.iterrows():
            self.sent_df = self.sent_df.append({'sentiment_score':
                                                    self.analyzer.polarity_scores(row['content'])['compound'],
                                                'title':row['title']},
                                               ignore_index=True,
                                               )
        df = df.merge(self.sent_df,left_on='title',right_on='title')
        # df['sentiment_score'] = self.sent_df['sentiment_score']
        print(df)
        return df

    #Push dataframe to ES
    def PushToES(self, df):
        self.conn_string = self.read_args()['conn']
        self.es = Elasticsearch([self.conn_string])
        self.data = []
        for i, row in df.iterrows():
            # print(row)
            self.data.append({
                "_index": 'demo',
                "_source": {
                    'author': row['author'],
                    'content': row['content'],
                    'title': row['title'],
                    'url': row['url'],
                    'source': row['source'],
                    'entities': row['entities'],
                    'sentiment_score': row['sentiment_score']
                }
            })
        print(self.data)
        helpers.bulk(self.es, self.data)
        print("data inserted")
