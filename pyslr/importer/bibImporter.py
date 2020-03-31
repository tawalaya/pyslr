import logging
from datetime import datetime
import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text
from pyslr.common import Format,Publication


logger = logging.getLogger(__name__)

__all__ = ["BibImporter"]

class BibImporter():

    def __init__(self):
        super().__init__()
        self.inproceedingsTypes = ["inproceedings"]
        self.articleTypes = ["article"]
        self.thesisTypes = ["phdthesis"]
        self.bookTypes = ["book"]
        self.validTypes = self.inproceedingsTypes+self.articleTypes+self.thesisTypes+self.bookTypes


    def open_file(self,filename):
        return open(filename,"r")

    def parse_and_write(self,reader,writer):

        with reader as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        inproceedings = filter(lambda x:x["ENTRYTYPE"] in self.inproceedingsTypes,bib_database.entries)
        
        ignored = filter(lambda x:x["ENTRYTYPE"] not in self.validTypes,bib_database.entries)

        for i in ignored:
            logger.warning("ignoring %s because of unknown type (%s)",i["ID"],i["ENTRYTYPE"])

        for inp in inproceedings:
            tried = ["id","peer_reviewed","publisher","title","year","authors","type","country","num_pages"]
            pub = Publication.Paper(
                        peer_reviewed=1,
                        publisher=self.get("publisher",inp,default="unknown"),
                        source="bib_import_v1",
                        title=self._get("title",inp,True),
                        year=self._get("year",inp,True),
                        authors=self.authors(inp),
                        country=self.read_country(inp),
                        book_title=self.get("booktitle",inp,default=None,tried=tried),
                        series=self.get("series",inp,default=None,tried=tried),
                        num_pages=self.pages(inp),
                        doi=self.optional("doi",inp,tried=tried),
                        keywords=self.keywords(inp,log_error=False),
                        abstract=None,
                        tried=tried,
                        references=None)
            writer.addRow(pub)
        
        article = filter(lambda x:x["ENTRYTYPE"]in self.articleTypes,bib_database.entries)

        for inp in article:
            tried = ["id","peer_reviewed","publisher","title","year","authors","type","num_pages"]
            pub = Publication.Journal(
                peer_reviewed=1,
                publisher=self.get("publisher",inp,default="unknown"),
                source='bib_import_v1',
                title=self._get("title",inp,True),
                year=self._get("year",inp,True),
                authors=self.authors(inp),
                country=self.read_country(inp,log_error=False),
                journal_name=self.get("journal",inp,default=None,tried=tried),
                volume=self.get("volume",inp,default=None,tried=tried),
                num_pages=self.pages(inp),
                doi=self.get("doi",inp,default=None,tried=tried),
                keywords=self.keywords(inp,log_error=False),
                abstract=None,
                tried=tried,
                references=None
            )
            writer.addRow(pub)
        
        
        thesis = filter(lambda x:x["ENTRYTYPE"]in self.thesisTypes,bib_database.entries)

        for inp in thesis:
            tried = ["id","peer_reviewed","publisher","title","year","authors","type",]
            pub = Publication.PHD(
                peer_reviewed=1,
                publisher=self.get("publisher",inp,default="unknown",log_error=False),
                source='bib_import_v1',
                title=self._get("title",inp,True),
                year=self._get("year",inp,True),
                authors=self.authors(inp),
                country=self.read_country(inp,log_error=False),
                school=self._get("school",inp,True),
                num_pages=self.pages(inp,log_error=False),
                doi=self.optional("doi",inp,tried=tried),
                abstract=None,
                isbn=self.optional("isbn",inp,tried=tried),
                references=None,
                tried=tried
            )
            writer.addRow(pub)

        
        book = filter(lambda x:x["ENTRYTYPE"] in self.bookTypes,bib_database.entries)

        for inp in book:
            tried = ["id","peer_reviewed","publisher","title","year","authors","type",]
            pub = Publication.Book(
                peer_reviewed=1,
                publisher=self.get("publisher",inp,default="unknown"),
                source='bib_import_v1',
                title=self._get("title",inp,True),
                year=self._get("year",inp,True),
                authors=self.authors(inp),
                num_pages=self.pages(inp,log_error=False),
                doi=self.optional("doi",inp,tried=tried),
                isbn=self.get("isbn",inp,default=None,tried=tried),
                references=None,
                tried=tried
            )
            
            writer.addRow(pub)


    def _get(self,key,bibentry,compile_latex):
        if key in bibentry:
            value =  bibentry[key]
            if compile_latex:
                return LatexNodes2Text().latex_to_text(value)
            return value
        else:
            raise KeyError(key)

    def get(self,key,bibentry,compile_latex=True,default="",tried=[],log_error=True):
        value = default
        tried.append(key)
        try:
            value = self._get(key,bibentry,compile_latex)
            return value
        except KeyError:
            if log_error:
                logger.warning("%s missing in %s",key,bibentry["ID"])
            return default

    def optional(self,key,bibentry,compile_latex=True,tried=[]):
        return self.get(key,bibentry,compile_latex,None,tried,False)
        

    def authors(self,bibentry,compile_latex=True):
        value = self._get("author",bibentry,compile_latex)

        return list(map(lambda x:"(%s)"%x.strip(),value.split("and")))

    def pages(self,bibentry,compile_latex=True,log_error=True):
        value = None
        if "numpages" in bibentry:
            value = bibentry["numpages"]

        #try to parese xx-yy format of pages and calulate them
        if "pages" in bibentry and value == "":
            value = bibentry["pages"]
            if "-" in value:
                pages = value.split("-")
                #remove empty cells due to (--)
                pages = list(filter(lambda x:len(x) > 0,pages))
                try:
                    value = str(int(pages[1])-int(pages[0]))
                except ValueError:
                    if log_error:
                        logger.warning("could not deterine pages of %s found only %s",bibentry["ID"],pages)

        return value

    def read_country(self,bibentry,compile_latex=True,log_error=True):
        try:
            value = self._get("address",bibentry,compile_latex)
            if "," in value:
                return value.split(",")[-1]
            else:
                return value
        except KeyError:
            if log_error:
                logger.warning("address missing in %s",bibentry["ID"])
            return None

    def keywords(self,bibentry,compile_latex=True,log_error=True):
        try:
            value = self._get("keywords",bibentry,compile_latex)
            return list(map(lambda x:"%s"%x.strip(),value.split(",")))
        except KeyError:
            if log_error:
                logger.warning("keywords missing in %s",bibentry["ID"])
            return None
