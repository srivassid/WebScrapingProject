# TTRecord

Architecture

![alt text](https://github.com/srivassid/TTRecord/blob/master/flow.jpg?raw=true)

<br><br>
<h2>High Level OverView</h2>
At the high level, i am using BeautifulSoup4 to scrape the data from the websites, then i put that data in a pandas dataframe, then i use Spacy to determine entities in text, vaderSentiment to determine sentiment of the article, and finally store that data in ElasticSearch.

Then i have an API that allows for searching data from ElasticSearch, which can be found at 

http://a4848d1fc15934aceaaf45f4c0d7b063-1043988501.us-east-2.elb.amazonaws.com:5000/getdata?query=%22europe%22

I use Flask as backend.

I have one single docker image that contains all the files, then i have 5 kubernetes deployments that contains 4 scrapers and 1 api pods. 

<h3>Crawlers</h3>
Bloomberg.py, Urcacp.py, Savills.py and Elcomercio.py are the crawlers that scrape data from the websites. They contain the scraping logic.

For the website urcacp.com, it was a little tricky getting the data because it has images. Which is why i first download the imgaes, then i use pytesseract to get text from the images, and then i store it in ES. It is to be notes that i do not have author and title for the data. I find the longest single sentence from the text and use that as title, but i do not have author.

<h3>Helper Functions</h3>

Helper functions are the common functions used by crawler files. They contain functions GetEntities, which use Spacy to determine entiites in the text, and GetSentiment, which uses VaderSentiment to determine sentiment of the article. Sentiment score is a compound score between -1 and 1, -1 being really negative tone and +1 being a really positive tone. It also contains PushToES method, which pushes data to ElasticSearch.

<h3>Docker and Kubernetes</h3>

All the files have been packaged into a single docker image, and then i have 4 kubernetes deployments that run the scrapers which run daily at an interval of 24 hours, and 1 api deployment, which gives access to elasticsearch data. The api has been exposed over loadBalancer which gives anyone access to it externally.
