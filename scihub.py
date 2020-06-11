import requests
from bs4 import BeautifulSoup

def _get(data,keys,idx):
    for key in keys:
        if key in data:
            data = data[key]
        else:
            data = None
            break
    if data is not None:
        if isinstance(data,list):
            for i in idx:
                if i < len(data):
                    data = data[i]
            return data

    return None

def download_pdf(id,doi):
    X = requests.get("https://sci-hub.tw/"+doi)
    if(X.status_code == 200):
        soup = BeautifulSoup(X.content,'lxml')
        frame = soup.find("iframe")
        if frame is not None:
            url = frame.attrs['src']
            
            X = requests.get("http://api.crossref.org/works/%s"%doi)
            
            name = "missing"
            year = 2000
            if X.status_code == 200:
                X = X.json()
                name = _get(X,["message","title"],[0]) 
                if name is not None:
                    name = name.replace(" ","_").replace(":","")
                year = _get(X,["message","published-print","published-print"],[0,0]) 

            r = requests.get(url, stream=True)


            
            with open('{}_{}_{}.pdf'.format(id,name,year), 'wb') as f:
                f.write(r.content)

import csv
import time

with open('to_download.csv','r') as f:
    x = csv.reader(f)
    #skip headers
    x.next()
    for l in x:
        print("downloading ",l[0]," ",l[1])
        download_pdf(l[0],l[1])
        time.sleep(2.5)

