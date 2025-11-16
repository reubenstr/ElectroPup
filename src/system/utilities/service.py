import subprocess
import traceback
from enum import Enum, auto

class ServiceCommand(Enum):
    START = "start"
    STOP = "stop"
    DISABLE = "disable"
    RESTART = "restart"

def service_action(action: ServiceCommand, service_name: str):
    try:
        subprocess.run(
            ["sudo", "systemctl", action.value, service_name],
            check=True
        )
        print(f"[System] '{action.value}' command successful for service '{service_name}'")

    except subprocess.CalledProcessError as e:
        print(f"[System] ERROR: failed to execute '{action.value}' on service '{service_name}': {e}")

    except Exception as e:
        print(f"[System] Unexpected error: {e}")
        print(traceback.format_exc())

    finally:
        exit(1)
