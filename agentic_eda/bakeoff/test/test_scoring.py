import os

import pandas as pd

import helpers.hunit_test as hunitest

import agentic_eda.bakeoff.scoring as aebscor


# #############################################################################
# Test_Scorecard
# #############################################################################


class Test_Scorecard(hunitest.TestCase):
    def test_empty(self) -> None:
        """
        An empty scorecard still has the full column schema.
        """
        card = aebscor.Scorecard()
        self.assertEqual(list(card.to_frame().columns), aebscor.COLUMNS)
        self.assertIn("empty", str(card))

    def test_save_roundtrip(self) -> None:
        """
        Saved CSV keeps the schema; judgment columns stay blank until PR 1.6.
        """
        card = aebscor.Scorecard()
        card.add(
            aebscor.ScoreRow(
                agent="dummy",
                dataset="uci_heart",
                task="classification",
                runs_ok=True,
                runtime_s=0.01,
                n_insights=4,
            )
        )
        path = os.path.join(self.get_scratch_space(), "card.csv")
        card.save(path)
        df = pd.read_csv(path)
        self.assertEqual(list(df.columns), aebscor.COLUMNS)
        self.assertEqual(df.loc[0, "agent"], "dummy")
        self.assertTrue(pd.isna(df.loc[0, "insight_quality"]))
