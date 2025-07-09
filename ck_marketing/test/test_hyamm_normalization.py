import pandas as pd

import ck_marketing.process_automation.hyamm as cmprauhy
import helpers.hunit_test as hunitest


# #############################################################################
# Test_normalize_contact_schema
# #############################################################################


class Test_normalize_contact_schema(hunitest.TestCase):

    def test1(self) -> None:
        """
        Test column renaming.
        """
        # Input data.
        df = pd.DataFrame(
            {"First Name": ["Alice"], "Email Address": ["alice@example.com"]}
        )
        cols_map = {"First Name": "first_name", "Email Address": "email"}
        # Call function to test.
        act = cmprauhy.normalize_contact_schema(df, cols_map)
        act = act.to_csv(index=False)
        exp = r"""
        hash,origin,timestamp,first_name,last_name,email,email_verification,linkedin_url,job_title,job_title_description,company_name,company_domain,city,stages,restrictions,industry,category,notes
        ,,,Alice,,alice@example.com,,,,,,,,,,,,
        """
        # Check output.
        self.assert_equal(exp, act, fuzzy_match=True)

    def test2(self) -> None:
        """
        Test handling of whitespace in column values.
        """
        # Input data.
        df = pd.DataFrame(
            {"first_name": ["    John "], "email": [" john@example.com "]}
        )
        cols_map = {"first_name": "first_name", "email": "email"}
        # Call function to test.
        act = cmprauhy.normalize_contact_schema(df, cols_map)
        act = act.to_csv(index=False)
        exp = r"""
        hash,origin,timestamp,first_name,last_name,email,email_verification,linkedin_url,job_title,job_title_description,company_name,company_domain,city,stages,restrictions,industry,category,notes
        ,,,John,,john@example.com,,,,,,,,,,,,
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test3(self) -> None:
        """
        Test that the email_verification column uses only canonical values.
        """
        # Input data.
        df = pd.DataFrame(
            {
                "first_name": ["    John "],
                "email": [" john@example.com "],
                "email_verification": ["valid"],
            }
        )
        cols_map = {
            "first_name": "first_name",
            "email": "email",
            "email_verification": "email_verification",
        }
        # Call the function to test.
        act = cmprauhy.normalize_contact_schema(df, cols_map)
        act = act.to_csv(index=False)
        exp = r"""
        hash,origin,timestamp,first_name,last_name,email,email_verification,linkedin_url,job_title,job_title_description,company_name,company_domain,city,stages,restrictions,industry,category,notes
        ,,,John,,john@example.com,_valid_,,,,,,,,,,,
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test4(self) -> None:
        """
        Test the final column order matches the Contact schema.
        """
        # Input data.
        df = pd.DataFrame(
            {"first_name": ["    John "], "Email": [" john@example.com "]}
        )
        cols_map = {"Email": "email", "first_name": "first_name"}
        # Call the function to test.
        act = cmprauhy.normalize_contact_schema(df, cols_map)
        act = act.to_csv(index=False)
        exp = r"""
        hash,origin,timestamp,first_name,last_name,email,email_verification,linkedin_url,job_title,job_title_description,company_name,company_domain,city,stages,restrictions,industry,category,notes
        ,,,John,,john@example.com,,,,,,,,,,,,
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test5(self) -> None:
        """
        Test for None values in cols_map.
        """
        # Input data.
        df = pd.DataFrame(
            {"first_name": ["Alice Smith"], "email": ["alice@example.com"]}
        )
        cols_map = {"email": None, "first_name": None}
        # Call the function to test.
        result = cmprauhy.normalize_contact_schema(df, cols_map)
        act = result.to_csv(index=False)
        exp = r"""
        hash,origin,timestamp,first_name,last_name,email,email_verification,linkedin_url,job_title,job_title_description,company_name,company_domain,city,stages,restrictions,industry,category,notes
        ,,,Alice Smith,,alice@example.com,,,,,,,,,,,,
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test6(self) -> None:
        """
        Test handling of empty DataFrame.
        """
        # Prepare input data.
        df = pd.DataFrame()
        cols_map = {}
        # Call function to test.
        act = cmprauhy.normalize_contact_schema(df, cols_map)
        # Check output.
        self.assertTrue(act.empty, "Returned DataFrame is not empty")
