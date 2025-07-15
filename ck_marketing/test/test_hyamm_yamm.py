import os
import unittest.mock

import pandas as pd

import ck_marketing.process_automation.hyamm as cmprauhy
import helpers.hunit_test as hunitest

# #############################################################################

# - When `use_mock_data = False`, functions will read
#   real data (will require Gsheet API and access).
# - When `use_mock_data True` (default), the functions will
#   call mock data, thus removing API dependancy.

use_mock_data = True

# #############################################################################


def _load_mock_data(
    test_instance: hunitest.TestCase, file_name: str
) -> pd.DataFrame:
    """
    Load and clean mock data from a CSV file.
    """
    dir_name = test_instance.get_input_dir()
    test_csv_path = os.path.join(dir_name, file_name)
    mock_data = pd.read_csv(test_csv_path)
    # Pandas puts "nan" for empty values which causes string mismatch.
    return mock_data.fillna("").astype(str)


def _run_test(
    test_instance: hunitest.TestCase,
    function_name: str,
    input_file_name: str,
    normalize: bool,
) -> pd.DataFrame:
    """
    Reusable function to run scraping functions.
    """
    if use_mock_data:
        mock_data = _load_mock_data(test_instance, input_file_name)
        with unittest.mock.patch(
            "ck_marketing.process_automation.hyamm.get_cached_sheet_to_df"
        ) as mock_func:
            mock_func.side_effect = lambda *args, **kwargs: mock_data.copy()
            df_out = getattr(cmprauhy, function_name)(normalize=normalize)
            df_out = df_out[:1]
    else:
        df_out = getattr(cmprauhy, function_name)(normalize=normalize)
        df_out = df_out[:1]
    return df_out


# #############################################################################
# Test_update_contact_df_with_yamm_df
# #############################################################################


class Test_update_contact_df_with_yamm_df(hunitest.TestCase):
    """
    Test different yamm processing functions from 'hyamm'.
    """

    def test1(self) -> None:
        """
        Test updating `contact_df` with `yamm_df`, covering edge cases.
        """
        # Prepare Inputs.
        yamm_df = _load_mock_data(self, "test1.csv")
        contact_df = _load_mock_data(self, "test2.csv")
        # Call function to test.
        updated_df = cmprauhy.update_contact_df_with_yamm_df(contact_df, yamm_df)
        exp = r"""
        hash        name     Campaign_1     Campaign_2     Campaign_3
        abc123     Alice           Sent        Clicked
        def456       Bob
        ghi789   Charlie         Opened
        """
        act = updated_df.to_csv(index=False, sep=" ")
        # Comparing strings.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test2(self) -> None:
        """
        Test behavior when `yamm_df` contains no matching keys.
        """
        # Prepare Inputs.
        contact_df = _load_mock_data(self, "test1.csv")
        yamm_df_no_match = _load_mock_data(self, "test2.csv")
        # Call function to test.
        updated_no_match = cmprauhy.update_contact_df_with_yamm_df(
            contact_df, yamm_df_no_match
        )
        exp = r"""
          hash     name   Campaign_1
        abc123    Alice
        def456      Bob
        """
        act = updated_no_match.to_csv(index=False, sep=" ")
        # Comparing strings.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test3(self) -> None:
        """
        Test behavior when `yamm_df` is empty.
        """
        # Prepare Inputs.
        contact_df = _load_mock_data(self, "test1.csv")
        yamm_df_empty = _load_mock_data(self, "test2.csv")
        # Call function to test.
        updated_empty = cmprauhy.update_contact_df_with_yamm_df(
            contact_df, yamm_df_empty
        )
        exp = r"""
          hash     name
        abc123    Alice
        def456      Bob
        """
        act = updated_empty.to_csv(index=False, sep=" ")
        # Comparing strings.
        self.assert_equal(act, exp, fuzzy_match=True)


# #############################################################################
# Test_select_campaign
# #############################################################################


