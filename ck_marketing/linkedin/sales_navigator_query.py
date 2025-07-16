"""
Import as:

import ck_marketing.linkedin.linkedin_utils as cmliliut
"""

import collections
import json
import logging
import re
import urllib.parse
from typing import Any, Dict

import helpers.hdbg as hdbg
import helpers.hprint as hprint

_LOG = logging.getLogger(__name__)

# LinkedIn filters from https://skylead.io/blog/linkedin-sales-navigator-filters

# #############################################################################
# Company
# #############################################################################

# - Current company
# (Typically not interesting)

# - Past company
# (Typically not interesting)

# - Company headcount
# https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/company-size-codes
company_size_map = {
    "A": "Self-employed",
    "B": "1-10",
    "C": "11-50",
    "D": "51-200",
    "E": "201-500",
    "F": "501-1000",
    "G": "1001-5000",
    "H": "5001-10,000",
    "I": "10,001+",
}

# - Company type
# Public company: a company whose stocks are available for purchase;
# Privately held: startup held by a few people;
# Non-profit: a company whose capital is on a positive zero;
# Educational institution: schools and universities;
# Partnership: business shared by multiple owners;
# Self-employed: company owner is the only employee of the company;
# Self-owned: individuals who run their own businesses;
# Government Agency: government entities.
company_type_map = {
    "A": "Self-Owned",
    "B": "Self-Employed",
    "C": "Public Company",
    "D": "Educational Institution",
    "E": "Government Agency",
    "F": "Nonprofit",
    "G": "Partnership",
    "H": "Privately Held",
    "I": "Sole Proprietorship",
}

# - Company headquarters location
# Oceania
# Asia
# Nordics
# MENA: the Middle East and Northern Africa
# EMEA: Europe, Middle East, and Africa
# Europe
# DACH: D - Deutschland, A - Austria, and CH - Switzerland
# Benelux: Belgium, the Netherlands, and Luxembourg.
# North America
# APJ: the Asia Pacific and Japan
# South America
# APAC: Asia - Pacific
# Africa
# TODO(gp): Update
location_map = {
    100506914: "Europe",
    102221843: "North America",
    103537801: "South America",
    104514572: "Asia",
    105193536: "Africa",
    106248663: "Australia",
    107644769: "Middle East",
    108100278: "Antarctica",
}

# #############################################################################
# Role
# #############################################################################

# - Function
# The company department in which the lead works.
# They don't seem to be officially documented.
# From https://booleanstrings.com/2024/02/06/sales-navigator-revelations-and-function-codes/
function_map = {
    k: v
    for k, v in enumerate(
        [
            "Accounting",
            "Administrative",
            "Arts and Design",
            "Business Development",
            "Community and Social Services",
            "Consulting",
            "Education",
            "Engineering",
            "Entrepreneurship",
            "Finance",
            "Healthcare Services",
            "Human Resources",
            "Information Technology",
            "Legal",
            "Marketing",
            "Media and Communication",
            "Military and Protective Services",
            "Operations",
            "Product Management",
            "Program and Project Management",
            "Purchasing",
            "Quality Assurance",
            "Real Estate",
            "Research",
            "Sales",
            "Customer Success and Support",
        ]
    )
}


