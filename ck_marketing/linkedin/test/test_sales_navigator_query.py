import logging
import urllib.parse

import ck_marketing.linkedin.sales_navigator_query as cmlsnaqu
import helpers.hprint as hprint
import helpers.hunit_test as hunitest

_LOG = logging.getLogger(__name__)


# #############################################################################
# Query strings
# #############################################################################


def get_query1() -> str:
    # Current job title=
    #   Chief Executive Officer
    #   Chief Operating Officer
    #   Chief Financial Officer
    #   Chief Technology Officer
    #   Chief Information Officer
    # Search = "head of ai"
    url = "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2CrecentSearchParam%3A(id%3A4138396274%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A280%2Ctext%3AChief%2520Operating%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A68%2Ctext%3AChief%2520Financial%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A203%2Ctext%3AChief%2520Information%2520Officer%2CselectionType%3AINCLUDED))))%2Ckeywords%3Ahead%2520of%2520ai)&sessionId=2qsWtelBS6yuOzkirzie%2FA%3D%3D&viewAllFilters=true"
    return url


def get_query2() -> str:
    # Company headcount=
    #   51-200
    #   201-500
    #   501-1000
    #   1001-5000
    #   5001-10,000
    #   10,000+
    # Company type=
    #   Public Company
    #   Privately Held
    # Company headquarters location=
    #   North America
    #   Europe
    #   APAC
    # Current job title=
    #   Chief Executive Officer
    #   Chief Operating Officer
    #   Chief Financial Officer
    #   Chief Technology Officer
    #   Chief Information Officer
    # Seniority level=
    #   Owner / Partner
    #   CXO
    #   Strategic
    #   Vice President
    # Industry=
    #   IT Services and IT Consulting
    #   Defense and Space Manufacturing
    # Search= ""
    url = "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4138396274%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)%2C(id%3AF%2Ctext%3A501-1000%2CselectionType%3AINCLUDED)%2C(id%3AH%2Ctext%3A5001-10%252C000%2CselectionType%3AINCLUDED)%2C(id%3AI%2Ctext%3A10%252C000%252B%2CselectionType%3AINCLUDED)%2C(id%3AG%2Ctext%3A1001-5000%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_TYPE%2Cvalues%3AList((id%3AC%2Ctext%3APublic%2520Company%2CselectionType%3AINCLUDED)%2C(id%3AP%2Ctext%3APrivately%2520Held%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)%2C(id%3A100506914%2Ctext%3AEurope%2CselectionType%3AINCLUDED)%2C(id%3A91000003%2Ctext%3AAPAC%2CselectionType%3AINCLUDED)))%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A68%2Ctext%3AChief%2520Financial%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A280%2Ctext%3AChief%2520Operating%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)%2C(id%3A203%2Ctext%3AChief%2520Information%2520Officer%2CselectionType%3AINCLUDED)))%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A96%2Ctext%3AIT%2520Services%2520and%2520IT%2520Consulting%2CselectionType%3AINCLUDED)%2C(id%3A1%2Ctext%3ADefense%2520and%2520Space%2520Manufacturing%2CselectionType%3AINCLUDED)))%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A320%2Ctext%3AOwner%2520%252F%2520Partner%2CselectionType%3AINCLUDED)%2C(id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)%2C(id%3A130%2Ctext%3AStrategic%2CselectionType%3AINCLUDED)%2C(id%3A300%2Ctext%3AVice%2520President%2CselectionType%3AINCLUDED)))))&sessionId=cO1dlT77TyGG6mV52BO89Q%3D%3D&viewAllFilters=true"
    return url


def get_query3() -> str:
    # Company headcount=
    #   201-500
    #   501-1000
    #   1001-5000
    #   5001-10,000
    #   10,000+
    # Company type=
    #   Public Company
    #   Privately Held
    # Company headquarters location=
    #   North America
    # Geography
    #   North America
    # Industry=
    #   Business Intelligence Platforms
    # Search= ""
    url = "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4138396354%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)%2C(id%3AF%2Ctext%3A501-1000%2CselectionType%3AINCLUDED)%2C(id%3AG%2Ctext%3A1001-5000%2CselectionType%3AINCLUDED)%2C(id%3AH%2Ctext%3A5001-10%252C000%2CselectionType%3AINCLUDED)%2C(id%3AI%2Ctext%3A10%252C000%252B%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)))%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A3128%2Ctext%3ABusiness%2520Intelligence%2520Platforms%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_TYPE%2Cvalues%3AList((id%3AC%2Ctext%3APublic%2520Company%2CselectionType%3AINCLUDED)%2C(id%3AP%2Ctext%3APrivately%2520Held%2CselectionType%3AINCLUDED)))%2C(type%3AREGION%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)))))&sessionId=7OpRz2epQze4HB5ucmW0Rw%3D%3D&viewAllFilters=true"
    return url


