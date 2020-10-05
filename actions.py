from typing import Dict, Text, Any, List, Union, Optional
import datetime
from dateutil import relativedelta
import logging
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.events import Form, AllSlotsReset, SlotSet, Restarted, EventType

logger = logging.getLogger(__name__)


class CustomFormAction(FormAction):
    def name(self):
        return

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        """Request the next slot and utter template if needed,
            else return None"""

        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                logger.debug(f"Request next slot '{slot}'")
                dispatcher.utter_message(
                    template=f"utter_ask_{self.name()}_{slot}", **tracker.slots
                )
                return [SlotSet(REQUESTED_SLOT, slot)]

        return None



class AccountOpenForm(CustomFormAction):
    """Transfer money form..."""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "act_open_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["PERSON", "aadhar_number","mobile_number", "confirm"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "PERSON": [
                self.from_entity(entity="PERSON"),
                self.from_text(intent=["inform", None, "transfer_money"]),
            ],
            "aadhar_number": [
                self.from_entity(entity="aadhar_number"),
                self.from_entity(entity="number"),
            ],
			"mobile_number": [
                self.from_entity(entity="mobile_number"),
                self.from_entity(entity="number"),
            ],
            "confirm": [
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ],
        }

    def submit(self, dispatcher, tracker, domain):
        if tracker.get_slot("confirm"):
            dispatcher.utter_message(template="utter_account_created")
            return [
                AllSlotsReset(),
                SlotSet("aadhar_number", tracker.get_slot("aadhar_number")),
            ]
        else:
            dispatcher.utter_message(template="utter_account_creation_cancelled")
            return [AllSlotsReset()]


class ActionAccountOpen(Action):
    def name(self):
        return "action_account_open"

    def run(self, dispatcher, tracker, domain):
	    PERSON = tracker.get_slot("PERSON")
		aadhar_number = int(tracker.get_slot("aadhar_number"))
        mobile_number = int(tracker.get_slot("mobile_number"))
        	
        if aadhar_number:
		    dispatcher.utter_message(
                template="utter_account_created",
                PERSON=PERSON,
                aadhar_number=aadhar_number,
            )
            return [
                SlotSet("aadhar_number", aadhar_number),
                
            ]
        else:
            dispatcher.utter_message(
                template="utter_ask_account_creation_confirm",
                aadhar_number=aadhar_number,
            )
