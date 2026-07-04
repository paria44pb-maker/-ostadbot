import time
import psutil
from datetime import datetime

START_TIME = time.time()

class Health:
    """
    System health monitoring for CryptoPulseAI
    """

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent(interval=0.5)

    @staticmethod
    def ram_usage():
        return psutil.virtual_memory().percent

    @staticmethod
    def disk_usage():
        return psutil.disk_usage("/").percent

    @staticmethod
    def uptime():
        return round(time.time() - START_TIME, 2)

    @staticmethod
    def status():
        """
        Full system status snapshot
        """
        return {
            "cpu": Health.cpu_usage(),
            "ram": Health.ram_usage(),
            "disk": Health.disk_usage(),
            "uptime_sec": Health.uptime(),
            "time": datetime.utcnow().isoformat()
        }
