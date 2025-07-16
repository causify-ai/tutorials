"""
Import as:

import ck_marketing.linkedin.linkedin_utils as cmliliut
"""

import logging
import re
import unicodedata
from typing import List, Tuple

import pandas as pd

import helpers.hdbg as hdbg
import helpers.hpandas as hpandas
import helpers.hprint as hprint

_LOG = logging.getLogger(__name__)


def filter_df(
    dataframe: pd.DataFrame, column: str, words: List[str], *, mode: str = "keep"
) -> pd.DataFrame:
    """
    Filter entries in a dataframe based on whether the specified column
    contains any of the words (case-insensitive).

    :param dataframe: input dataframe to be filtered.
    :param column: column name on which to apply the filter.
    :param words: words to search for within the specified column.
    :param mode: "keep" for retaining and "remove" for removing those
        rows
    :return: filtered dataframe.
    """
    regex_pattern = re.compile("|".join(map(re.escape, words)), re.IGNORECASE)
    initial_length = len(dataframe)
    if mode == "keep":
        filtered_df = dataframe[
            dataframe[column].apply(lambda x: bool(regex_pattern.search(x)))
        ]
        _LOG.info(
            "Filtered dataframe to keep rows where '%s' contains any of %s.",
            column,
            words,
        )
        _LOG.info("%d entries were kept", len(filtered_df))
        _LOG.warning("%d entries were removed", initial_length - len(filtered_df))
    elif mode == "remove":
        filtered_df = dataframe[
            ~dataframe[column].apply(lambda x: bool(regex_pattern.search(x)))
        ]
        _LOG.info(
            "Filtered dataframe to remove rows where '%s' contains any of %s",
            column,
            words,
        )
        _LOG.info("%d entries were removed", initial_length - len(filtered_df))
    else:
        raise ValueError("Invalid mode='%s'", mode)
    _LOG.info("Entries: %s", hprint.perc(initial_length, len(filtered_df)))
    return filtered_df


# #############################################################################


def _remove_titles(text: str) -> str:
    """
    Remove inline titles, commas, and periods at the end.

    E.g.,
    - Common titles (e.g., Dr., Mr., Prof.) and retain the next token.
      Example: "Dr. John" -> "John".
    - Titles at the end of the sentence
      Example: "John Smith, PhD." -> "John Smith".
    """
    # Remove common titles (e.g., Dr., Mr., Prof.) and retain the next token.
    # Example: "Dr. John" -> "John".
    text = re.sub(
        r"\b(?:Dr|Mr|Ms|Mrs|Prof|Rev|Sir|Dame|Jr)\.?\b(?:\s+|\.|$)+", "", text
    )
    # Remove inline titles, commas, and periods at the end.
    # Example: "John Smith, PhD." -> "John Smith".
    text = re.sub(r",.*$", "", text)
    return text


def _balance_unbalanced_symbols(text: str) -> str:
    """
    Fix unbalanced parentheses and quotes.
    """
    if text.startswith("(") and text.count("(") > text.count(")"):
        text += ")"
    elif text.startswith('"') and text.count('"') % 2 != 0:
        text += '"'
    elif "(" in text and text.count("(") > text.count(")"):
        text += ")"
    elif '"' in text and text.count('"') % 2 != 0:
        text += '"'
    return text


def _extract_nickname(text: str) -> Tuple[str, str]:
    """
    Extract a nickname from parenthetical/quoted content.

    return: text_without_nickname, nickname
    """
    pronouns = {
        "he/him",
        "she/her",
        "they/them",
        "he",
        "him",
        "she",
        "her",
        "they",
        "them",
        "he/him/his",
        "she/her/hers",
        "they/them/theirs",
        "he/himself",
        "she/herself",
        "they/themselves",
        "she/her/ella",
        "ceo",
    }
    nickname_match = re.search(r'\(([^)]+)\)|"([^"]+)"|\'([^\']+)\'', text)
    if nickname_match:
        nickname = (
            nickname_match.group(1)
            or nickname_match.group(2)
            or nickname_match.group(3)
        )
        # Normalize the nickname for comparison.
        nickname = nickname.strip()
        if nickname.lower() not in pronouns:
            # Keep valid nicknames.
            nickname = nickname.title() if len(nickname) > 2 else nickname
        else:
            # Remove pronouns.
            nickname = ""
    else:
        nickname = ""
    # Remove the parenthetical/quoted content entirely.
    # Check if the entire text is a pronoun.
    if text.lower().strip() in pronouns:
        text = ""
    else:
        text = re.sub(r'(\([^\)]+\)|"[^"]+"|\'[^\']+\')', "", text).strip()
    return text, nickname