class Test_select_campaign(hunitest.TestCase):
    """
    Test `select_campaign` function from `hyamm.py`.
    """

    def test1(self) -> None:
        """
        Test selecting a subset of contacts for a campaign.
        """
        # Prepare inputs
        contact_df = _load_mock_data(self, "test.csv")
        campaign_col = "campaign_1"
        # Call function to test.
        selected_df, updated_contact_df = cmprauhy.select_campaign(
            contact_df, campaign_col, type_="email", num_rows=2, seed=42
        )
        exp = r"""
        hash    first_name  last_name  company_name           email   email_verification
        abc123       Alice      Smith      TechCorp  alice@mail.com                valid
        jkl012       David     Miller    HealthPlus  david@mail.com            all_valid
        """
        act = selected_df.to_csv(index=False, sep=" ")
        # Check Outputs.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test2(self) -> None:
        """
        Test updated contact_df after selecting the campaign.
        """
        # Prepare inputs
        contact_df = _load_mock_data(self, "test.csv")
        campaign_col = "campaign_1"
        # Call function to test.
        selected_df, updated_contact_df = cmprauhy.select_campaign(
            contact_df, campaign_col, type_="email", num_rows=2, seed=42
        )
        exp = r"""
        hash     first_name last_name   email             email_verification    linkedin_url         company_name    campaign_1
        abc123   Alice      Smith       alice@mail.com    valid                                          TechCorp    selected
        def456   Bob        Johnson                                             linkedin.com/bob           BizInc
        ghi789   Charlie    Brown       charlie@mail.com  invalid                                         FinTech
        jkl012   David      Miller      david@mail.com    all_valid                                    HealthPlus    selected
        mno345   Eve        Davis                                               linkedin.com/eve         EduWorld
        """

        act = updated_contact_df.to_csv(index=False, sep=" ")
        # Check Outputs.
        self.assert_equal(act, exp, fuzzy_match=True)


# #############################################################################
# Test_get_yamm_results
# #############################################################################


class Test_get_yamm_results(hunitest.TestCase):
    """
    Test `get_yamm_results` from `hyamm.py`
    """

    def test1(self) -> None:
        """
        Test for normalization in DataFrame.
        """
        # Call mock data and test function using helper function.
        df = _run_test(self, "get_yamm_results", "test.csv", normalize=True)
        act = df.to_csv(index=False)
        # String comparison.
        self.check_string(act)

    def test2(self) -> None:
        """
        Test for no normalization in DataFrame.
        """
        # Call mock data and test function using helper function.
        df = _run_test(self, "get_yamm_results", "test.csv", normalize=False)
        act = df.to_csv(index=False)
        # String comparison.
        self.check_string(act)


# #############################################################################
# Test_normalize_yamm_schema
# #############################################################################


class Test_normalize_yamm_schema(hunitest.TestCase):
    """
    Test 'normalize_yammm_schema' functionalities.
    """

    def test1(self) -> None:
        """
        Test normalized output of `normalize_yamm_schema` with given `cols_map`
        """
        # Prepare inputs.
        cols_map = {
            "origin": None,
            "refreshedAt": "timestamp",
            "firstName": "first_name",
            "lastName": "last_name",
            "linkedinProfileUrl": "linkedin_url",
            "linkedinJobTitle": "job_title",
            "job_title_description": None,
            "companyName": "company_name",
            "location": "city",
            "companyIndustry": "category",
        }
        filtered_cols_map = {k: v for k, v in cols_map.items() if v is not None}
        mock_data = _load_mock_data(self, "test.csv")
        # Run test function.
        result = cmprauhy.normalize_yamm_schema(mock_data, filtered_cols_map)
        act = result.to_csv(index=False, sep=" ")
        # Check outputs.
        exp = r"""
         timestamp  first_name   last_name        linkedin_url   job_title   company_name             city    category
        2024-01-01       Alice       Smith  linkedin.com/alice    Engineer       TechCorp       "New York"        Tech
        2024-01-02         Bob     Johnson    linkedin.com/bob     Manager         BizInc  "San Francisco"     Finance
        """
        # Compare strings.
        self.assert_equal(act, exp, fuzzy_match=True)
