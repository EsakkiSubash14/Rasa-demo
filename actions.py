from typing import Any, Text, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from models import Reminder, SessionLocal

class ActionStoreReminder(Action):
    
    def name(self) -> Text:
        return "action_store_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract entities
        task = tracker.get_slot('task')
        time = tracker.get_slot('time')
        
        if not task or not time:
            dispatcher.utter_message(text="I need both a task and a time to set the reminder.")
            return []

        # Convert time string to datetime object
        try:
            parsed_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")  # Example format: 2023-06-30T15:00:00.000+02:00
        except ValueError:
            dispatcher.utter_message(text="Failed to parse the time. Please provide a valid time format.")
            return []

        # Connect to the database session
        db: Session = SessionLocal()

        try:
            # Create a new Reminder object
            reminder = Reminder(task=task, time=parsed_time)

            # Add the reminder to the session
            db.add(reminder)
            db.commit()  # Commit the transaction to the database
            db.refresh(reminder)  # Refresh the object to get updated attributes

            dispatcher.utter_message(text=f"Reminder set: {task} at {time}")
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to store reminder: {str(e)}")
        finally:
            db.close()  # Close the session

        return [SlotSet("task", task), SlotSet("time", time)]
