import shutil


class Health:
    force_fail = False

    @staticmethod
    def check_health():
        checks = []
        checks.append({"name": "disk", "status": Health.checkDisk()})
        checks.append({"name": "test", "status": Health.checkTest()})

        status = "UP" if all(check["status"] == "UP" for check in checks) else "DOWN"
        return status, checks

    @staticmethod
    def checkDisk():
        _, _, free = shutil.disk_usage("/")

        _10_mb = 10.0 * 1024 * 1024

        return "UP" if free > _10_mb else "DOWN"

    @staticmethod
    def checkTest():
        return "DOWN" if Health.force_fail else "UP"
