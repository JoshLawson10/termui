from __future__ import annotations

import unicodedata
from enum import Enum

FUNCTIONAL_KEYS = {
    "27u": "escape",
    "13u": "enter",
    "9u": "tab",
    "127u": "backspace",
    "2~": "insert",
    "3~": "delete",
    "1D": "left",
    "1C": "right",
    "1A": "up",
    "1B": "down",
    "5~": "pageup",
    "6~": "pagedown",
    "1H": "home",
    "1~": "home",
    "7~": "home",
    "1F": "end",
    "4~": "end",
    "8~": "end",
    "57358u": "caps_lock",
    "57359u": "scroll_lock",
    "57360u": "num_lock",
    "57361u": "print_screen",
    "57362u": "pause",
    "57363u": "menu",
    "1P": "f1",
    "11~": "f1",
    "1Q": "f2",
    "12~": "f2",
    "13~": "f3",
    "1R": "f3",
    "1S": "f4",
    "14~": "f4",
    "15~": "f5",
    "17~": "f6",
    "18~": "f7",
    "19~": "f8",
    "20~": "f9",
    "21~": "f10",
    "23~": "f11",
    "24~": "f12",
    "57376u": "f13",
    "57377u": "f14",
    "57378u": "f15",
    "57379u": "f16",
    "57380u": "f17",
    "57381u": "f18",
    "57382u": "f19",
    "57383u": "f20",
    "57384u": "f21",
    "57385u": "f22",
    "57386u": "f23",
    "57387u": "f24",
    "57388u": "f25",
    "57389u": "f26",
    "57390u": "f27",
    "57391u": "f28",
    "57392u": "f29",
    "57393u": "f30",
    "57394u": "f31",
    "57395u": "f32",
    "57396u": "f33",
    "57397u": "f34",
    "57398u": "f35",
    "57399u": "0",
    "57400u": "1",
    "57401u": "2",
    "57402u": "3",
    "57403u": "4",
    "57404u": "5",
    "57405u": "6",
    "57406u": "7",
    "57407u": "8",
    "57408u": "9",
    "57409u": "decimal",
    "57410u": "divide",
    "57411u": "multiply",
    "57412u": "subtract",
    "57413u": "add",
    "57414u": "enter",
    "57415u": "equal",
    "57416u": "separator",
    "57417u": "left",
    "57418u": "right",
    "57419u": "up",
    "57420u": "down",
    "57421u": "pageup",
    "57422u": "pagedown",
    "57423u": "home",
    "57424u": "end",
    "57425u": "insert",
    "57426u": "delete",
    "1E": "kp_begin",
    "57427~": "kp_begin",
    "57428u": "media_play",
    "57429u": "media_pause",
    "57430u": "media_play_pause",
    "57431u": "media_reverse",
    "57432u": "media_stop",
    "57433u": "media_fast_forward",
    "57434u": "media_rewind",
    "57435u": "media_track_next",
    "57436u": "media_track_previous",
    "57437u": "media_record",
    "57438u": "lower_volume",
    "57439u": "raise_volume",
    "57440u": "mute_volume",
    "57441u": "left_shift",
    "57442u": "left_control",
    "57443u": "left_alt",
    "57444u": "left_super",
    "57445u": "left_hyper",
    "57446u": "left_meta",
    "57447u": "right_shift",
    "57448u": "right_control",
    "57449u": "right_alt",
    "57450u": "right_super",
    "57451u": "right_hyper",
    "57452u": "right_meta",
    "57453u": "iso_level3_shift",
    "57454u": "iso_level5_shift",
}


