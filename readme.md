# Setup

From jetson nano terminal run:

```bash
./setup.sh
```

# Configuration

The file "config.ini" contains all the configurabale values for the app.

## Camera Source

For the uri, just fill in exactly what you would put into VLC to see the stream.
Example:

[SOURCE]
uri = rtsp://192.168.1.68:554/live/0/SUB


## Notifications

For the telegram bot, you can create your own bot and group and give the details here.

[TELEGRAM]
token = <>
groupId = <>

Use the below to tweak the timing for notifications.
The 'time_to_arm' bit is not yet implemented, system is always armed.

[NOTIFICATIONS]
#time with no eye detection before we arm the system (minutes)
time_to_arm=10
#once armed, how many frames before we trigger an alert
frames_to_trigger=1
#the window in which to count the above (seconds)
trigger_window=10
fps=25
repeat_alert_minutes=1

## Detection

To tweak this bit, it would be good to have a display attached to the nano.
Faces will be outlined in red, eyes in blue.

[DETECTOR]
#fiddle with these numbers to tune the system.
#Scale factor indicates how much the image is reduced at each scale
#min_neghbours is a measure of certainty
face_scale_factor=1.3
face_min_neighbours=5
eye_scale_factor=2
eye_min_neighbours=5

# Run the app

For now, the app only runs with a display attached. A headless option will be coming soon.

From the terminal, run:
```bash
python3 detect.py
```