# - Current job title
# TODO(gp): Maybe we need to use the API to get the info
# https://learn.microsoft.com/en-us/linkedin/shared/references/v2/standardized-data/titles
job_title_map = {
    1: "Chief Human Resources Officer (CHRO)",
    2: "Chief Marketing Officer (CMO)",
    3: "Chief Operating Officer (COO)",
    4: "Chief Strategy Officer (CSO)",
    5: "Chief Risk Officer (CRO)",
    6: "Chief Revenue Officer (CRO)",
    7: "Chief Information Officer (CIO)",
    8: "Chief Executive Officer (CEO)",
    9: "Chief Product Officer (CPO)",
    10: "Chief Technology Officer (CTO)",
    11: "Chief Data Officer (CDO)",
    12: "Chief Innovation Officer",
    13: "Chief Compliance Officer",
    14: "Chief Customer Officer",
    15: "Chief Experience Officer",
    16: "Chief Development Officer",
    17: "Chief Diversity Officer",
    18: "Chief Investment Officer",
    19: "Chief Legal Officer",
    20: "Chief Procurement Officer",
    21: "Chief Research Officer",
    22: "Chief Security Officer",
    23: "Chief Sustainability Officer",
    24: "Chief Transformation Officer",
    25: "President",
    26: "Vice President",
    27: "Senior Vice President",
    28: "Executive Vice President",
    29: "General Manager",
    30: "Managing Director",
    31: "Director",
    32: "Senior Director",
    33: "Head of Department",
    34: "Partner",
    35: "Owner",
    36: "Founder",
    37: "Co-Founder",
    38: "Principal",
    39: "Consultant",
    40: "Advisor",
    41: "Associate",
    42: "Analyst",
    43: "Engineer",
    44: "Developer",
    45: "Product Manager",
    46: "Project Manager",
    47: "Program Manager",
    48: "Marketing Manager",
    49: "Sales Manager",
    50: "Operations Manager",
    51: "Account Manager",
    52: "Business Development Manager",
    53: "Customer Success Manager",
    54: "Finance Manager",
    55: "HR Manager",
    56: "IT Manager",
    57: "Legal Manager",
    58: "Risk Manager",
    59: "Supply Chain Manager",
    60: "Strategy Manager",
    61: "Design Manager",
    62: "UX/UI Designer",
    63: "Graphic Designer",
    64: "Creative Director",
    65: "Art Director",
    66: "Copywriter",
    67: "Content Manager",
    68: "Chief Financial Officer (CFO)",
    69: "Researcher",
    70: "Scientist",
    71: "Doctor",
    72: "Nurse",
    73: "Professor",
    74: "Lecturer",
    75: "Teacher",
    76: "Coach",
    77: "Trainer",
    78: "Athlete",
    79: "Artist",
    80: "Musician",
    81: "Actor",
    82: "Writer",
    83: "Editor",
    84: "Journalist",
    85: "Photographer",
    86: "Filmmaker",
    87: "Producer",
    88: "Broadcaster",
    89: "Public Relations Specialist",
    90: "Event Manager",
    91: "Fundraiser",
    92: "Volunteer Coordinator",
    93: "Community Manager",
    94: "Government Official",
    95: "Politician",
    96: "Diplomat",
    97: "Military Officer",
    98: "Lawyer",
    99: "Judge",
    100: "Police Officer",
}


# - Past job title
# (Typically not interesting)


# - Seniority levels
# https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/seniority-codes
# TODO(gp): Double check
seniority_codes = {
    1: "Unpaid",
    2: "Training",
    3: "Entry-level",
    4: "Senior",
    5: "Manager",
    6: "Director",
    7: "Vice President (VP)",
    8: "Chief X Officer (CxO)",
    9: "Partner",
    10: "Owner",
}


# - Years in current company
# (Typically not interesting)
# 1 to 2 years
# 3 to 5 years
# 6 to 10 years
# More than 10 years


# - Years in current position
# (Typically not interesting)
# Same as above

# #############################################################################
# Personal
# #############################################################################

# - First name
# (Typically not interesting)

# - Last name
# (Typically not interesting)

# - Profile language
# (Typically not interesting)

# - Years of experience
# (Typically not interesting)

# - Geography

# - Postal code
# (Typically not interesting)

# - Groups
# (Typically not interesting)

# - Industry
# 413 industries
# https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/industry-codes-v2
# https://github.com/FernandoKGA/linkedin-industry-codes-v2/blob/main/linkedin_industry_code_v2_all_eng_with_header.csv
# See industry_code_v2.csv


def get_industry_code_map() -> Dict[int, str]:
    """
    Get the industry code map.

    ```
    {1: 'Defense and Space Manufacturing',
     10: 'Legal Services',
     100: 'Non-profit Organizations',
     1005: 'Household Appliance Manufacturing',
    ...
    ```
    """
    file_name = hgit.find_gile("industry_codes_v2.csv")
    df = pd.read_csv(file_name)
    #       label                               hierarchy                       description
    # id
    # 1     Defense and Space Manufacturing     Manufacturing > ...             This industry includes entities that manufactu...
    # 10    Legal Services                      Professional Services > ...     This industry includes entities that offer leg...
    # 100   Non-profit Organizations            Consumer Services > ...         This industry includes entities that provide p...
    df.set_index("id", inplace=True)
    industry_code_map = df["label"].to_dict()
    return industry_code_map