def _normalize_casing(text: str) -> str:
    """
    Normalize casing for each word.

    Fix:
    - Title-case long words
    - Keep two-letter uppercase words (like "DJ")
    - Preserve hyphenation with correct casing (like "An-Yen").
    """
    words = text.split()
    normalized_words = []
    for w in words:
        # Check if the word has mixed casing (both uppercase and lowercase letters).
        is_mixed_case = any(c.islower() for c in w) and any(
            c.isupper() for c in w
        )
    for w in words:
        if "-" in w:
            # Preserve hyphenated subparts (e.g., "An-Yen")
            parts = w.split("-")
            parts = [p.capitalize() for p in parts if p]
            normalized_words.append("-".join(parts))
        elif "'" in w:
            # Preserve apostrophe subparts (e.g., "O'Connell").
            parts = w.split("'")
            parts = [
                (
                    p
                    if any(c.islower() for c in p) and any(c.isupper() for c in p)
                    else p.capitalize()
                )
                for p in parts
                if p
            ]
            normalized_words.append("'".join(parts))
        elif is_mixed_case:
            # Preserve the original casing for mixed-case words.
            normalized_words.append(w)
        else:
            # If exactly two uppercase letters, preserve them.
            # Else, capitalize the first letter.
            if len(w) == 2 and w.isupper():
                normalized_words.append(w)
            else:
                normalized_words.append(w.capitalize())
    text = " ".join(normalized_words)
    return text


def clean_first_last_name(name: str, is_last_name: bool) -> Tuple[str, str]:
    """
    Clean the first or last name.

    In the majority of the cases the nickname (E.g, Jimmy in 'James
    "Jimmy" Doe') can be a part of either the first name or the last
    name. Given the first name or the last name, return a tuple
    containing the cleaned first/last name and nickname present in
    quotes and parentheses.

    :param name: first or last name.
    :param is_last_name: True if the input is the last name, False if
        the input is the first name.
    :return: tuple containing the cleaned first name and nickname.
    """
    hdbg.dassert_isinstance(name, str)
    # Strip leading and trailing whitespace.
    text = name.strip()
    # Preserve initials if they are the entire name.
    # Example: "J.D." -> "J.D.".
    if is_last_name and re.match(r"^[A-Z](\.[A-Z]\.)?$", text):
        text = text.upper()
        nickname = ""
    else:
        # Normalize accents and diacritics.
        # Example: "José" -> "Jose".
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
        # Handle unbalanced symbols (parentheses).
        text = _balance_unbalanced_symbols(text)
        # Extract nicknames in quotes or parentheses, but exclude pronouns.
        text, nickname = _extract_nickname(text)
        # Remove titles and prefixes.
        text = _remove_titles(text)
        # Preserve hyphenated names.
        # Example: "John - Smith" -> "John-Smith"
        text = re.sub(r"\s+-\s+", "-", text)
        # Remove unwanted special characters and numerics.
        text = re.sub(r"[^\w\s'-]|\b\d+\b", "", text)
        if not is_last_name:
            # Handle removal or preservation of initials.
            # Preserve if the text is entirely initials (e.g., "D", "D J").
            if re.match(r"^[A-Z](\s[A-Z])?$", text.strip()):
                text = text.strip()
            else:
                # Remove trailing initials if part of a full name.
                # Example: "Smith J" -> "Smith".
                text = re.sub(r"\b[A-Z](?:\.[A-Z]\.|\.?\s*)(?![\'\-])$", "", text)
        # Normalize inconsistent casing for each word in the name.
        text = _normalize_casing(text)
    return text, nickname


