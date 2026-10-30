import pandas as pd
import pytest

import helpers.hunit_test as hunitest

import agentic_eda.bakeoff.datasets as aebdata


# #############################################################################
# Test_datasets
# #############################################################################


class Test_datasets(hunitest.TestCase):
    def test_registry(self) -> None:
        """
        The registry holds exactly the four bake-off datasets.
        """
        names = {d.name for d in aebdata.all_datasets()}
        self.assertEqual(
            names, {"uci_heart", "nyc_taxi", "openaq", "amazon_reviews"}
        )

    def test_sample_loads_with_target(self) -> None:
        """
        Every sample is a non-empty DataFrame containing its target column.
        """
        for ds in aebdata.all_datasets():
            df = ds.load()
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
            self.assertIn(ds.target, df.columns)

    def test_sample_is_deterministic(self) -> None:
        ds = aebdata.get_dataset("nyc_taxi")
        pd.testing.assert_frame_equal(ds.load(), ds.load())

    def test_real_load_not_wired(self) -> None:
        """
        Asking for real data that is not wired raises instead of faking it.
        """
        with pytest.raises(NotImplementedError):
            aebdata.get_dataset("openaq").load(real=True)

    def test_unknown_dataset(self) -> None:
        with pytest.raises(KeyError):
            aebdata.get_dataset("nope")
