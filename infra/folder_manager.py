import os


class FolderManager:
    """
    Ensures required directories exist
    """

    REQUIRED_FOLDERS = [
        "logs",
        "data",
        "backups",
        "temp",
        "plugins"
    ]

    @staticmethod
    def create():
        base_dir = os.getcwd()

        for folder in FolderManager.REQUIRED_FOLDERS:
            path = os.path.join(base_dir, folder)

            if not os.path.exists(path):
                os.makedirs(path)
