import scholarly
from pyslr.find import Finder
from pyslr.common import Format

class ScholarSearch(Finder):
    def name():
        return "Google Scholar"


    @abstractmethod
    def search(keywords=[]):
        results = scholarly.search_pubs_query("' '".join(keywords))
        for result in results:
            result


    @abstractmethod
    def search_raw(query): raise NotImplementedError
