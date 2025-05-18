# actions.py
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_utils import BitcoinAPI

class ActionGetBtcPrice(Action):
    def name(self) -> str:
        return "action_get_btc_price"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        api = BitcoinAPI(vs_currency="usd")
        price = api.get_current_price()
        dispatcher.utter_message(
            text=f"The current Bitcoin price is ${price:,.2f}"
        )
        return []
