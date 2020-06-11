import requests
from pyslr import Publication
import time

def crossref(doi):
    def _authros(authors):
        return list(map(lambda x:(x["family"],x["given"]),authors))
    resp = requests.get("http://api.crossref.org/works/%s"%doi)
    time.sleep(1)
    if resp.status_code > 200:
        return None
    else:
        data = resp.json()
        if "message" in data:
            data = data["message"]
            if "type" not in data:
                return None
            
            if "journal" in data["type"]:
                return Publication.Journal(
                    peer_reviewed=True,
                    publisher=data["publisher"],
                    source="crossref",
                    title=data["title"][0],
                    year=data["created"]["date-parts"][0][0],
                    authors=_authros(data["author"]) ,
                    journal_name=data["container-title"],
                    doi=doi
                )
            elif "proceedings-article" in data["type"]:
                return Publication.Paper(
                    peer_reviewed=True,
                    publisher=data["publisher"],
                    source="crossref",
                    title=data["title"][0],
                    year=data["created"]["date-parts"][0][0],
                    authors=_authros(data["author"]),
                    book_title=data["container-title"],
                    series=data["event"]["acronym"],
                    doi=doi
                )
            else:
                return None

