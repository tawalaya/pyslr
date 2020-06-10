from urllib.parse import urlencode
from pyslr.find import Finder
from pyslr.common import Publication,Expression
from datetime import datetime
import requests
import json
import time




class IEEESearch(Finder):
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'"
    backoff_time = 5

    def name(self):
        return "IEEE"

    def search_expression(self,experssion):
        return self.search_raw(str(experssion.withTemplate('(All Metadata":"{}")')))

    def search(self,keywords=[]):
        query = []
        for keyword in keywords:
            query.append(r'("All Metadata":"{}")'.format(keyword))
        query=r" OR ".join(query)
        return self.search_raw(query)


    def search_raw(self,query,start=2015,end=None):
        search_name = "{}-{}".format(self.name(),hash(query)%10**8)
 
        records = list(self._extract(query,search_name,start,end))

        print("using {} we collected  {} dois, getting detailed information now...".format(query,len(records)))

        return records

    def _extract(self,query,search_name,start=2015,end=None):
        startPage=1
        totalPages = None
        while totalPages is None or startPage < totalPages:
            action,header = self._assembleRequestAction(query,page=startPage,startYear=start,endYear=end)
            print(action,header)
            x = requests.post('https://ieeexplore.ieee.org/rest/search',json=action,headers=header)
            print("looking up page {}/{}".format(startPage,totalPages))
            if x.status_code == 200:
                resp = x.json()

                totalPages = resp['totalPages'] 
                if 'records' not in resp:
                    print("no content {} {}".format(x.status_code,x.content))
                    break
                else:
                    print(resp)
                
                for r in resp['records']:
                    yield self._convert(r,search_name)
            else:
                print("failed to grab data from ieee {} error:{} cause:{}".format(query,x.status_code,x.content))
                break

            time.sleep(self.backoff_time)
            startPage+=1

    def _assembleRequestAction(self,query,page=1,startYear=2015,endYear=None):
        if not query:
            raise ValueError("query missing!")

        if endYear is None:
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
        return list(map(lambda x:(x['lastName'],x['firstName']),gd(r,'authors',""))) 

    def _convert(self,r,search_name):
        if gd(r,'isConference',False):
            return Publication.Paper(
                peer_reviewed=True,
                publisher=gd(r,'publisher',""),
                source=search_name,
                title=gd(r,'articleTitle',""),
                year=gd(r,'publicationYear',""),
                authors=self._authors(r),
                country="",
                book_title=gd(r,'publicationTitle',""),
                series="",
                num_pages=int(gd(r,'endPage',"0"))-int(gd(r,'startPage',"0")),
                doi=gd(r,'doi',""),
                keywords=[],
                abstract=gd(r,'abstract',""),
                tried=None,
                references=None
            )
        elif gd(r,'isJournal',False) or gd(r,'isJournalAndMagazine',False):
            return Publication.Journal(
                peer_reviewed=True,
                publisher=gd(r,'publisher',""),
                source=search_name,
                title=gd(r,'articleTitle',""),
                year=gd(r,'publicationYear',""),
                authors=self._authors(r),
                country="",
                journal_name=r["publicationTitle"],
                volume=gd(r,'volume',""),
                num_pages=int(gd(r,'endPage',"0"))-int(gd(r,'startPage',"0")),
                doi=gd(r,'doi',""),
                keywords=[],
                abstract=gd(r,'abstract',""),
                tried=None,
                references=None
            )
        elif gd(r,'isBook',False):
            return Publication.Book(
                peer_reviewed=True,
                publisher=gd(r,'publisher',""),
                source=search_name,
                title=gd(r,'articleTitle',""),
                year=gd(r,'publicationYear',""),
                authors=self._authors(r),
                num_pages=None,
                isbn=None,
                doi='https://ieeexplore.ieee.org/%s'%gd(r,'puplicationLink',""),
                references=None,
                tried=None
            )
        else:
            print("failed to process %s"%gd(r,'doi',""))
            with open('failed_bibs.txt',"w+") as f:
                json.dump(r,f)
            return None
        
def gd(dir,key,default):
    if key in dir:
        return dir[key]
    else:
        return default