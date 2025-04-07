> Installation Steps Provided Below.

## How It Works
Authentication: The tool uses your Meetup API key for authentication.

Configuration: You specify which groups to monitor in the config.json file.

Event Checking: The tool periodically checks for upcoming events in your configured groups.

Filtering: It can filter events based on keywords in the event title or description.

Auto-RSVP: When it finds a matching event, it automatically RSVPs on your behalf.

Tracking: It keeps track of events you've already RSVPed to avoid duplicates.

## Setup/Installation
Insert your meetup.com API Key in .env file in this format:
```
MEETUP_API_KEY=your_api_key_here
```
Then run the program by 
```bash
pip install -r requirements.txt 
./auto_rsvp.py
```

to setup cron 
```bash
# Open crontab editor
crontab -e

# Add this line to run every hour (replace with your actual path)
0 * * * * cd /path/to/meetup-auto-rsvp && /path/to/meetup-auto-rsvp/meetup-rsvp-env/bin/python auto_rsvp.py
```


## Troubleshooting
If you encounter authentication issues, verify your API key is correct.

If the tool isn't RSVPing to events, check your group configurations and make sure the group urlnames are correct.

Check the log file (auto_rsvp.log) for detailed error messages.

