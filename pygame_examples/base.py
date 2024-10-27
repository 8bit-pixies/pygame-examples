from abc import ABC


class BaseScene(ABC):
    def render(self, clock, screen, events, keys):
        raise NotImplementedError
