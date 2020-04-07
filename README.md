# Python_Nanoleaf_Ambilight
Python Script to sync Nanoleaf with Computer Screen Content

This script is intend to capture all colored pixels of you current screen and checks for updates since the last capture.
If so it analyzes the main colors, runs some adjustments and sends the color command to the <a href="https://nanoleaf.me/en/">NanoLeaf</a>
It should work quite similar with other networked lighting systems if you change the commands regarding my_aurora.
The script is also sending the Nanoleaf to sleep mode if there is inactivity, so dont worry.

# Limitations
Keep in mind i have limited the area to analyze down to 80% and only analyze 10% of those pixels dueto my slow computer (1x1.4Ghz) Meaning it consumes 10-20% CPU time when running, idle consumption = 0-1%

It should be much faster with a better computer, but there might still be a latency because of the transmission from Computer -> Switch(router) -> WiFi -> Nanoleaf

# Demonstration
See a demo video how it <a href="https://mega.nz/folder/CMMAXICB#uQ_Ma9DWCaXFfk9WzWZILA/file/CI0yiQhQ">runs here</a> Launch demo.mp4