class Keys(str, Enum):  # type: ignore[no-redef]
    """
    List of keys for use in key bindings.

    Note that this is an "StrEnum", all values can be compared against
    strings.
    """

    # pylint: disable=invalid-overridden-method
    @property
    def value(self) -> str:
        return super().value

    Escape = "escape"
    ShiftEscape = "shift+escape"
    Return = "return"

    ControlAt = "ctrl+@"

    ControlA = "ctrl+a"
    ControlB = "ctrl+b"
    ControlC = "ctrl+c"
    ControlD = "ctrl+d"
    ControlE = "ctrl+e"
    ControlF = "ctrl+f"
    ControlG = "ctrl+g"
    ControlH = "ctrl+h"
    ControlI = "ctrl+i"  # Tab
    ControlJ = "ctrl+j"  # Newline
    ControlK = "ctrl+k"
    ControlL = "ctrl+l"
    ControlM = "ctrl+m"
    ControlN = "ctrl+n"
    ControlO = "ctrl+o"
    ControlP = "ctrl+p"
    ControlQ = "ctrl+q"
    ControlR = "ctrl+r"
    ControlS = "ctrl+s"
    ControlT = "ctrl+t"
    ControlU = "ctrl+u"
    ControlV = "ctrl+v"
    ControlW = "ctrl+w"
    ControlX = "ctrl+x"
    ControlY = "ctrl+y"
    ControlZ = "ctrl+z"

    Control1 = "ctrl+1"
    Control2 = "ctrl+2"
    Control3 = "ctrl+3"
    Control4 = "ctrl+4"
    Control5 = "ctrl+5"
    Control6 = "ctrl+6"
    Control7 = "ctrl+7"
    Control8 = "ctrl+8"
    Control9 = "ctrl+9"
    Control0 = "ctrl+0"

    ControlShift1 = "ctrl+shift+1"
    ControlShift2 = "ctrl+shift+2"
    ControlShift3 = "ctrl+shift+3"
    ControlShift4 = "ctrl+shift+4"
    ControlShift5 = "ctrl+shift+5"
    ControlShift6 = "ctrl+shift+6"
    ControlShift7 = "ctrl+shift+7"
    ControlShift8 = "ctrl+shift+8"
    ControlShift9 = "ctrl+shift+9"
    ControlShift0 = "ctrl+shift+0"

    ControlBackslash = "ctrl+backslash"
    ControlSquareClose = "ctrl+right_square_bracket"
    ControlCircumflex = "ctrl+circumflex_accent"
    ControlUnderscore = "ctrl+underscore"

    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"
    Home = "home"
    End = "end"
    Insert = "insert"
    Delete = "delete"
    PageUp = "pageup"
    PageDown = "pagedown"

    ControlLeft = "ctrl+left"
    ControlRight = "ctrl+right"
    ControlUp = "ctrl+up"
    ControlDown = "ctrl+down"
    ControlHome = "ctrl+home"
    ControlEnd = "ctrl+end"
    ControlInsert = "ctrl+insert"
    ControlDelete = "ctrl+delete"
    ControlPageUp = "ctrl+pageup"
    ControlPageDown = "ctrl+pagedown"

    ShiftLeft = "shift+left"
    ShiftRight = "shift+right"
    ShiftUp = "shift+up"
    ShiftDown = "shift+down"
    ShiftHome = "shift+home"
    ShiftEnd = "shift+end"
    ShiftInsert = "shift+insert"
    ShiftDelete = "shift+delete"
    ShiftPageUp = "shift+pageup"
    ShiftPageDown = "shift+pagedown"

    ControlShiftLeft = "ctrl+shift+left"
    ControlShiftRight = "ctrl+shift+right"
    ControlShiftUp = "ctrl+shift+up"
    ControlShiftDown = "ctrl+shift+down"
    ControlShiftHome = "ctrl+shift+home"
    ControlShiftEnd = "ctrl+shift+end"
    ControlShiftInsert = "ctrl+shift+insert"
    ControlShiftDelete = "ctrl+shift+delete"
    ControlShiftPageUp = "ctrl+shift+pageup"
    ControlShiftPageDown = "ctrl+shift+pagedown"

    BackTab = "shift+tab"

    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"
    F13 = "f13"
    F14 = "f14"
    F15 = "f15"
    F16 = "f16"
    F17 = "f17"
    F18 = "f18"
    F19 = "f19"
    F20 = "f20"
    F21 = "f21"
    F22 = "f22"
    F23 = "f23"
    F24 = "f24"

    ControlF1 = "ctrl+f1"
    ControlF2 = "ctrl+f2"
    ControlF3 = "ctrl+f3"
    ControlF4 = "ctrl+f4"
    ControlF5 = "ctrl+f5"
    ControlF6 = "ctrl+f6"
    ControlF7 = "ctrl+f7"
    ControlF8 = "ctrl+f8"
    ControlF9 = "ctrl+f9"
    ControlF10 = "ctrl+f10"
    ControlF11 = "ctrl+f11"
    ControlF12 = "ctrl+f12"
    ControlF13 = "ctrl+f13"
    ControlF14 = "ctrl+f14"
    ControlF15 = "ctrl+f15"
    ControlF16 = "ctrl+f16"
    ControlF17 = "ctrl+f17"
    ControlF18 = "ctrl+f18"
    ControlF19 = "ctrl+f19"
    ControlF20 = "ctrl+f20"
    ControlF21 = "ctrl+f21"
    ControlF22 = "ctrl+f22"
    ControlF23 = "ctrl+f23"
    ControlF24 = "ctrl+f24"

    Any = "<any>"
    ScrollUp = "<scroll-up>"
    ScrollDown = "<scroll-down>"
    Ignore = "<ignore>"
    ControlSpace = "ctrl-at"
    Tab = "tab"
    Space = "space"
    Enter = "enter"
    Backspace = "backspace"

    ShiftControlLeft = ControlShiftLeft
    ShiftControlRight = ControlShiftRight
    ShiftControlHome = ControlShiftHome
    ShiftControlEnd = ControlShiftEnd


