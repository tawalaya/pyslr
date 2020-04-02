from urllib.parse import urlencode
from pyslr.find import Finder
from pyslr.common import Publication
from datetime import datetime
import requests
import json
import time




class IEEESearch(Finder):
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'"
    backoff_time = 5

    def name(self):
        return "IEEE"

    def search(self,keywords=[]):
        query = []
        for keyword in keywords:
            query.append("Abstract:({})".format(keyword))
        query=" OR ".join(query)
        return self.search_raw(query)


    def search_raw(self,query,start=2015,end=None):
        search_name = "{}-{}".format(self.name(),hash(query)%10**8)
 
        records = list(self._extract(query,start,end,search_name))

        print("using {} we collected  {} dois, getting detailed information now...".format(query,len(records)))

        return records

    def _extract(self,query,search_name,start=2015,end=None):
        startPage=1
        totalPages = None
        while totalPages is None or startPage < totalPages:
            action,header = self._assembleRequestAction(query)
            x = requests.post('https://ieeexplore.ieee.org/rest/search',json=action,headers=header,page=startPage,startYear=start,endYear=end)
            print("looking up page {}/{}".format(startPage,totalPages))
            if x.status_code == 200:
                resp = x.json()

                totalPages = resp['totalPages'] 

                for r in resp['records']:
                    yield self._convert(r,search_name)
            else:
                print("failed to grab data from ieee {} error:{} cause:{}".format(query,x.status_code,x.content))
                break

            time.sleep(self.backoff_time)
            startPage+=1

    def _assembleRequestAction(self,query,page=1,endYear=None,startYear=2015):
        if not query:
            raise ValueError("query missing!")

        if not endYear:
            endYear = datetime.now().year
        
        action = {
            "action":"search",
            "matchBoolean":True,
            "queryText":query,
            "highlight":False,
            "returnFacets":["ALL"],
            "returnType":"SEARCH",
            "ranges":["{}_{}_Year".format(startYear,endYear)]
        }
        
        if page > 1:
            action["pageNumber"] = page

        header = {
                'User-Agent':self.user_agent,
                "Origin":"https://ieeexplore.ieee.org"
        }

        return action, header

    def _authors(self,r):
        return list(map(lambda x:(x['lastName'],x['firstName']),r['authors'])) 

    def _convert(self,r,search_name):
        if r['isConference']:
            Publication.fromPaper(
                peer_reviewed=True,
                publisher=r['publisher'],
                source=search_name,
                title=r['articleTitle'],
                year=r['publicationYear'],
                authors=self._authors(r),
                country="",
                book_title=r['publicationTitle'],
                series=r[''],
                num_pages=r['endPage']-r['startPage'],
                doi=r['doi'],
                keywords=[],
                abstract=r['abstract'],
                tried=None,
                references=None
            )
        elif r['isJournal'] or r['isJournalAndMagazine']:
            Publication.fromJournal(
                peer_reviewed=True,
                publisher=r['publisher'],
                source=search_name,
                title=r['articleTitle'],
                year=r['publicationYear'],
                authors=self._authors(r),
                country="",
                journal_name=r["publicationTitle"],
                volume=r['volume'],
                num_pages=r['endPage']-r['startPage'],
                doi=r['doi'],
                keywords=[],
                abstract=r['abstract'],
                tried=None,
                references=None
            )
        elif r['isBook']:
            Publication.fromBook(
                peer_reviewed=True,
                publisher=r['publisher'],
                source=search_name,
                title=r['articleTitle'],
                year=r['publicationYear'],
                authors=self._authors(r),
                num_pages=None,
                isbn=None,
                doi='https://ieeexplore.ieee.org/%s'%r['puplicationLink'],
                references=None,
                tried=None
            )
        else:
            print("failed to process %s"%r['doi'])
            with open('failed_bibs.txt',"w+") as f:
                json.dump(r,f)
        
        