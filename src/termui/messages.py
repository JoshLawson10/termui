from termui.message import Message


class TerminalSupportsSynchronizedOutput(Message):
    """Message indicating that the terminal supports synchronized output."""


class InBandWindowResize(Message):
    """Reports if the in-band window resize protocol is supported."""

    def __init__(self, supported: bool, enabled: bool) -> None:
        """Initialize message.

        Args:
            supported: Is the protocol supported?
            enabled: Is the protocol enabled.
        """
        self.supported = supported
        self.enabled = enabled
        super().__init__()

    @classmethod
    def from_setting_parameter(cls, setting_parameter: int) -> "InBandWindowResize":
        """Construct the message from the setting parameter.

        Args:
            setting_parameter: Setting parameter from stdin.

        Returns:
            New InBandWindowResize instance.
        """

        supported = setting_parameter not in (0, 4)
        enabled = setting_parameter in (1, 3)
        return InBandWindowResize(supported, enabled)
