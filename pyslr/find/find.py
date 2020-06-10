
from abc import ABCMeta,abstractmethod


class Finder(metaclass=ABCMeta):
    
    @abstractmethod
    def name(self,): raise NotImplementedError

    @abstractmethod
    def search_expression(self,experssion=None): raise NotImplementedError

    @abstractmethod
    def search(self,keywords=[]): raise NotImplementedError

    @abstractmethod
    def search_raw(self,query): raise NotImplementedError
