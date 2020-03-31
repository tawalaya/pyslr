import csv
import hashlib
import logging
import pandas as pd
from datetime import datetime

__all__ = ["Format","Publication"]

logger = logging.getLogger(__name__)




class Publication(object):

    def __init__(self,id=None, peer_reviewed=None, publisher=None, source=None, search_date=None, 
    title=None, year=None, authors=None, type=None, country=None, school=None, book_title=None, 
    series=None, num_pages=None, doi=None, journal_name=None, volume=None, keywords=None, 
    abstract=None, tried=None, references=None, isbn=None):
        self.id=id
        self.peer_reviewed=peer_reviewed
        self.publisher=publisher
        self.source=source
        self.search_date=search_date
        self.title=title
        self.year=year
        self.authors=authors
        self.type=type
        self.country=country
        self.school=school
        self.book_title=book_title
        self.series=series
        self.num_pages=num_pages
        self.doi=doi
        self.journal_name=journal_name
        self.volume=volume
        self.keywords=keywords
        self.abstract=abstract
        self.tried=tried
        self.references=references
        self.isbn=isbn
    
    def __ensure_not_none(s):
        if s is None:
            return ""
        return s

    def _reset(self):
        self.id = None
        self.peer_reviewed = None
        self.publisher = None
        self.source = None
        self.search_date = None
        self.title = None
        self.year = None
        self.authors = None
        self.type = None
        self.country = None
        self.school = None
        self.book_title = None
        self.series = None
        self.num_pages = None
        self.doi = None
        self.journal_name = None
        self.volume = None
        self.keywords = None
        self.abstract = None
        self.tried = None
        self.references = None
        self.isbn = None        
 
    @staticmethod
    def Paper(peer_reviewed,publisher,source,title,year,authors=[],
                country="",book_title="",series="",num_pages=None,doi=None,
                keywords=[],abstract=None,tried=None,references=None):
        """
            Builder method to create a paper publication
        """
        return Publication().fromPaper(peer_reviewed,publisher,source,title,year,
        authors,country,book_title,series,num_pages,doi,keywords,
        abstract,tried,references)  

    def fromPaper(self,peer_reviewed,publisher,source,title,year,authors=[],
                country="",book_title="",series="",num_pages=None,doi=None,
                keywords=[],abstract=None,tried=None,references=None):
        self._reset()
        self.id = Format.generate_id(title,authors,year,"inproceedings")
        self.peer_reviewed = peer_reviewed
        self.publisher = publisher
        self.source = source
        self.search_date = datetime.now()
        self.title = title
        self.year = year
        self.authors = authors
        self.type = "inproceedings"
        self.country = country
        self.book_title = book_title
        self.series = series
        self.num_pages = num_pages
        self.doi = doi
        self.keywords = keywords
        self.abstract = abstract
        self.tried = tried
        self.references = references
        return self

    @staticmethod
    def Journal(peer_reviewed,publisher,source,title,year,authors=[],
                country="",journal_name="",volume="",num_pages=None,doi=None,
                keywords=[],abstract=None,tried=None,references=None):
        """
            Builder method to create a journal publication
        """
        return Publication().fromJournal(peer_reviewed,publisher,source,title,year,
        authors,country,journal_name,volume,num_pages,doi,keywords,
        abstract,tried,references)
        
    def fromJournal(self,peer_reviewed,publisher,source,title,year,authors=[],
                country="",journal_name="",volume="",num_pages=None,doi=None,
                keywords=[],abstract=None,tried=None,references=None):
        self._reset()
        self.id = Format.generate_id(title,authors,year,"article")
        self.peer_reviewed = peer_reviewed
        self.publisher = publisher
        self.source = source
        self.search_date = datetime.now()
        self.title = title
        self.year = year
        self.authors = authors
        self.type = "article"
        self.country = country
        self.num_pages = num_pages
        self.doi = doi
        self.journal_name = journal_name
        self.volume = volume
        self.keywords = keywords
        self.abstract = abstract
        self.tried = tried
        self.references = references
        return self

    @staticmethod
    def Book(peer_reviewed,publisher,source,title,year,authors=[],
                num_pages=None,isbn=None,doi=None,references=None,tried=None):
        """
            Builder method to create a book publication
        """
        return Publication().fromBook(peer_reviewed,publisher,source,title,year,authors,
                num_pages,isbn,doi,references,tried)

    def fromBook(self,peer_reviewed,publisher,source,title,year,authors=[],
                num_pages=None,isbn=None,doi=None,references=None,tried=None):
        self._reset()
        self.id = Format.generate_id(title,authors,year,"book")
        self.peer_reviewed = peer_reviewed
        self.publisher = publisher
        self.source = source
        self.search_date = datetime.now()
        self.title = title
        self.year = year
        self.authors = authors
        self.type = "book"
        self.num_pages = num_pages
        self.doi = doi
        self.references = references
        self.tried = tried
        self.isbn = isbn
        return self

    @staticmethod
    def PHD(peer_reviewed,publisher,source,title,year,authors=[],
                country="",school=None,num_pages=None,doi=None,
                abstract=None,isbn=None,references=None,tried=None):
        """
            Build method for phd thesis publications
        """
        return Publication().fromPHD(peer_reviewed,publisher,source,title,year,authors[0],
                country,school,num_pages,doi,abstract,isbn,references,tried)

    def fromPHD(self,peer_reviewed,publisher,source,title,year,author=None,
                country="",school=None,num_pages=None,doi=None,
                abstract=None,isbn=None,references=None,tried=None):
        self._reset()
        self.id = Format.generate_id(title,[author],year,"phdthesis")
        self.peer_reviewed = peer_reviewed
        self.publisher = publisher
        self.source = source
        self.search_date = datetime.now()
        self.title = title
        self.year = year
        self.authors = [author]
        self.type = "phdthesis"
        self.country = country
        self.school = school
        self.num_pages = num_pages
        self.doi = doi
        self.abstract = abstract
        self.references = references
        self.isbn = isbn
        self.tried = tried
        return self

    def toWritableList(self):
        return list(map(Publication.__ensure_not_none,[
            self.id,
            self.peer_reviewed,
            self.publisher,
            self.source,
            None if self.search_date is None else Format.format_date(self.search_date),
            self.title,
            self.year,
            self.authors,
            self.type,
            self.country,
            self.school,
            self.book_title,
            self.series,
            self.num_pages,
            self.doi,
            self.journal_name,
            self.volume,
            self.keywords,
            self.abstract,
            self.tried,
            self.references,
            self.isbn
        ]))
    
    def fromList(args):
        pub = Publication(*args)
        pub.search_date = datetime.strptime(pub.search_date,"%Y-%m-%dT%H:%M")
        return pub


    def __str__(self):
        return str(self.toWritableList())


