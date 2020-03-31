from pyslr.find import *
from pyslr.common import Format

class Search():
    def __init__(self,modules=[]):
        self.modules=modules
    
    def serach(self,output,keywords=[]):
        slr = Format()
        with open(output,"w") as out:
            writer = slr.openWriter(out)

            for module in self.modules:
                find = module()
                print("using {}".format(find.name()))

                results = find.search(keywords)

                for result in results:
                    slr.addRow(result)
        
        

