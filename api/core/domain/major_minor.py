from typing import NamedTuple, Self


class MajorMinor(NamedTuple):
    major: int
    minor: int

    @classmethod
    def from_string(cls, value: str) -> Self | None:
        splits = value.split(".")
        if len(splits) != 2:
            return None
        try:
            return cls(major=int(splits[0]), minor=int(splits[1]))
        except ValueError:
            return None

    def to_string(self) -> str:
        return f"{self.major}.{self.minor}"
