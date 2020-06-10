import scrapy
from urllib.parse import urlencode
from scrapy.crawler import CrawlerProcess
from pyslr.find import Finder
from pyslr.common import Publication,Expression
import requests
import json
import time


class ACMSearchDOISpiderr(scrapy.Spider):
    name="ACM-Serach-Spider"
    results_per_page=50
    def __init__(self, after_year=2015,query=None,results=[], *args, **kwargs):
        super(ACMSearchDOISpiderr, self).__init__(*args, **kwargs)
        q = {'AllField':query}
        allfields=urlencode(q).replace('%28','(').replace("%22","\"").replace("%29",")") 
        baseurl = 'https://dl.acm.org/action/doSearch?fillQuickSearch=false&expand=dl&AfterYear={}&{}++'
        self.start_urls = [baseurl.format(after_year,allfields)]
        self.results = results
        print("using",self.start_urls)

    def parse(self,response):

        for doi in map(lambda x:x[len('https://doi.org/'):],response.xpath('//a[contains(@class,"item__doi")]/@href').getall()):
            self.results.append(doi)
            yield {"doi":doi}
        
        baseurl =response.request.url
        if "startPage" not in baseurl:
            
            #number of found items/items per page
            pages = round(int(response.css('span.hitsLength::text').get().replace(',',''))/self.results_per_page)

            for page in range(pages):
                yield scrapy.Request('{}&pageSize={}&startPage={}'.format(baseurl,self.results_per_page,page))



class ACMSearch(Finder):
    def name(self):
        return "ACM"

    def from_dois(self,filename):
        dois = []
        with open(filename,"r") as f:
            dois = list(map(lambda x:x.strip(),f.readlines()))
        
        self._fromDoiToInternal(dois,search_name="FROM_DOIS")

        def search_expression(self,experssion):
            return self.search_raw(str(experssion.withTemplate("Abstract:({})")))

    def search(self,keywords=[]):
        query = []
        for keyword in keywords:
            query.append("Abstract:({})".format(keyword))
        query=" OR ".join(query)
        return self.search_raw(query)

    def _fromDoiToInternal(self,dois,search_name):
        items = self._optainDetails(dois)
        
        with open('results.txt',"w+") as f:
            json.dump(items,f)
        
        return self._convertACMDetails(items,search_name)
    

    def from_jsonDump(self,filename):
        with open(filename,"r") as f:
            items = json.load(f)
        return self._convertACMDetails(items,search_name="FROM DUMP")

    def _convertACMDetails(self,items,search_name="DEBUG"):
        converter = {
            'ARTICLE_JOURNAL':self._asJournal, 
            'PAPER_CONFERENCE':self._asPaper,
            'ARTICLE':self._asJournal,
        }

        search_results = []
        failed = []
        
        for item in items:
            try:
                item = self._unpack(item)
                if 'type' not in item:
                    print("don't know hat this is: {}".format(item))
                    continue
                if item['type'] in converter:
                    try:
                        search_results.append(converter[item['type']](item,search_name))
                    except Exception as e:
                        print("failed to add {} due to {}".format(item['id'],e))
                        failed.append(item)
                else:
                    print("failed to add {}".format(item['DOI']))
                    failed.append(item)
            except Exception as err:
                print("something went wrong, its my fault \_o_/. {}".format(err))
    
        with open('failed_bibs.txt',"w+") as f:
            json.dump(failed,f)

        return search_results


    def search_raw(self,query):
        search_name = "{}-{}".format(self.name(),hash(query)%10**8)
        
        results = self._searchDoisUsingSpyder(query,search_name)

        print("using {} we collected  {} dois, getting detailed information now...".format(query,len(results)))
        
        self._storeIntermediateResults('dois.txt',results,"w")

        return self._fromDoiToInternal(results,search_name)

    def _optainDetails(self,results):
        items = []
        for doi_chunk in chunks(results,100):
            doi_response = requests.post('https://dl.acm.org/action/exportCiteProcCitation',data={'targetFile':'custom-bibtex','format':'bibTex','dois':",".join(doi_chunk)}) 
            if doi_response.status_code == 200:
                data = json.loads(doi_response.content)
                #the bitTex are in the imtes
                items = items+data['items']
            else:
                print("could not collect dois, cause:",doi_response.status_code,doi_response.content)
                self._storeIntermediateResults('failed.txt',doi_chunk,"a+")
            time.sleep(5)
        
        return items



    def _storeIntermediateResults(self, filename,results,mode="w+"):
        with open(filename,mode) as f:
            f.write("\n".join(results))

    def _searchDoisUsingSpyder(self, query,name=""):
        process = CrawlerProcess()
        process.settings.set('DOWNLOAD_DELAY',  5, priority='cmdline')
        process.settings.set('COOKIES_DEBUG',  True, priority='cmdline')

        results=[]

        process.crawl(ACMSearchDOISpiderr,query=query,results=results,name=name)
        process.start()
        return results
    
    def _unpack(self,item):
        return list(item.items())[0][1]

    def _author(self,authors): 
        result = []
        for x in authors:
            if 'family' in x and 'given' in x:
                result.append("({},{})".format(x['family'],x['given']))
            elif 'family' in x:
                result.append("({},)".format(x['family']))
        return result
    
    def _asPaper(self,item,src):
        keywords = []
        if "keyword" in item:
            keywords = item['keyword'].split(',')
        return Publication.Paper(peer_reviewed=True,publisher="ACM",title=item['title'],num_pages=item['number-of-pages'],year=item['original-date']['date-parts'][0][0],country=item['event-place'],book_title=item['container-title'],series=item['collection-title'],doi=item['DOI'],keywords=keywords,authors=self._author(item['author']),source=src)
    
    def _asJournal(self,item,src):
        keywords = []
        if "keyword" in item:
            keywords = item['keyword'].split(',')
        return Publication.Journal(peer_reviewed=True,publisher="ACM",title=item['title'],source=src,year=item['original-date']['date-parts'][0][0],authors=self._author(item['author']),country=None,journal_name=item['container-title'],volume=item['volume'],num_pages=item['number-of-pages'],doi=item['DOI'],keywords=keywords)

    
# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]