# #############################################################################
# Parse query.
# #############################################################################


# After the decoding the URL looks like:
# 'https://www.linkedin.com/sales/search/people?query=(
#   spellCorrectionEnabled:true,recentSearchParam:(id:4138396274,doLogHistory:true),
#   filters:List(
#       (type:CURRENT_TITLE,values:List(
#           (id:8,text:Chief%20Executive%20Officer,selectionType:INCLUDED),
#           (id:280,text:Chief%20Operating%20Officer,selectionType:INCLUDED),
#           (id:68,text:Chief%20Financial%20Officer,selectionType:INCLUDED),
#           (id:153,text:Chief%20Technology%20Officer,selectionType:INCLUDED),
#           (id:203,text:Chief%20Information%20Officer,selectionType:INCLUDED)))),
#       keywords:head%20of%20ai)
#       &sessionId=2qsWtelBS6yuOzkirzie/A==
#       &viewAllFilters=true'

# Everything after the `?query=` in the URL specifies the search parameters.
#
# # Query Parameters
# - spellCorrectionEnabled: whether LinkedIn will attempt to correct spelling
# mistakes in search queries.
# - recentSearchParam:(id:4138396274,doLogHistory:true)
#   - `id`  is a unique identifier for a previously performed search
#   - `doLogHistory`: indicates that LinkedIn will save this search in the
#     user's history.

# # Filters
# The filters parameter includes multiple constraints applied to refine the
# search results. Each filter consists of:
# - type: which aspect is being filtered
# - values: list of accepted values


def _cleanup(regex: str, decoded_query: str) -> str:
    _LOG.debug("\n%s", hprint.frame(hprint.to_str("regex")))
    _LOG.debug("    before: %s", decoded_query)
    decoded_query = re.sub(regex, "", decoded_query)
    _LOG.debug("    after:  %s", decoded_query)
    return decoded_query


