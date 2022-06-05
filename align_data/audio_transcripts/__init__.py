from .audio_transcripts import AudioTranscripts


AUDIO_TRANSCRIPTS_REGISTRY = [
    AudioTranscripts(
        "https://drive.google.com/uc?id=13JiAHAWakTTNQqGEXgiL0mjsuVka4-Sm",
        "scraped-transcripts",
        "transcripts",
        True,
    ),
    # AudioTranscripts(
    #     "otter_ai_cleaned_transcripts", ""
    # ),
]
