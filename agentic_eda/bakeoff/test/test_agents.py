import helpers.hunit_test as hunitest

import agentic_eda.bakeoff.agents as aebagent
import agentic_eda.bakeoff.datasets as aebdata


class _FailingAgent(aebagent.Agent):
    name = "failing"

    def run(self, dataset: aebdata.Dataset) -> aebagent.AgentResult:
        raise ValueError("intentional")


# #############################################################################
# Test_agents
# #############################################################################


class Test_agents(hunitest.TestCase):
    def test_dummy_agent(self) -> None:
        """
        The dummy agent runs and reports real facts about the data.
        """
        res = aebagent.DummyAgent().timed_run(aebdata.get_dataset("uci_heart"))
        self.assertTrue(res.ran_ok)
        self.assertGreaterEqual(len(res.insights), 3)
        self.assertIn("300 rows x 8 columns", res.insights[0])
        self.assertIsNotNone(res.runtime_s)

    def test_failing_agent_is_caught(self) -> None:
        """
        A crashing agent is recorded as a failure, not raised.
        """
        res = _FailingAgent().timed_run(aebdata.get_dataset("openaq"))
        self.assertFalse(res.ran_ok)
        self.assertIn("ValueError: intentional", res.error)
        self.assertIsNotNone(res.runtime_s)

    def test_all_agents(self) -> None:
        names = [a.name for a in aebagent.all_agents()]
        self.assertIn("dummy", names)
