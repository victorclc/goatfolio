from dataclasses import dataclass


@dataclass
class ExtractIcon:
    color: int
    code_point: int

    def to_json(self):
        return self.__dict__
