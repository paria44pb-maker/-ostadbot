import importlib


class DependencyChecker:
    """
    Checks required dependencies before system start
    """

    REQUIRED_PACKAGES = [
        "asyncio",
        "logging",
        "psutil"
    ]

    @staticmethod
    def check():
        missing = []

        for pkg in DependencyChecker.REQUIRED_PACKAGES:
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append(pkg)

        if missing:
            raise Exception(f"Missing dependencies: {missing}")
