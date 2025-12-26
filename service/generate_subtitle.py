from pathlib import Path
import json

from model.subtitle_style import ASSStyle
from utils.ass_format import seconds_to_ass_time, bool_to_ass
from utils.speaker_color import get_speaker_color_map


def generate_subtitle(
    word_transcript_path: Path,
    output_path: Path,
    start: float,
    end: float,
    base_style: ASSStyle = ASSStyle(),
    fade_in_ms: int = 50,
    fade_out_ms: int = 50,
    is_upper_case: bool = True,
):
    """
    Generates an .ass subtitle file for a specific time range using speaker-aware coloring.
    """
    if not word_transcript_path.exists():
        raise FileNotFoundError(word_transcript_path)

    with open(word_transcript_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clip_words = [w for w in data["words"] if w["start"] >= start and w["end"] <= end]

    if not clip_words:
        print(f"Warning: No words found for subtitle range {start}-{end}")
        return

    ranked_speakers, speaker_colors = get_speaker_color_map(clip_words)

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

    # Generate dynamic styles based on ranked speakers
    for spk in ranked_speakers:
        color = speaker_colors[spk]

        lines.append(
            f"Style: {spk},{base_style.font_name},{base_style.font_size},"
            f"{color},&H000000FF,{base_style.outline_color},{base_style.back_color},"
            f"{bool_to_ass(base_style.bold)},{bool_to_ass(base_style.italic)},0,0,"
            f"100,100,0,0,1,{base_style.outline},{base_style.shadow},"
            f"{base_style.alignment},{base_style.margin_l},{base_style.margin_r},{base_style.margin_v},1"
        )

    lines.append("")

    # -------- EVENTS --------
    lines.append("[Events]")
    lines.append(
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    )

    for w in clip_words:
        # Calculate relative timestamps for the clip
        start_ts = seconds_to_ass_time(w["start"] - start)
        end_ts = seconds_to_ass_time(w["end"] - start)

        speaker_id = w.get("speaker", "SPEAKER_00")

        text_content = w["text"].strip()
        if is_upper_case:
            text_content = text_content.upper()

        # Apply fading effect
        text = f"{{\\fad({fade_in_ms},{fade_out_ms})}}{text_content}"

        # Use speaker_id as the Style name to apply the correct color automatically
        lines.append(
            f"Dialogue: 0,{start_ts},{end_ts},{speaker_id},,"
            f"{base_style.margin_l},{base_style.margin_r},{base_style.margin_v},,"
            f"{text}"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