def get_query4() -> str:
    # Company headquarters location=
    #   North America
    url = "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(doLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)))))&sessionId=th7%2BY%2FDPRvG8xy7yZJm%2Fmw%3D%3D&viewAllFilters=true"
    return url


def get_query5() -> str:
    # Function =
    #   Accounting
    url = "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(doLogHistory%3Atrue)%2Cfilters%3AList((type%3AFUNCTION%2Cvalues%3AList((id%3A1%2Ctext%3AAccounting%2CselectionType%3AINCLUDED)))))&sessionId=HFB%2FLUZ6SZSSfZmY4HrCjg%3D%3D&viewAllFilters=true"
    return url


# #############################################################################
# Test_parse_query1
# #############################################################################


class Test_parse_query1(hunitest.TestCase):

    def helper(self, query: str, exp: str) -> None:
        # Run tests.
        parsed_query = cmlsnaqu.parse_query(query)
        # Check output.
        act = cmlsnaqu.query_to_str(parsed_query, sort_keys=True)
        self.assert_equal(act, exp, dedent=True)

    def test1(self) -> None:
        query = get_query1()
        exp = r"""
        {
          "filters": {
            "CURRENT_TITLE": [
              {
                "id": "8",
                "selectionType": "INCLUDED",
                "text": "Chief Executive Officer"
              },
              {
                "id": "280",
                "selectionType": "INCLUDED",
                "text": "Chief Operating Officer"
              },
              {
                "id": "68",
                "selectionType": "INCLUDED",
                "text": "Chief Financial Officer"
              },
              {
                "id": "153",
                "selectionType": "INCLUDED",
                "text": "Chief Technology Officer"
              },
              {
                "id": "203",
                "selectionType": "INCLUDED",
                "text": "Chief Information Officer"
              }
            ]
          },
          "keywords": "head of ai",
          "recentSearch": {
            "doLogHistory": "true",
            "id": "4138396274"
          },
          "sessionId": "2qsWtelBS6yuOzkirzie/A==",
          "spellCorrectionEnabled": "true",
          "viewAllFilters": "true"
        }
        """
        self.helper(query, exp)

    def test2(self) -> None:
        query = get_query2()
        exp = r"""
        {
          "filters": {
            "COMPANY_HEADCOUNT": [
              {
                "id": "D",
                "selectionType": "INCLUDED",
                "text": "51-200"
              },
              {
                "id": "E",
                "selectionType": "INCLUDED",
                "text": "201-500"
              },
              {
                "id": "F",
                "selectionType": "INCLUDED",
                "text": "501-1000"
              },
              {
                "id": "H",
                "selectionType": "INCLUDED",
                "text": "5001-10,000"
              },
              {
                "id": "I",
                "selectionType": "INCLUDED",
                "text": "10,000+"
              },
              {
                "id": "G",
                "selectionType": "INCLUDED",
                "text": "1001-5000"
              }
            ],
            "COMPANY_HEADQUARTERS": [
              {
                "id": "102221843",
                "selectionType": "INCLUDED",
                "text": "North America"
              },
              {
                "id": "100506914",
                "selectionType": "INCLUDED",
                "text": "Europe"
              },
              {
                "id": "91000003",
                "selectionType": "INCLUDED",
                "text": "APAC"
              }
            ],
            "COMPANY_TYPE": [
              {
                "id": "C",
                "selectionType": "INCLUDED",
                "text": "Public Company"
              },
              {
                "id": "P",
                "selectionType": "INCLUDED",
                "text": "Privately Held"
              }
            ],
            "CURRENT_TITLE": [
              {
                "id": "8",
                "selectionType": "INCLUDED",
                "text": "Chief Executive Officer"
              },
              {
                "id": "68",
                "selectionType": "INCLUDED",
                "text": "Chief Financial Officer"
              },
              {
                "id": "280",
                "selectionType": "INCLUDED",
                "text": "Chief Operating Officer"
              },
              {
                "id": "153",
                "selectionType": "INCLUDED",
                "text": "Chief Technology Officer"
              },
              {
                "id": "203",
                "selectionType": "INCLUDED",
                "text": "Chief Information Officer"
              }
            ],
            "INDUSTRY": [
              {
                "id": "96",
                "selectionType": "INCLUDED",
                "text": "IT Services and IT Consulting"
              },
              {
                "id": "1",
                "selectionType": "INCLUDED",
                "text": "Defense and Space Manufacturing"
              }
            ],
            "SENIORITY_LEVEL": [
              {
                "id": "320",
                "selectionType": "INCLUDED",
                "text": "Owner / Partner"
              },
              {
                "id": "310",
                "selectionType": "INCLUDED",
                "text": "CXO"
              },
              {
                "id": "130",
                "selectionType": "INCLUDED",
                "text": "Strategic"
              },
              {
                "id": "300",
                "selectionType": "INCLUDED",
                "text": "Vice President"
              }
            ]
          },
          "keywords": "",
          "recentSearch": {
            "doLogHistory": "true",
            "id": "4138396274"
          },
          "sessionId": "cO1dlT77TyGG6mV52BO89Q==",
          "spellCorrectionEnabled": "",
          "viewAllFilters": "true"
        }
        """
        self.helper(query, exp)

    def test3(self) -> None:
        query = get_query3()
        exp = r"""
        {
          "filters": {
            "COMPANY_HEADCOUNT": [
              {
                "id": "E",
                "selectionType": "INCLUDED",
                "text": "201-500"
              },
              {
                "id": "F",
                "selectionType": "INCLUDED",
                "text": "501-1000"
              },
              {
                "id": "G",
                "selectionType": "INCLUDED",
                "text": "1001-5000"
              },
              {
                "id": "H",
                "selectionType": "INCLUDED",
                "text": "5001-10,000"
              },
              {
                "id": "I",
                "selectionType": "INCLUDED",
                "text": "10,000+"
              }
            ],
            "COMPANY_HEADQUARTERS": [
              {
                "id": "102221843",
                "selectionType": "INCLUDED",
                "text": "North America"
              }
            ],
            "COMPANY_TYPE": [
              {
                "id": "C",
                "selectionType": "INCLUDED",
                "text": "Public Company"
              },
              {
                "id": "P",
                "selectionType": "INCLUDED",
                "text": "Privately Held"
              }
            ],
            "INDUSTRY": [
              {
                "id": "3128",
                "selectionType": "INCLUDED",
                "text": "Business Intelligence Platforms"
              }
            ],
            "REGION": [
              {
                "id": "102221843",
                "selectionType": "INCLUDED",
                "text": "North America"
              }
            ]
          },
          "keywords": "",
          "recentSearch": {
            "doLogHistory": "true",
            "id": "4138396354"
          },
          "sessionId": "7OpRz2epQze4HB5ucmW0Rw==",
          "spellCorrectionEnabled": "",
          "viewAllFilters": "true"
        }
        """
        self.helper(query, exp)

    def test4(self) -> None:
        query = get_query4()
        exp = r"""
        {
          "filters": {
            "COMPANY_HEADQUARTERS": [
              {
                "id": "102221843",
                "selectionType": "INCLUDED",
                "text": "North America"
              }
            ]
          },
          "keywords": "",
          "recentSearch": {
            "doLogHistory": "true",
            "id": null
          },
          "sessionId": "th7+Y/DPRvG8xy7yZJm/mw==",
          "spellCorrectionEnabled": "",
          "viewAllFilters": "true"
        }
        """
        self.helper(query, exp)

    def test5(self) -> None:
        query = get_query5()
        exp = r"""
        {
          "filters": {
            "FUNCTION": [
              {
                "id": "1",
                "selectionType": "INCLUDED",
                "text": "Accounting"
              }
            ]
          },
          "keywords": "",
          "recentSearch": {
            "doLogHistory": "true",
            "id": null
          },
          "sessionId": "HFB/LUZ6SZSSfZmY4HrCjg==",
          "spellCorrectionEnabled": "",
          "viewAllFilters": "true"
        }
        """
        self.helper(query, exp)