class Format():
    _version = "v1"
    _v1_header = ["id","peer_reviewed","publisher","source","search_date","title","year","authors","type","country","school","book_title","series","num_pages","doi","journal_name","volume","keywords","abstract","tried","references","isbn"]

    def __init__(self,writer=None):
        self.writer = writer
        super().__init__()

    def readAsPanda(self, fname):
        return pd.read_csv(fname,converters=
                    {"keywords": Format.csv_list_reader,
                     "authors":Format.author_list_reader,
                     "tried":Format.csv_list_reader,
                     "references":Format.csv_list_reader
                    })
    
    def readAsPublications(self,fname):
        reader = csv.reader(fname)

        return map(Publication.fromList,reader)

    @staticmethod
    def openWriter(file, writeHeader=True):
        return Format().openWriter(filename,writeHeader)

    def openWriter(self,file, writeHeader=True):
        writer =  csv.writer(file, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL,strict=True)
        if writeHeader:
            writer.writerow(self._v1_header)

        self.writer = writer

        return writer
    
    @staticmethod
    def format_date(date):
        return date.strftime("%Y-%m-%dT%H:%M")
    
    @staticmethod
    def generate_id(title,authros,year,publication_type):
        key = title+str(authros)+str(year)+publication_type

        return hashlib.sha1(key.encode('utf-8')).hexdigest()
    
    @staticmethod
    def writeRow(writer,publication):
        Format(writer).addRow(publication)

    def addRow(self,publication):
        self.writer.writerow(publication.toWritableList())

    @staticmethod
    def write(writer,publications=[]):
        Format(writer).writeAll(publications)

    def writeAll(self,writer,publications=[]):
        for publication in publications:
            self.writeRow(publication)

    @staticmethod
    def csv_list_reader(line):
        #remove [] and split by ,
        string_list = line.strip("[]").split(",")
        #remove the '' around each string and convert to list
        return list(map(lambda y:y.strip("''"),string_list))

    @staticmethod
    def author_list_reader(line):
        #remove [] and split by ','
        string_list = line.strip("[]").split("','")
        #clean up elements
        elements = map(lambda elem:elem.replace("'","").strip("()"),string_list)
        #split up author strings, and convert to tuple
        author_pairs = map(lambda authors:tuple(map(lambda q:q.strip(),authors.split(","))),elements)
        return list(author_pairs)
