from pyslr.importer import BibImporter
from pyslr.common import Format
import logging

if __name__ == "__main__":
    import sys
    print("pyslr")
    logging.basicConfig(level=logging.DEBUG)

    args = sys.argv[1:]
    bibfile = args[0]
    output = args[1]
    slr = Format()
    with open(output,"w") as out:
        writer = slr.openWriter(out)

        bibin = BibImporter()

        bibin.parse_and_write(bibfile,slr)