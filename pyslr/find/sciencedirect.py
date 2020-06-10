from pyslr.find import Finder
from pyslr.common import Publication,Expression
from datetime import datetime
import requests
import json
import time

class ScienceDirectSearch(Finder):
    def __init__(self,api_key):
        self.api_key = api_key

    def name(self):
        return "Elsivier"

    def search_expression(self,experssion,year=2015,categories=[]):
        return self.search_raw(str(experssion),year,categories)

    def search(self,keywords=[],year=2015,categories=[]):
        return self.search_expression(Expression("OR",keywords,False),year,categories)

    def search_raw(self,query,year,categories): 
        if self.api_key is None:
            raise ValueError("missing api key")
        
        
        
        

        session = requests.Session()
        qs = "{}".format(query)
        if categories is not None and len(categories) > 0:
            qs = qs+" and content-type({})".format(" OR ".join(categories))
        results = []

        offset = 0
        today = datetime.now().year
        done = False
        
        print("using",qs)
        search_name = "{}-{}".format(self.name(),hash(qs)%10**8)
        print("starting",search_name)
        while not done:
            done = True
            params = {
                "apiKey":self.api_key,
                "httpAccept":"application/json",
                "query":qs,
                "date":"{}-{}".format(year,today),
                "start":offset,
                "count":50
            }
            resp = session.get("https://api.elsevier.com/content/search/sciencedirect",params=params)
            if resp.status_code > 200:
                print("failed to request due to {} - {}",resp.status_code,resp.content)
            else:
                data = resp.json()

                if "search-results" in data:
                    data = data["search-results"]
                    if "opensearch:totalResults" in data and "opensearch:startIndex" in data and "opensearch:itemsPerPage" in data:
                        availible = int(data["opensearch:totalResults"])-int(data["opensearch:itemsPerPage"])-int(data["opensearch:startIndex"])
                        if availible > 0:
                            print(availible,"still availible")
                            offset+=int(data["opensearch:itemsPerPage"])+int(data["opensearch:startIndex"])
                            done = False
                    else:
                        print("missing page indicator, last request...")
                    
                    if "entry" in data:
                        entires = data["entry"]
                        results += self._extractPublications(search_name,entires)
                else:
                    print("got unexpected response...")
            time.sleep(1)
        
        print("found {} elements",len(results))
        return results
    
    def _extractPublications(self,search_name,entires):
        results = []
        failed = []
        for entry in entires:
            try:
                if "prism:volume" in entry:
                    pages = None
                    if "prism:endingPage" in entry and "prism:startingPage" in entry:
                        pages = int(entry["prism:endingPage"])-int(entry["prism:startingPage"])
                    results.append(Publication.Journal(
                        peer_reviewed=True,
                        publisher=self.name(),
                        source=search_name,
                        title=entry["dc:title"],
                        year=int(entry["prism:coverDate"][:4]),
                        authors=self._extract_authros(entry["authors"]),
                        journal_name=entry["prism:publicationName"],
                        volume=entry["prism:volume"],
                        num_pages=pages,
                        doi=entry["prism:doi"],
                    ))
                else:
                    failed.append(failed.append(entry))
            except Exception:
                failed.append(failed.append(entry))

        with open("{}_failed.txt".format(self.name()),"w+") as f:
            json.dump(failed,f)

        return results
    
    def _extract_authros(self,authros):
        author = authros["author"]
        if type(author) == str:
            return author.split(" ",1)
        else:
            return list(map(lambda x: x["$"].split(" ",1),author))
        