def clean_and_track_name_changes(
    df: pd.DataFrame,
    *,
    first_name_col: str = "first_name",
    last_name_col: str = "last_name"
) -> pd.DataFrame:
    """
    Clean first and last names in a df and track if they were modified.

    :param df: input df with first and last names
    :param first_name_col: name of the column containing the first names
    :param last_name_col: name of the column containing the last names
    :return: df with
        - cleaned first and last names
        - column indicating if they were modified
    """
    # Validate input columns.
    hdbg.dassert_in(first_name_col, df.columns)
    hdbg.dassert_in(last_name_col, df.columns)
    # Ensure no NaN values to prevent issues with cleaning function.
    df_cleaned = df.copy()
    df_cleaned[[first_name_col, last_name_col]] = df_cleaned[
        [first_name_col, last_name_col]
    ].astype(str)
    # Clean first names and generate their aliases.
    df_cleaned[["cleaned_first_name", "first_alias"]] = df_cleaned.apply(
        lambda row: clean_first_last_name(
            row[first_name_col], is_last_name=False
        ),
        axis=1,
        result_type="expand",
    )
    # Clean last names and generate their aliases.
    df_cleaned[["cleaned_last_name", "second_alias"]] = df_cleaned.apply(
        lambda row: clean_first_last_name(row[last_name_col], is_last_name=True),
        axis=1,
        result_type="expand",
    )
    # Compute whether names were modified.
    df_cleaned["is_modified"] = (
        df_cleaned[first_name_col] != df_cleaned["cleaned_first_name"]
    ) | (df_cleaned[last_name_col] != df_cleaned["cleaned_last_name"])
    return df_cleaned


