def process_axis_value(value, deadzone):
    """
    Processes a joystick axis value, applying a deadzone and scaling.

    Args:
        value (float): The raw axis value in range [-1, 1].
        deadzone (float): Threshold around 0 where small movements are ignored.

    Returns:
        float: The scaled axis value, with deadzone applied.
    """
    check_value(value)

    if abs(value) < deadzone:
        return 0

    if value > 0:
        return scale_value(value, deadzone, 1, 0, 1)
    else:
        return scale_value(value, -1, -deadzone, -1, 0)

def check_value(value):
    if value < -1 or value > 1:
        raise ValueError(f"value out of range! {value} is not in [-1, 1]")

def scale_value(value, old_min, old_max, new_min, new_max) -> float:
    if old_max == old_min:
        raise ValueError("old_max and old_min cannot be the same value.")
    return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min