# #############################################################################
# Test_parse_query2
# #############################################################################


class Test_parse_query2(hunitest.TestCase):

    def helper(self, query: str, mode: str) -> None:
        # Run tests.
        parsed_query = cmlsnaqu.parse_query(query)
        query_out = cmlsnaqu.generate_query(parsed_query)
        _LOG.debug(hprint.to_str("query_out"))
        _LOG.debug(hprint.to_str("query"))
        # Check output.
        # We remove the encoding of the URL, since there can be some differences
        # due to the encoding of the URL, e.g.,
        # ORITY_LEVEL%2Cvalues%3AList((id%3A320%2Ctext%3AOwner%2520%2F%2520Partn
        # ORITY_LEVEL%2Cvalues%3AList((id%3A320%2Ctext%3AOwner%2520%252F%2520Par
        # so
        for _ in range(2):
            query_out = urllib.parse.unquote(query_out)
            query = urllib.parse.unquote(query)
        if mode == "assert_equal":
            self.assert_equal(query_out, query, split_max_len=70)
        elif mode == "check_string":
            txt = f"act={query_out}\nexp={query}"
            self.check_string(txt)
        else:
            raise ValueError(f"Invalid mode={mode}")

    def test1(self) -> None:
        query = get_query1()
        self.helper(query, "assert_equal")

    def test2(self) -> None:
        query = get_query2()
        self.helper(query, "assert_equal")

    def test3(self) -> None:
        query = get_query3()
        self.helper(query, "assert_equal")

    def test4(self) -> None:
        query = get_query4()
        self.helper(query, "assert_equal")

    def test5(self) -> None:
        query = get_query5()
        self.helper(query, "assert_equal")
