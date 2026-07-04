import asyncio
from collections import defaultdict


class EventBus:
    """
    Async event system for internal communication
    """

    def __init__(self):
        self._events = defaultdict(list)

    def on(self, event_name: str, handler):
        """
        Register event handler
        """
        self._events[event_name].append(handler)

    async def emit(self, event_name: str, data=None):
        """
        Trigger event
        """
        if event_name not in self._events:
            return

        for handler in self._events[event_name]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                print(f"⚠️ Event error [{event_name}]: {e}")