def parse_query(query: str) -> Dict[str, Any]:
    """
    Parse the LinkedIn Sales Navigator query.

    :param query: URL query string.
    :return: Dictionary with the parsed query parameters.
    """
    hdbg.dassert_isinstance(query, str)
    out = {}
    # URL decode the query.
    decoded_query = urllib.parse.unquote(query)
    _LOG.debug(hprint.to_str("decoded_query"))
    # After the decoding, a URL looks like:
    # https://www.linkedin.com/sales/search/people?query=(
    #   spellCorrectionEnabled:true,recentSearchParam:(id:4138396274,doLogHistory:true),
    #   filters:List(
    #       (type:CURRENT_TITLE,values:List(
    #           (id:8,text:Chief%20Executive%20Officer,selectionType:INCLUDED),
    #           (id:280,text:Chief%20Operating%20Officer,selectionType:INCLUDED),
    #           (id:68,text:Chief%20Financial%20Officer,selectionType:INCLUDED),
    #           (id:153,text:Chief%20Technology%20Officer,selectionType:INCLUDED),
    #           (id:203,text:Chief%20Information%20Officer,selectionType:INCLUDED)))),
    #       keywords:head%20of%20ai)
    #       &sessionId=2qsWtelBS6yuOzkirzie/A==
    #       &viewAllFilters=true
    regex = r"https://www.linkedin.com/sales/search/people\?query=\("
    decoded_query = _cleanup(regex, decoded_query)
    # 1) Extract recent search param from the query.
    # spellCorrectionEnabled:true,
    regex = "spellCorrectionEnabled:(true|false),"
    query_match = re.search(regex, decoded_query)
    spell_correction_enabled = query_match.group(1) if query_match else ""
    out["spellCorrectionEnabled"] = spell_correction_enabled
    decoded_query = _cleanup(regex, decoded_query)
    # recentSearchParam:(id:4138396274,doLogHistory:true),
    # regex = r"recentSearchParam:(\(id:(\d+),)?doLogHistory:(true|false)\),"
    regex = r"recentSearchParam:\((?:id:(\d+),)?doLogHistory:(true|false)\)"
    query_match = re.search(regex, decoded_query)
    research_search_param = query_match.group(1) if query_match else ""
    do_log_history = query_match.group(2) if query_match else ""
    out["recentSearch"] = {
        "id": research_search_param,
        "doLogHistory": do_log_history,
    }
    decoded_query = _cleanup(regex, decoded_query)
    # 2) Extract filters from the query.
    # (type:CURRENT_TITLE,values:List(
    #     (id:8,text:Chief%20Executive%20Officer,selectionType:INCLUDED),
    #     (id:280,text:Chief%20Operating%20Officer,selectionType:INCLUDED),
    #     (id:68,text:Chief%20Financial%20Officer,selectionType:INCLUDED),
    #     (id:153,text:Chief%20Technology%20Officer,selectionType:INCLUDED),
    #     (id:203,text:Chief%20Information%20Officer,selectionType:INCLUDED)))),
    regex = r"type:(\w+),values:List\((.*?)\)\)"
    _LOG.debug("\n%s", hprint.frame(hprint.to_str("regex")))
    filter_matches = re.findall(regex, decoded_query)
    _LOG.debug(hprint.to_str("filter_matches"))
    decoded_query = _cleanup(regex, decoded_query)
    #
    regex = r"filters:List\(.*\),"
    decoded_query = _cleanup(regex, decoded_query)
    #
    filters = collections.defaultdict(list)
    _LOG.debug("\n%s", hprint.frame("Parsing filter_matches"))
    for filter_type, values in filter_matches:
        regex = r"\(id:(.*?),text:(.*?),selectionType:(\w+)\)?,?"
        value_matches = re.findall(regex, values)
        _LOG.debug(hprint.to_str("filter_type value_matches"))
        for value_id, text, selection_type in value_matches:
            _LOG.debug("  %s", hprint.to_str("value_id text selection_type"))
            text = urllib.parse.unquote(text)
            filters[filter_type].append(
                {"id": value_id, "text": text, "selectionType": selection_type}
            )
        values = re.sub(regex, "", values)
        hdbg.dassert_eq(values, "")
    out["filters"] = dict(filters)
    # 3) Parse keywords.
    regex = r"keywords:(.*)\)"
    keywords_match = re.search(regex, decoded_query)
    decoded_query = _cleanup(regex, decoded_query)
    keywords = keywords_match.group(1) if keywords_match else ""
    if keywords:
        keywords = urllib.parse.unquote(keywords)
    out["keywords"] = keywords
    # 4) Parse sessionId and viewAllFilters.
    #    ```
    #       &sessionId=2qsWtelBS6yuOzkirzie/A==
    #       &viewAllFilters=true
    #    ```
    regex = r"&sessionId=([^&]+)"
    session_id_match = re.search(regex, decoded_query)
    decoded_query = _cleanup(regex, decoded_query)
    session_id = session_id_match.group(1) if session_id_match else ""
    out["sessionId"] = session_id
    #
    regex = r"&viewAllFilters=(true|false)"
    view_all_filters_match = re.search(regex, decoded_query)
    decoded_query = _cleanup(regex, decoded_query)
    view_all_filters = (
        view_all_filters_match.group(1) if view_all_filters_match else ""
    )
    out["viewAllFilters"] = view_all_filters
    # # TODO(gp): We assume that the parsing is correct if the decoded query has
    # #  only parentheses left. We should consume those parentheses in the
    # #  parsing.
    # hdbg.dassert_eq(decoded_query.replace("(", "").replace(")", ""), "")
    return out


def query_to_str(parsed_query: Dict[str, Any], *, sort_keys: bool = False) -> str:
    """
    Convert the parsed query to a string.
    """
    hdbg.dassert_isinstance(parsed_query, dict)
    val = json.dumps(parsed_query, indent=2, sort_keys=sort_keys)
    return val


# #############################################################################
# Generate query.
# #############################################################################


