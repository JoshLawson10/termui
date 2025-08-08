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
        return f"RGB({self.red}, {self.green}, {self.blue})"

    def to_tuple(self):
        return (self.red, self.green, self.blue)

    def lighten(self, percent: float) -> "RGBColor":
        """
        Lightens the color by a given percentage.
        """
        return RGBColor(
            red=min(255, int(self.red + self.red * percent)),
            green=min(255, int(self.green + self.green * percent)),
            blue=min(255, int(self.blue + self.blue * percent)),
        )

    def darken(self, percent: float) -> "RGBColor":
        """
        Darkens the color by a given percentage.
        """
        return RGBColor(
            red=max(0, int(self.red - self.red * percent)),
            green=max(0, int(self.green - self.green * percent)),
            blue=max(0, int(self.blue - self.blue * percent)),
        )
