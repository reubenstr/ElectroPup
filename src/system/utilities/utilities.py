import subprocess
from math import log, copysign, log1p

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
def log_scale_value(x, in_min, in_max, out_min, out_max, k=9.0):
        """
        Map x from [in_min, in_max] to [out_min, out_max] using a signed log-like scale.
        k controls curvature: higher k -> more compression near ends, more resolution near 0.
        """
        # Normalize x to [-1, 1]
        norm_x = ( (x - in_min) / (in_max - in_min) ) * 2.0 - 1.0
        norm_x = max(-1.0, min(1.0, norm_x))  # clamp
        
        # Signed log shaping
        shaped = copysign(log1p(k * abs(norm_x)) / log1p(k), norm_x)
        
        # Map shaped value from [-1, 1] to [out_min, out_max]
        return out_min + (shaped + 1.0) * 0.5 * (out_max - out_min)

@staticmethod
def angle_difference_deg(a, b):
    """
    Returns the smallest difference between two angles in degrees.
    Result is in range [-180, 180].
    """
    diff = (a - b + 180) % 360 - 180
    return diff