def generate_query(parsed_query: Dict[str, Any]) -> str:
    """
    Generate the LinkedIn Sales Navigator query from the parsed query.

    This is the inverse operation of `parse_query()`.
    """
    spell_correction_enabled = parsed_query.get("spellCorrectionEnabled", "")
    if spell_correction_enabled:
        spell_correction_str = (
            f"spellCorrectionEnabled:{spell_correction_enabled}"
        )
    else:
        spell_correction_str = ""
    var_name = "spell_correction_str"
    _LOG.debug("before: %s", hprint.to_str(var_name))
    spell_correction_str = urllib.parse.quote(spell_correction_str, safe="=&()")
    _LOG.debug("after:  %s", hprint.to_str(var_name))
    # 1) Encode recent search param.
    recent_search = parsed_query.get("recentSearch", {})
    if recent_search:
        recent_search_param = []
        #
        recent_search_id = recent_search.get("id")
        if recent_search_id:
            recent_search_param.append(f"id:{recent_search_id}")
        #
        recent_search_do_log_history = recent_search.get("doLogHistory")
        if recent_search_do_log_history:
            recent_search_param.append(
                f"doLogHistory:{recent_search_do_log_history}"
            )
        recent_search_param = ",".join(recent_search_param)
        recent_search_str = f"recentSearchParam:({recent_search_param})"
    else:
        recent_search_str = ""
    var_name = "recent_search_str"
    _LOG.debug("before: %s", hprint.to_str(var_name))
    recent_search_str = urllib.parse.quote(recent_search_str, safe="=&()")
    _LOG.debug("after:  %s", hprint.to_str(var_name))
    # 2) Encode filters.
    filters = parsed_query.get("filters", {})
    filters_str = []
    for filter_type, values in filters.items():
        values_str = []
        for value in values:
            value_id = value["id"]
            value_text = urllib.parse.quote(value["text"])
            value_selection_type = value["selectionType"]
            value_str = f"id:{value_id},text:{value_text},selectionType:{value_selection_type}"
            values_str.append(f"({value_str})")
        filters_str.append(
            f"(type:{filter_type},values:List(" + ",".join(values_str) + "))"
        )
    filters_str = "filters:List(" + ",".join(filters_str) + ")"
    var_name = "filters_str"
    _LOG.debug("before: %s", hprint.to_str(var_name))
    filters_str = urllib.parse.quote(filters_str, safe="=&()")
    _LOG.debug("after:  %s", hprint.to_str(var_name))
    # 3) Encode keywords.
    keywords = parsed_query.get("keywords", "")
    if keywords:
        keywords_str = "keywords:" + urllib.parse.quote(keywords) + ")"
    else:
        keywords_str = ""
    var_name = "keywords_str"
    _LOG.debug("before: %s", hprint.to_str(var_name))
    keywords_str = urllib.parse.quote(keywords_str, safe="=&()")
    _LOG.debug("after:  %s", hprint.to_str(var_name))
    # 4) Encode sessionId.
    session_id = parsed_query.get("sessionId", "")
    if session_id:
        session_id_str = "&sessionId=" + urllib.parse.quote(session_id, safe="()")
    else:
        session_id_str = ""
    # 5) Encode viewAllFilters.
    view_all_filters = parsed_query.get("viewAllFilters", "")
    if view_all_filters:
        view_all_filters_str = "&viewAllFilters=" + view_all_filters
    else:
        view_all_filters_str = ""
    var_name = "view_all_filters_str"
    _LOG.debug("before: %s", hprint.to_str(var_name))
    view_all_filters_str = urllib.parse.quote(view_all_filters_str, safe="=&()")
    _LOG.debug("after:  %s", hprint.to_str(var_name))
    # Combine all parts.
    query_parts = [
        spell_correction_str,
        recent_search_str,
        filters_str,
        keywords_str,
    ]
    sep = urllib.parse.quote(",")
    query_str = "query=(" + sep.join(part for part in query_parts if part)
    # TODO(gp): For some tests there is an extra parenthesis is needed.
    if keywords_str == "":
        query_str += ")"
    query_str += session_id_str + view_all_filters_str
    #
    ret = "https://www.linkedin.com/sales/search/people?" + query_str
    return ret
