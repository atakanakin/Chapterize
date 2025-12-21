from pathlib import Path
import json

from model.subtitle_style import ASSStyle
from utils.ass_format import seconds_to_ass_time, bool_to_ass


def generate_ass(
    word_transcript_path: Path,
    output_path: Path,
    *,
    start: float,
    end: float,
    style: ASSStyle = ASSStyle(),
    fade_in_ms: int = 150,
    fade_out_ms: int = 150,
    is_upper_case: bool = True,
):
    with open(word_transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = [
        w for w in data["words"]
        if w["start"] >= start and w["end"] <= end
    ]

    lines = []

    # -------- HEADER --------
    lines.append("[Script Info]")
    lines.append("ScriptType: v4.00+")
    lines.append("PlayResX: 1080")
    lines.append("PlayResY: 1920")
    lines.append("ScaledBorderAndShadow: yes")
    lines.append("")

    # -------- STYLES --------
    lines.append("[V4+ Styles]")
    lines.append(
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding"
    )

    lines.append(
        f"Style: {style.name},{style.font_name},{style.font_size},"
        f"{style.primary_color},&H000000FF,{style.outline_color},{style.back_color},"
        f"{bool_to_ass(style.bold)},{bool_to_ass(style.italic)},0,0,"
        f"100,100,0,0,1,{style.outline},{style.shadow},"
        f"{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},1"
    )

    lines.append("")

    # -------- EVENTS --------
    lines.append("[Events]")
    lines.append(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    )

    for w in words:
        start_ts = seconds_to_ass_time(w["start"] - start)
        end_ts = seconds_to_ass_time(w["end"] - start)

        text = f"{{\\fad({fade_in_ms},{fade_out_ms})}}{w['text']}"

        lines.append(
            f"Dialogue: 0,{start_ts},{end_ts},{style.name},,"
            f"{style.margin_l},{style.margin_r},{style.margin_v},,"
            f"{text.upper() if is_upper_case else text}"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
