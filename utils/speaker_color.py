from collections import Counter
from typing import List, Dict, Tuple

# --- CONSTANTS ---
# Format: &H[Alpha][Blue][Green][Red]
# Alpha 20 = ~12% Transparency
PRIORITY_PALETTE = [
    "&H20FFFFFF",  # Rank 1: WHITE (Main Speaker / Default - Clean & Neutral)
    "&H2032C9FF",  # Rank 2: GOLD / AMBER (Primary Emphasis - High Visibility)
    "&H206060FF",  # Rank 3: PASTEL RED / SALMON (Secondary Emphasis - Warm Tone)
    "&H20FFC080",  # Rank 4: SKY BLUE (Tertiary Emphasis - Cool Tone Contrast)
]
DEFAULT_COLOR = "&H20FFFFFF"  # Rank 5+: White (Fallback)


def get_speaker_color_map(words: List[dict]) -> Tuple[List[str], Dict[str, str]]:
    """
    Analyzes the word list, ranks speakers based on word count (density),
    and assigns colors from the priority palette.

    Args:
        words: List of word dictionaries containing 'speaker' keys.

    Returns:
        Tuple containing:
        - ranked_speakers_list: List of speaker IDs sorted by frequency.
        - color_map_dict: Dictionary mapping Speaker ID -> ASS Color Code.
    """
    if not words:
        return [], {}

    # 1. Calculate speaker frequencies
    speaker_counts = Counter([w.get("speaker", "SPEAKER_00") for w in words])

    # 2. Sort from most frequent to least frequent
    # Example: ['SPEAKER_05', 'SPEAKER_02']
    ranked_speakers = [spk for spk, count in speaker_counts.most_common()]

    # 3. Create the Color Map
    color_map = {}
    for i, spk in enumerate(ranked_speakers):
        if i < len(PRIORITY_PALETTE):
            color_map[spk] = PRIORITY_PALETTE[i]
        else:
            color_map[spk] = DEFAULT_COLOR

    return ranked_speakers, color_map
