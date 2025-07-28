import subprocess
from math import log

@staticmethod
def is_service_running(service_name):
        try:
            # Run the systemctl command to check the service status
            result = subprocess.run(
                ['systemctl', 'status', service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )      
            return 'active (running)' in result.stdout          
        except Exception as e:
            print(f"[Live] error, unable to determine if service is running: {e}")
            return False 
        

@staticmethod
def scale_value(value, old_min, old_max, new_min, new_max) -> float:
    if old_max == old_min:
        raise ValueError("old_max and old_min cannot be the same value.")
    return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min

@staticmethod
def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return float("inf")
    return numerator / denominator

@staticmethod
def log_scale_value(value, old_min, old_max, new_min, new_max):
    if old_max == old_min:
        raise ValueError("old_max and old_min cannot be the same value.")
    if value <= 0:
        return new_min

    if old_min <= 0:
        log_old_min = log(old_min + 0.000001)
    else:
        log_old_min = log(old_min)

    log_old_max = log(old_max)
    log_value = log(value)

    return (log_value - log_old_min) / (log_old_max - log_old_min) * (new_max - new_min) + new_min
