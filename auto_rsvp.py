import os
import json
import time
import logging
from datetime import datetime
import schedule
import requests
from dotenv import load_dotenv
import meetup.api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_rsvp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MeetupAutoRSVP:
    def __init__(self, config_file="config.json"):
        """Initialize the Meetup Auto-RSVP tool."""
        self.api_key = os.getenv("MEETUP_API_KEY")
        if not self.api_key:
            raise ValueError("MEETUP_API_KEY environment variable not set")
        
        # Initialize Meetup client
        self.client = meetup.api.Client(self.api_key)
        
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Track RSVPed events to avoid duplicates
        self.rsvped_events = set()
        self.load_rsvped_events()
        
        logger.info("Meetup Auto-RSVP initialized")

    def load_rsvped_events(self):
        """Load previously RSVPed events from file."""
        try:
            with open("rsvped_events.json", 'r') as f:
                self.rsvped_events = set(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            self.rsvped_events = set()
    
    def save_rsvped_events(self):
        """Save RSVPed events to file."""
        with open("rsvped_events.json", 'w') as f:
            json.dump(list(self.rsvped_events), f)

    def check_events(self):
        """Check for new events in configured groups and RSVP if needed."""
        logger.info("Checking for new events...")
        
        for group in self.config["groups"]:
            if not group.get("auto_rsvp", False):
                continue
                
            group_urlname = group["urlname"]
            keywords = [k.lower() for k in group.get("keywords", [])]
            
            try:
                # Get upcoming events for the group
                events = self.client.GetEvents({
                    'group_urlname': group_urlname,
                    'status': 'upcoming'
                })
                
                logger.info(f"Found {len(events.results)} upcoming events for {group_urlname}")
                
                for event in events.results:
                    event_id = event.get('id')
                    event_name = event.get('name', 'Unnamed event')
                    
                    # Skip if already RSVPed
                    if event_id in self.rsvped_events:
                        logger.debug(f"Already RSVPed to event: {event_name}")
                        continue
                    
                    # Check if event matches keywords (if any)
                    event_description = (event.get('description', '') or '').lower()
                    event_name_lower = event_name.lower()
                    
                    if keywords and not any(keyword in event_name_lower or keyword in event_description 
                                           for keyword in keywords):
                        logger.debug(f"Event doesn't match keywords: {event_name}")
                        continue
                    
                    # RSVP to the event
                    self.rsvp_to_event(event_id, event_name, group_urlname)
                    
            except Exception as e:
                logger.error(f"Error checking events for {group_urlname}: {str(e)}")

    def rsvp_to_event(self, event_id, event_name, group_urlname):
        """RSVP to a specific event."""
        try:
            # Use the Meetup API to RSVP
            response = self.client.PostRSVP({
                'event_id': event_id,
                'rsvp': self.config.get("rsvp_answer_default", "yes")
            })
            
            if response:
                logger.info(f"Successfully RSVPed to: {event_name} in {group_urlname}")
                self.rsvped_events.add(event_id)
                self.save_rsvped_events()
            else:
                logger.warning(f"Failed to RSVP to: {event_name}")
                
        except Exception as e:
            logger.error(f"Error RSVPing to {event_name}: {str(e)}")

    def run_scheduler(self):
        """Run the scheduler to check for events periodically."""
        interval_hours = self.config.get("check_interval_hours", 1)
        
        logger.info(f"Setting up scheduler to run every {interval_hours} hour(s)")
        
        # Schedule the check_events function
        schedule.every(interval_hours).hours.do(self.check_events)
        
        # Run check_events immediately on startup
        self.check_events()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Sleep for 1 minute between checks

def main():
    """Main function to run the Meetup Auto-RSVP tool."""
    try:
        auto_rsvp = MeetupAutoRSVP()
        auto_rsvp.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
