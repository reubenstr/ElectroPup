"""
    Custom exceptions for better error reporting and handling.
"""

class DomainBreach(Exception):
    """Exception raised when domain is breached when calculating inverse kinematics.

    Attributes:
       None
    """
    def __init__(self):       
        self.message = "Domain breach during inverse kinematics calculation!"
        super().__init__(self.message)