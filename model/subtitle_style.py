from dataclasses import dataclass


@dataclass
class ASSStyle:
    name: str = "Default"

    font_name: str = "Montserrat Black"
    font_size: int = 90

    primary_color: str = "&H20FFFFFF"
    outline_color: str = "&H00000000"
    back_color: str = "&H00000000"

    bold: bool = False
    italic: bool = False

    outline: int = 3
    shadow: int = 1

    alignment: int = 5
    margin_l: int = 40
    margin_r: int = 40
    margin_v: int = 60