KEY_NAME_REPLACEMENTS = {
    "solidus": "slash",
    "reverse_solidus": "backslash",
    "commercial_at": "at",
    "hyphen_minus": "minus",
    "plus_sign": "plus",
    "low_line": "underscore",
}
REPLACED_KEYS = {value: key for key, value in KEY_NAME_REPLACEMENTS.items()}

KEY_TO_UNICODE_NAME = {
    "exclamation_mark": "EXCLAMATION MARK",
    "quotation_mark": "QUOTATION MARK",
    "number_sign": "NUMBER SIGN",
    "dollar_sign": "DOLLAR SIGN",
    "percent_sign": "PERCENT SIGN",
    "left_parenthesis": "LEFT PARENTHESIS",
    "right_parenthesis": "RIGHT PARENTHESIS",
    "plus_sign": "PLUS SIGN",
    "hyphen_minus": "HYPHEN-MINUS",
    "full_stop": "FULL STOP",
    "less_than_sign": "LESS-THAN SIGN",
    "equals_sign": "EQUALS SIGN",
    "greater_than_sign": "GREATER-THAN SIGN",
    "question_mark": "QUESTION MARK",
    "commercial_at": "COMMERCIAL AT",
    "left_square_bracket": "LEFT SQUARE BRACKET",
    "reverse_solidus": "REVERSE SOLIDUS",
    "right_square_bracket": "RIGHT SQUARE BRACKET",
    "circumflex_accent": "CIRCUMFLEX ACCENT",
    "low_line": "LOW LINE",
    "grave_accent": "GRAVE ACCENT",
    "left_curly_bracket": "LEFT CURLY BRACKET",
    "vertical_line": "VERTICAL LINE",
    "right_curly_bracket": "RIGHT CURLY BRACKET",
}

KEY_ALIASES = {
    "tab": ["ctrl+i"],
    "enter": ["ctrl+m"],
    "escape": ["ctrl+left_square_brace"],
    "ctrl+at": ["ctrl+space"],
    "ctrl+j": ["newline"],
}

KEY_DISPLAY_ALIASES = {
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
    "backspace": "⌫",
    "escape": "esc",
    "enter": "⏎",
    "minus": "-",
    "space": "space",
    "pagedown": "pgdn",
    "pageup": "pgup",
    "delete": "del",
}


ASCII_KEY_NAMES = {"\t": "tab"}


def _get_unicode_name_from_key(key: str) -> str:
    """Get the best guess for the Unicode name of the char corresponding to the key.

    This function can be seen as a pseudo-inverse of the function `_character_to_key`.
    """
    return KEY_TO_UNICODE_NAME.get(key, key)


def _get_key_aliases(key: str) -> list[str]:
    """Return all aliases for the given key, including the key itself"""
    return [key] + KEY_ALIASES.get(key, [])


def format_key(key: str) -> str:
    """Given a key (i.e. the `key` string argument to Binding __init__),
    return the value that should be displayed in the app when referring
    to this key (e.g. in the Footer widget)."""

    display_alias = KEY_DISPLAY_ALIASES.get(key)
    if display_alias:
        return display_alias

    original_key = REPLACED_KEYS.get(key, key)
    tentative_unicode_name = _get_unicode_name_from_key(original_key)
    try:
        unicode_name = unicodedata.lookup(tentative_unicode_name)
    except KeyError:
        pass
    else:
        if unicode_name.isprintable():
            return unicode_name
    return tentative_unicode_name


def key_to_character(key: str) -> str | None:
    """Given a key identifier, return the character associated with it.

    Args:
        key: The key identifier.

    Returns:
        A key if one could be found, otherwise `None`.
    """
    _, separator, key = key.rpartition("+")
    if separator:
        return None

    if len(key) == 1:
        return key

    try:
        return unicodedata.lookup(KEY_TO_UNICODE_NAME[key])
    except KeyError:
        pass

    try:
        return unicodedata.lookup(key.replace("_", " ").upper())
    except KeyError:
        pass

    return None


def _character_to_key(character: str) -> str:
    """Convert a single character to a key value.

    This transformation can be undone by the function `_get_unicode_name_from_key`.
    """
    if not character.isalnum():
        try:
            key = (
                unicodedata.name(character).lower().replace("-", "_").replace(" ", "_")
            )
        except ValueError:
            key = ASCII_KEY_NAMES.get(character, character)
    else:
        key = character
    key = KEY_NAME_REPLACEMENTS.get(key, key)
    return key


def _normalize_key_list(keys: str) -> str:
    """Normalizes a comma separated list of keys.

    Replaces single letter keys with full name.
    """

    keys_list = [key.strip() for key in keys.split(",")]
    return ",".join(
        _character_to_key(key) if len(key) == 1 else key for key in keys_list
    )
