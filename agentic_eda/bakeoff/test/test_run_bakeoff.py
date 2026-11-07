import os
import unittest.mock as umock

import helpers.hunit_test as hunitest

import agentic_eda.bakeoff.run_bakeoff as aebrubak


# #############################################################################
# Test_run_bakeoff
# #############################################################################


class Test_run_bakeoff(hunitest.TestCase):
    def test_list(self) -> None:
        with umock.patch("builtins.print") as mock_print:
            aebrubak._main(aebrubak._parse(), ["--list"])
        out = "\n".join(str(c.args[0]) for c in mock_print.call_args_list)
        self.assertIn("Datasets (4)", out)
        self.assertIn("dummy", out)

    def test_run_subset(self) -> None:
        """
        Running one agent on one dataset produces a one-row scorecard on disk.
        """
        scratch = self.get_scratch_space()
        with umock.patch("agentic_eda.bakeoff.scoring.RESULTS_DIR", scratch):
            card = aebrubak._run("dummy", "uci_heart")
        self.assertEqual(len(card.rows), 1)
        self.assertTrue(card.rows[0].runs_ok)
        self.assertTrue(os.path.exists(os.path.join(scratch, "scorecard.csv")))
