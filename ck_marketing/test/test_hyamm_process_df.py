import io
import textwrap

import pandas as pd

import ck_marketing.process_automation.hyamm as cmprauhy
import helpers.hunit_test as hunitest


# #############################################################################
# Test_clean_up_contact_df
# #############################################################################


class Test_clean_up_contact_df(hunitest.TestCase):

    def test1(self) -> None:
        """
        Test removal of row where first name is empty.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        ,Brown,invalid@,Invalid Company,invalid.com,
        Josh,Brown,invalid@umd.edu,Microsoft,invalid.com,
        """
        # Read the data, ensuring no extra spaces cause issues
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name    email               company_name   company_domain   linkedin_url
        5252cdcbd791c20f78a5c7a9186afe7b     Josh         Brown       invalid@umd.edu    Microsoft      invalid.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test2(self) -> None:
        """
        Test for moving emails from LinkedIn column to email column.
        """
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        Alice,Smith,,Business LLC,business.com,alice@company.com
        John,Smith,john.smith@gmail.com,Business LLC,business.com,alice@company.com
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name   email               company_name      company_domain   linkedin_url
        8c4426faaff63f1da2a822bca8d9208c     John         Smith      alice@company.com   "Business LLC"      business.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test3(self) -> None:
        """
        Test for moving URLs from `company_name` to `company_domain`.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        Charlie,Taylor,,https://company.com,,
        John,Smith,john.smith@gmail.com,Business LLC,business.com,alice@company.com
        """
        # Read the data, ensuring no extra spaces cause issues
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name   email                 company_name      company_domain   linkedin_url
        8c4426faaff63f1da2a822bca8d9208c     John         Smith       alice@company.com   "Business LLC"      business.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test4(self) -> None:
        """
        Test the removal of invalid names.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        李,Wang,li@example.com,Tech Corp,tech.com,https://linkedin.com/in/li
        John,Smith,john.smith@gmail.com,Business LLC,business.com,alice@company.com
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name   email                company_name      company_domain   linkedin_url
        8c4426faaff63f1da2a822bca8d9208c     John         Smith       alice@company.com   "Business LLC"      business.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test5(self) -> None:
        """
        Test the removal duplicate mail.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        John,Doe,john@example.com,Apple Inc,example.com,https://linkedin.com/in/john
        Shaun,Dan,john@example.com,Google Inc,example.com,https://linkedin.com/in/john
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name   email               company_name      company_domain   linkedin_url
        7866f143baa0b2a515f43ed7812feacb     John         Doe         john@example.com    "Apple Inc"         example.com      https://linkedin.com/in/john
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test6(self) -> None:
        """
        Test the removal of row containing invalid emails.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        John,Doe,john@example.com,Example Inc,example.com,https://linkedin.com/in/john
        Alice,Smith,alice@example.com,Business LLC,business.com,alice@company.com
        ,Brown,invalid@,Invalid Company,invalid.com,nan
        Charlie,Taylor,,https://company.com,,
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name    email               company_name       company_domain    linkedin_url
        678d00d89607d41e06a8764bb1eb61fe     Alice        Smith       alice@company.com   "Business LLC"      business.com
        7866f143baa0b2a515f43ed7812feacb     John         Doe         john@example.com    "Example Inc"       example.com      https://linkedin.com/in/john
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test7(self) -> None:
        """
        Test the cleaning of mails from emails.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        John,Doe,mailto:john@example.com,Example Inc,example.com,https://linkedin.com/in/john
        John,Smith,john.smith@gmail.com,Business LLC,business.com,alice@company.com
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                            first_name last_name               email   company_name  company_domain linkedin_url
        8c4426faaff63f1da2a822bca8d9208c      John     Smith   alice@company.com   "Business LLC"  business.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test8(self) -> None:
        """
        Test the removal of 'nan' value in df.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        Shaun,Brown,invalid@gmail.com,Invalid Company,invalid.com,
        John,Smith,john.smith@gmail.com,Business LLC,business.com,alice@company.com
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name   email                 company_name      company_domain   linkedin_url
        79267b97c5b33fd47a7fbbb5a2b71a75     Shaun        Brown       invalid@gmail.com   "Invalid Company"   invalid.com
        8c4426faaff63f1da2a822bca8d9208c     John         Smith       alice@company.com   "Business LLC"      business.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test9(self) -> None:
        """
        Test if the invalid LinkedIn urls are removed.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        Alice,Smith,alice@example.com,Business LLC,business.com,alice@company.com
        Bob,Jones,bob@example.com,Startup Co,startup.com,https://example.com
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name    email               company_name       company_domain   linkedin_url
        678d00d89607d41e06a8764bb1eb61fe     Alice        Smith       alice@company.com   "Business LLC"      business.com
        b4d2f3c2cd2a878c64b97728395bf746     Bob          Jones       bob@example.com     "Startup Co"        https://example.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)

    def test10(self) -> None:
        """
        Test the addition of hash with sorting.
        """
        # Prepare input.
        input_data = r"""
        first_name,last_name,email,company_name,company_domain,linkedin_url
        Alice,Smith,alice@example.com,Business LLC,business.com,
        John,Doe,john@example.com,Example Inc,example.com,https://linkedin.com/in/john
        Bob,Jones,bob@example.com,Startup Co,startup.com,
        """
        df = pd.read_csv(io.StringIO(input_data.strip()))
        # Call function to test.
        cleaned_df = cmprauhy.clean_up_contact_df(df)
        act = cleaned_df.to_csv(sep=" ")
        exp = r"""
        hash                                first_name   last_name    email                company_name      company_domain   linkedin_url
        2c40409ef65bc7a428e36b434dd69ca4     Alice        Smith       alice@example.com   "Business LLC"      business.com
        7866f143baa0b2a515f43ed7812feacb     John         Doe         john@example.com    "Example Inc"       example.com      https://linkedin.com/in/john
        b4d2f3c2cd2a878c64b97728395bf746     Bob          Jones       bob@example.com     "Startup Co"        startup.com
        """
        # Check output.
        self.assert_equal(act, exp, fuzzy_match=True)


