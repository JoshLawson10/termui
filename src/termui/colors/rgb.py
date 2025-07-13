from dataclasses import dataclass


@dataclass
class RGBColor:
    """
    Represents an RGB color with red, green, and blue components.
    """

    red: int
    green: int
    blue: int

    def __repr__(self):
        return f"RGBC({self.red}, {self.green}, {self.blue})"

    def to_tuple(self):
        return (self.red, self.green, self.blue)