def _clean_full_name(name: str) -> str:
    """
    Clean up an individual name according to specific rules.

    :param name: name to be cleaned.
    :return: the cleaned name.

    Example Usage with DataFrame:
        ```
        df = pd.DataFrame({
            'Name': ['Dr. Peter parker ', 'ash ketchum', 'Mrs. Biden', 'Prof. GP p']
        })
        #Apply the _clean_first_last_name function to the 'Name' column.
        df['Name'] = df['Name'].apply(_clean_first_last_name)
        ```

    Cleaned names examples:
    - "JOHN DOE" -> "John Doe"
    - "  John Doe " -> "John Doe"
    - "Dr. John Smith" -> "John Smith"
    - "John (Johnny) Doe" -> "Johnny Doe"
    - "Amanda Townsend (she/her)" -> "Amanda Townsend"
    - "Aaref Hilaly (23829)" -> "Aaref Hilaly"
    - "J.D. Smith" -> "Smith"
    - "john SMITH" -> "John Smith", but "An-Yen Hu" -> "An-Yen Hu"
    - "John Smith (CEO)" -> "John Smith"
    - "J. Smith" -> "Smith"
    - "John "Smith"" -> "John Smith"
    - "John   Smith" -> "John Smith"
    - "J.D." -> "J.D."
    - "John (Johnny) Doe" -> "Johnny Doe"
    - "Samantha (Sam) Carter" -> "Sam Carter"
    - "William 'Billy' Brown" -> "Billy Brown"
    - "Anna \"Annie\" White" -> "Annie White"
    """
    hdbg.dassert_isinstance(name, str)
    # Strip leading and trailing whitespace.
    # Example: "  John Doe " -> "John Doe".
    text = name.strip()
    # Normalize case if the entire name is uppercase.
    # Example: "JOHN DOE" -> "John Doe".
    if text.isupper():
        text = text.title()
    # Normalize accents and diacritics.
    # Example: "José" -> "Jose".
    # text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Remove common titles (e.g., Dr., Mr., Prof.) and retain the next token.
    # Example: "Dr. John Smith" -> "John Smith".
    # Remove common titles (with or without space).
    text = re.sub(
        r"\b(?:mr|mrs|ms|mx|dr|prof|professor|rev|sir|dame|jr|sr|capt|col|lt|major|gen|rabbi|judge|justice|senator|rear admiral)\.?(?=\s|[A-Z])",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # Remove inline titles, commas, and periods at the end.
    # Example: "John Smith, PhD." -> "John Smith".
    text = re.sub(r",.*$", "", text)
    # Extract nicknames in quotes or parentheses, but exclude pronouns.
    # Example: "John (Johnny) Doe" -> "Johnny Doe",
    # but "Amanda Townsend (she/her)" -> "Amanda Townsend".
    text = re.sub(r"\(\d+\)", "", text).strip()

    def contains_pronoun_or_slash(content):
        words = content.lower().split("/")
        pronoun_keywords = {
            "he",
            "she",
            "they",
            "him",
            "her",
            "them",
            "his",
            "hers",
            "himself",
            "herself",
            "themselves",
        }
        return any(word.strip() in pronoun_keywords for word in words)

    # Search for nicknames in parentheses, single quotes, or double quotes.
    # Find all potential nicknames in parentheses, quotes, or single quotes
    nickname_matches = re.findall(r'\(([^)]+)\)|"([^"]+)"|\'([^\']+)\'', text)
    if nickname_matches:
        # Extract all found nicknames and remove empty matches
        nicknames = [
            match for group in nickname_matches for match in group if match
        ]
        # Use the first valid nickname (if any exist)
        if nicknames:
            nickname = nicknames[0].strip()
            if contains_pronoun_or_slash(nickname.lower()):
                # If it's a pronoun, remove the parenthetical/quoted content
                text = re.sub(
                    r'(\([^\)]+\)|"[^"]+"|\'[^\']+\')', "", text
                ).strip()
            else:
                # If it's a valid nickname, replace the full name with the nickname
                text = re.sub(
                    r'^(.*?)\s*(\([^\)]+\)|"[^"]+"|\'[^\']+\')', nickname, text
                )
    # Normalize inconsistent casing for each word in the name.
    # List of lowercase name particles.
    particles = {
        "de",
        "van",
        "van der",
        "von",
        "le",
        "du",
        "la",
        "da",
        "del",
        "della",
        "di",
        "des",
        "el",
        "mc",
        "mac",
    }
    words = text.split()
    text = " ".join(
        (
            "-".join(part.capitalize() for part in word.split("-"))
            if "-" in word
            else (
                word
                if (word.lower() in particles and i > 0)
                else word.capitalize()
            )
        )  # Keep lowercase for name particles
        for i, word in enumerate(words)
    )
    # Remove standalone single-letter initials (with or without a period).
    text = re.sub(r"\b([A-Z])\b(?=\s+[A-Z]\b)", "", text)
    # Remove unrelated parenthetical information.
    # Example: "John Smith (CEO)" -> "John Smith".
    text = re.sub(r"\([^\)]+\)", "", text)
    # Keep only the first and last name, remove middle names
    text = re.sub(r"^(\S+)\s+\S+\s+(\S+)$", r"\1 \2", text)
    # Preserve hyphenated names.
    # Example: "John - Smith" -> "John-Smith"
    text = re.sub(r"\s+-\s+", "-", text)
    # Example: "John@Smith" -> "John Smith".
    text = re.sub(r"[^\w\s'-]|_", "", text)
    # Preserve initials if they are the entire name.
    # Example: "John 123 Smith" -> "John Smith".
    text = re.sub(r"\b\d+\b", "", text)
    # Example: "John   Smith" -> "John Smith".
    text = re.sub(r"\s+", " ", text).strip()
    # Remove stray or mismatched quotes.
    # Example: "John "Smith"" -> "John Smith"
    text = re.sub(r'["]', "", text)
    return text


def get_debug_clean_name_df(df: pd.DataFrame) -> pd.DataFrame:
    col_names = [
        "first_name",
        "last_name",
        "cleaned_first_name",
        "first_alias",
        "cleaned_last_name",
        "second_alias",
        "is_modified",
    ]
    hdbg.dassert_is_subset(col_names, df.columns)
    return df[col_names]


def merge_clean_names_df(df: pd.DataFrame) -> pd.DataFrame:
    col_names = [
        "cleaned_first_name",
        "first_alias",
        "cleaned_last_name",
        "second_alias",
        "is_modified",
    ]
    hdbg.dassert_is_subset(col_names, df.columns)
    #
    df["first_name"] = df["cleaned_first_name"]
    df["last_name"] = df["cleaned_last_name"]
    #
    df.drop(columns=col_names, inplace=True)
    return df


def get_clean_name_stats(df: pd.DataFrame) -> pd.DataFrame:
    display(get_debug_clean_name_df(df).head(3))
    stats_df = {}
    stats_df["is_modified"] = hpandas.to_perc(df["is_modified"])
    stats_df["empty_first_name"] = hpandas.to_perc(df["cleaned_first_name"] == "")
    stats_df["empty_last_name"] = hpandas.to_perc(df["cleaned_last_name"] == "")
    stats_df["has_alias"] = hpandas.to_perc(
        (df["first_alias"] != "") | (df["second_alias"] != "")
    )
    stats_df = pd.Series(stats_df).to_frame()
    display(stats_df)


# #############################################################################


# TODO(gp): Obsolete
def filter_VCs(df: pd.DataFrame, title_col_name: str) -> pd.DataFrame:
    """
    Filter the dataframe for VCs based on the job title of the profile.

    :param df: entire data
    :param title_col_name: name of column that has titles.
    :return: two dfs with and without VCs with stats.
    """
    words = ["Partner", "VC", "invest", "Venture", "Director"]
    filtered_df_VC = filter_df(df, title_col_name, words, "keep")
    filtered_df_non_VC = filter_df(df, title_col_name, words, "remove")
    return filtered_df_VC, filtered_df_non_VC