# #############################################################################
# Test_infer_category
# #############################################################################


class Test_infer_category(hunitest.TestCase):

    def test1(self) -> None:
        """
        Test the `infer_category` function to ensure it correctly infers
        categories.
        """
        # Prepare input data.
        sample_data_2 = r"""
        category,company_domain,company_name,stages,job_title
        ,vc.com,VC Corp,,Partner
        Tech,tech.com,Tech Inc,Series A,Engineer
        ,venture.com,Venture LLC,Seed,Investor
        Finance,finance.com,Finance Corp,,Analyst
        ,capital.com,Capital Partners,Series B,Director
        """
        cleaned_sample_data = textwrap.dedent(sample_data_2)
        # Read the data, ensuring no extra spaces cause issues.
        contact_df = pd.read_csv(
            io.StringIO(cleaned_sample_data.strip()), dtype=str, na_filter=False
        )
        # Call function to test.
        result_df = cmprauhy.infer_category(contact_df, leave_debug_cols=True)
        expected_categories = [
            "Venture Fund (inferred)",
            "Tech",
            "Venture Fund (inferred)",
            "Finance",
            "Venture Fund (inferred)",
        ]
        # Check output.
        self.assertEqual(
            list(result_df["category"]),
            expected_categories,
            "Category column is not updated correctly",
        )


# #############################################################################
# Test_sanity_check_contact_df
# #############################################################################


class Test_sanity_check_contact_df(hunitest.TestCase):
    """
    Test different data processing functions from 'hyamm'.
    """

    def test1(self) -> None:
        """
        Ensure `sanity_check_contact_df` runs without errors on valid data.

        This test checks that the function does not raise any exceptions
        when provided with a valid DataFrame.
        """
        # Prepare input data.
        data = {
            "first_name": ["John", "Alice", "Bob"],
            "last_name": ["Doe", "Smith", "Jones"],
            "email": ["john@example.com", "alice@example.com", "bob@example.com"],
            "company_domain": ["example.com", "business.com", "startup.com"],
            "linkedin_url": [
                "https://linkedin.com/in/john",
                "https://linkedin.com/in/alice",
                "",
            ],
            "email_verification": ["valid", "accept_all", "unknown"],
            "campaign_source": ["Ad1", "Ad2", "Ad3"],
            "campaign_medium": ["Email", "Social", "Organic"],
        }
        df = pd.DataFrame(data)
        try:
            # Call function to test and check action on valid data.
            cmprauhy.sanity_check_contact_df(df)
        except Exception as e:
            self.fail(
                f"sanity_check_contact_df raised an unexpected exception: {e}"
            )
