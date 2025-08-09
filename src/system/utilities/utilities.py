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

    # Detect and store the sign
    sign = 1 if value >= 0 else -1
    abs_value = abs(value)

    # Handle edge case for non-positive values
    if abs_value == 0:
        return sign * new_min

    # Adjust old_min for log scale if it's non-positive
    adjusted_old_min = old_min if old_min > 0 else 0.000001
    log_old_min = log(adjusted_old_min)
    log_old_max = log(old_max)
    log_abs_value = log(abs_value)

    # Perform log scaling
    scaled = (log_abs_value - log_old_min) / (log_old_max - log_old_min) * (new_max - new_min) + new_min

    # Restore original sign
    return sign * scaled

@staticmethod
def angle_difference_deg(a, b):
    """
    Returns the smallest difference between two angles in degrees.
    Result is in range [-180, 180].
    """
    diff = (a - b + 180) % 360 - 180
    return diff