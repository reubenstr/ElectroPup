import subprocess

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