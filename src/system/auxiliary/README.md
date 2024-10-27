# Auxiliary

Auxiliary is a set of optional functionality that sends system status data
to the auxiliary Raspberry Pi hat with a display, neopixels, and misc hardware.

## Heartbeat

The auxilary board expects a heartbeat signal (on GPIO17) from the Raspberry Pi as an indication
if the Raspberry Pi has booted and is operational.

Execute the install_heartbeat.sh on the Raspberry Pi to install and start the heartbeat service.

Check the service status:
>sudo systemctl status heartbeat.service 

Stop the service:
>sudo systemctl stop heartbeat.service 

Start the service:

>sudo systemctl start heartbeat.service 



