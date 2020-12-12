from selectorlib import Extractor
import requests
import json
import random
from time import sleep

e = Extractor.from_yaml_file('selectors.yml')


def scrape(url):

    f = open('headers.json',) 

    data = json.load(f) 

    headers = random.choice(data)

    f.close() 

    print("Download %s"%url)
    r = requests.get(url, headers=headers)

    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None

    return e.extract(r.text)

