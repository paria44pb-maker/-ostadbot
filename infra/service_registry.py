class ServiceRegistry:
    """
    Global service container for sharing system components
    """

    _services = {}

    @classmethod
    def register(cls, name: str, service):
        cls._services[name] = service

    @classmethod
    def get(cls, name: str):
        return cls._services.get(name)

    @classmethod
    def all(cls):
        return cls._services

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._services
