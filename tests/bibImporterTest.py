import unittest

import os
import csv
from io import StringIO
from pyslr import BibImporter,Format


bibFile = r"""
    @inproceedings{2018-Back-ESOCC-FaasBenchmarking,
        author     = "{B}ack, {T}imon and {A}ndrikopoulos, {V}asilios",
        title      = "{U}sing a {M}icrobenchmark to {C}ompare {F}unction as a {S}ervice {S}olutions",
        booktitle  = "{P}roceedings of the 7th {E}uropean {C}onference on {S}ervice-{O}riented and {C}loud {C}omputing",
        series     = "{ESOCC}'18",
        year       = "2018",
        month      = "{A}ug",
        isbn       = "978-3-319-99819-0",
        location   = "{C}omo, {I}taly",
        pages      = "146--160",
        numpages   = "15",
        doi        = "https://doi.org/10.1007/978-3-319-99819-0_11",
        editor     = "{K}ritikos, {K}yriakos and {P}lebani, {P}ierluigi  and de {P}aoli, {F}lavio",
        publisher  = "{S}pringer {I}nternational {P}ublishing",
        address    = "{C}ham"
    }

    @article{2019-Hellerstein-CoRR-ServerlessComputing,
        author    = "{J}oseph {M}. {H}ellerstein and
                    {J}ose {M}. {F}aleiro and
                    {J}oseph {E}. {G}onzalez and
                    {J}ohann {S}chleier{-}{S}mith and
                    {V}ikram {S}reekanti and
                    {A}lexey {T}umanov and
                    {C}henggang {W}u",
        title     = "{S}erverless {C}omputing: {O}ne {S}tep {F}orward, {T}wo {S}teps {B}ack",
        journal   = "{C}o{RR}",
        volume    = {abs/1812.03651},
        year      = "2018",
        month     = "{J}an",
        day       = "01",
        pages     = "1-8",
        numpages  = "8",
        publisher = "arXiv",
        url       = {http://arxiv.org/abs/1812.03651}
    }

    @phdthesis{2018-Klems-Phd-ExperimentDrivenEvaluation,
        author    = "Klems, Markus",
        title     = "Experiment-driven Evaluation of Cloud-based Distributed Systems",
        school    = "TU Berlin",
        year      = "2016"
    }


    %%% Books
    @book{2017-Bermbach-Book-CloudServiceBenchmarking,
        author    = "Bermbach, David and Wittern, Erik and Tai, Stefan",
        title     = "Cloud Service Benchmarking: Measuring Quality of Cloud Services from a Client Perspective",
        year      = "2017",
        publisher = "Springer International Publishing",
        address   = "Cham",
        isbn      = "978-3-319-55482-2"
    }

"""


class BibImporterTest(unittest.TestCase):


    def test_upper(self):
        output = StringIO()
        writer = csv.writer(output, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL,strict=True)

        fmt = Format(writer)

        bib = BibImporter()
        bib.parse_and_write(StringIO(bibFile),fmt)

        assert(len(output.getvalue()) > 0)

        publications = fmt.readAsPublications(StringIO(output.getvalue()))

        types = list(map(lambda x:x.type,publications))

        assert("book" in types)
        assert("article" in types)
        assert("inproceedings" in types)
        assert("phdthesis" in types)

       

if __name__ == '__main__':
    unittest.main()