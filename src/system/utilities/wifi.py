
import os
import shlex
import subprocess
from enum import Enum

"""
    Connects to WiFi access point per credentials supplied as environmental variables.
    Creates hotspot. 
"""

class WiFiSelection(Enum):
    UNKNOWN = 0
    CLIENT = 1
    HOTSPOT = 2


class Wifi():
    def __init__(self):
        self.selection: WiFiSelection = WiFiSelection.UNKNOWN
    
        self.ap_ssid: str = "ElectroPup AP"
        self.ap_pass: str = "electropup"
        self.client_ssid: str = None
        self.client_pass: str = None

    def get_credentials(self):     
        try:
            self.client_ssid = os.environ["ELECTROPUP_CLIENT_SSID"]
            self.client_pass = os.environ["ELECTROPUP_CLIENT_PASS"]          
        except KeyError:
            pass
         

    def connect_to_wifi(self):
        self.get_credentials()

        if self.client_ssid == None or self.client_pass == None:
            print("[WiFi] Error, client SSID and password not found in the environmental variables!")
            return
   
        print("[WiFi] connecting to :", self.client_ssid )
    
        command_str = f"nmcli device wifi connect {shlex.quote(self.client_ssid)} password {shlex.quote(self.client_pass)}"
        command_tokens = shlex.split(command_str)

        try:           
            result = subprocess.run(command_tokens, check=True, capture_output=True, text=True)           
            print("[WiFi] Output:", result.stdout)
            self.selection = WiFiSelection.CLIENT
        except subprocess.CalledProcessError as e:        
            print("[WiFi] Error output:", e.stderr)
            self.selection = WiFiSelection.UNKNOWN

    
    def create_hotspot(self):
        self.get_credentials()

        if self.client_ssid == None or self.client_pass == None:
            print("[WIFI] Unable to create hotspot, client credentials must be supplied as an environmental variable for connect reset!")
            return

        print(f"[WiFi] Creating hotspot SSID: {self.ap_ssid}, password: {self.ap_pass}")

        command_str = f"nmcli device wifi hotspot ssid {shlex.quote(self.ap_ssid)} password {shlex.quote(self.ap_pass)}"
        command_tokens = shlex.split(command_str)

        try:           
            result = subprocess.run(command_tokens, check=True, capture_output=True, text=True)           
            print("[WiFi] Output:", result.stdout)
            self.selection = WiFiSelection.HOTSPOT
        except subprocess.CalledProcessError as e:        
            print("[WiFi] Error output:", e.stderr)
            self.selection = WiFiSelection.UNKNOWN


    def is_wifi_connected(self):
        try:
            command_str = 'nmcli -t -f STATE general'
            command_tokens = shlex.split(command_str)
            result = subprocess.run(command_tokens, capture_output=True, text=True)
            state = result.stdout.strip()
            return state == "connected"
        except subprocess.CalledProcessError as e:
            print("[WiFi] Failed to get Wi-Fi status:", e.stderr.strip())
            return False
        
        
    def is_wifi_connected_to_ssid(self, target_ssid):
        try:
            command_str = 'nmcli -t -f active,ssid dev wifi'
            command_tokens = shlex.split(command_str)
            result = subprocess.run(command_tokens, capture_output=True, text=True)
            for line in result.stdout.strip().splitlines():
                if line.startswith("yes:"):
                    current_ssid = line.split(":")[1]
                    return current_ssid == target_ssid
            return False
        except subprocess.CalledProcessError as e:
            print("[WiFi] Failed to get Wi-Fi status:", e.stderr.strip())
            return False


