from enum import Enum


class GeminiModel(Enum):
    GEMINI_3_FLASH = "gemini-3-flash-preview"
    GEMINI_3_PRO = "gemini-3-pro-preview"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"


DEFAULT_MODEL = GeminiModel.GEMINI_3_FLASH


def resolve_model(name: str | None) -> GeminiModel:
    if not name:
        return DEFAULT_MODEL
    try:
        return GeminiModel[name.upper()]
    except KeyError:
        raise ValueError(
            f"Invalid Gemini model '{name}'. "
            f"Available: {[m.name for m in GeminiModel]}"
        )
