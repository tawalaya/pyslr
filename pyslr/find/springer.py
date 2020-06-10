from pyslr.find import Finder
from pyslr.common import Publication,Expression
import requests
import time
import json

class SpringerLinkSearch(Finder):

    def __init__(self,api_key):
        self.api_key=api_key

    def name(self):
        return "Springer"

    def search_expression(self,experssion,year=None,subject="Computer Science"):
        template = "subject:\"{}\""
        if year is not None:
            template = template + " and year:{}".format(year)
        
        template = template+" and {}"

        query=template.format(subject,str(experssion))
        return self.search_raw(query)

    def search(self,keywords=[],year=None,subject="Computer Science"):
        return self.search_expression(Expression("or",keywords),year,subject)

    def search_raw(self,query): 
        if self.api_key is None:
            raise ValueError("missing api key")
        
        search_name = "{}-{}".format(self.name(),hash(query)%10**8)
        print("using",query," | ",search_name)
        
        session = requests.Session()
        results = []
        offset = 0

        continue_requests = True
        while continue_requests:
            continue_requests = False
            params={
                "q":query,
                "api_key":self.api_key,
                "p":100,
                "s":offset
            }
            print("fetching",offset)

            resp = session.get("http://api.springernature.com/meta/v2/json",params=params)
            if resp.status_code > 200:
                #TODO: error !!
                print("failed to fetch ...")
                
            else:
                result = resp.json()
                if "records" in result:
                    results += self.parse_results(result["records"],search_name)
                    print("got",len(result["records"])," records")
                page = result["result"]
                if len(page) > 0:
                    page = page[0]
                else:
                    continue
                
                availible = int(page["total"])-(int(page["start"])-1)-int(page["recordsDisplayed"]) 
                print(availible," still availible")
                

                if availible > 0:
                    offset = int(page["start"])+int(page["recordsDisplayed"])
                    continue_requests = True
            
            time.sleep(1)
        
        session.close()

        
        return results

    def parse_results(self,records,search_name):
        publications = []
        unknown = []
        for record in records:
            if record["publicationType"] == "Journal":
                publications.append(Publication.Journal(
                    peer_reviewed=True,
                    publisher=record["publisher"],
                    source=search_name,
                    title=record["title"],
                    year=int(record["publicationDate"][:4]),
                    authors=self.extractAuthros(record["creators"]),
                    journal_name=record["publicationName"],
                    doi=record["doi"])
                )                                                                                                        
            elif record["publicationType"] == "Book" and record["contentType"] == "Chapter":
                publications.append(Publication.Paper(
                    peer_reviewed=True,
                    publisher=record["publisher"],
                    source=search_name,
                    title=record["title"],
                    year=int(record["publicationDate"][:4]),
                    authors=self.extractAuthros(record["creators"]),
                    country=None,
                    book_title=record["publicationName"],
                    doi=record["doi"],
                 ))
            else:
                print("record of unknown type",record)
                unknown.append(record)

        with open("failed_springer.txt","w+") as f:
            json.dump(unknown,f)

        return publications


    def extractAuthros(self,authors):
        return list(map(lambda x:x["creator"].split(","),authors["creators"])) 