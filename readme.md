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

uri = rtsp://192.168.1.68:554/live/0/SUB

## Sink

Set enabled to yes to show the output on screen. Set to no for headless operation.

To store the current frame as a jpeg, use the `keep_frame` options in the config

## Notifications

For the telegram bot, you can create your own bot and group and supply the details under the `TELEGRAM` section of the options.

To change the notifaction frequency modify the values in the `NOTIFICATIONS` section.
The 'time_to_arm' bit is not yet implemented, system is always armed.

frames_to_trigger: (integer) The number of positive detections in the window after which an event will be triggered
trigger_window: (seconds) the window used for the above
fps: (integer) Frames per a second to process
repeat_alert_minutes: (minutes) The number of minutes to suppress notifications for after a positive notice.

## Detection

To tweak this bit, it would be good to have a display attached to the nano.
Faces will be outlined in red, eyes in blue.

# Run the app

From the terminal, run:
```bash
python3 detector.py
```