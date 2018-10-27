# mors_crawler

Crawler prototype for Engineer's Thesis.

### Warning!
* Beware of DEPTH_LIMIT setting in settings.py. Crawler won't scrap data from pages further than ARG jumps from starting url.   
Comment this line if you want to avoid restriction.

### Short scrapy-crawler tutorial

* ###### Run spider
Move to mors_crawler directory and type in console:
```angular2html
scrapy crawl [spider_name]
``` 
* ###### items.py
Items.py stores objects that can be used to store data from web pages

* ###### Code explanation
Crawler code is pretty easy to understand, but few things must be explained
```angular2html
rules = (
        Rule(LinkExtractor(allow=['https://tmt\.knect365\.com/.+',
                                  'https://www\.mobileworldcongress\.com/.+',
                                  'https://www\.iotdevfest\.com/.+',
                                  'http://singapore.azurebootcamp\.net/.+',
                                  'https://www\.embedded-world\.de/en/.+'],
                           deny=[
                                # Here sites that crawler shouldn't visit
                           ]),
             callback='parse_item',
             follow=True),
    )
```
rules - it's ofc for crawling rules  
allow - list of allowed pages  
deny - list of pages we don't want to visit within our allow pages  
callback - what we should do with our response  
follow - if true it will visit every link in response content(ofc if link fulfill allow rule)

### Short virtualenv tutorial

* ###### Create virtual env:
```angular2html
conda env create -f mors_crawler.yml
```
* ###### Remove virtual env:
```angular2html
conda remove --name mors_crawler --all
```

* ###### Update virtual env dependencies:
```angular2html
source activate mors_crawler
conda env update -f=mors_crawler.yml
```