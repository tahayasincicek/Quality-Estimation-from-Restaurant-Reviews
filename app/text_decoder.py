import re

EMOJI_DICT = {
    "\U0001f525": "excellent",
    "\U0001f621": "angry",
    "\U0001f92e": "disgusting",
    "\U0001f922": "disgusting",
    "\U0001f60d": "love",
    "\u2764\ufe0f": "love",
    "\U0001f44d": "good",
    "\U0001f44e": "bad",
    "\u2b50": "star",
    "\U0001f60b": "delicious",
    "\U0001f4a9": "terrible",
    "\U0001f60a": "happy",
    "\U0001f61e": "sad",
    "\U0001f4af": "perfect",
    "\U0001f44f": "bravo",
}

SLANG_DICT = {
    "wtf": "what the fuck",
    "tbh": "to be honest",
    "ngl": "not gonna lie",
    "lmao": "laughing my ass off",
    "idk": "i do not know",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "goat": "greatest of all time",
    "omg": "oh my god",
    "af": "as fuck",
    "fr": "for real",
    "rn": "right now",
    "sus": "suspicious",
}


def decode_text(text):
    """
    Translate emojis and slang to NLP-friendly English words.

    Returns:
        tuple[str, list[dict]]: decoded text and replacement metadata.
    """
    insights = []
    decoded_text = text

    for emoji, meaning in EMOJI_DICT.items():
        if emoji in decoded_text:
            insights.append({"original": emoji, "decoded": meaning, "type": "emoji"})
            decoded_text = decoded_text.replace(emoji, f" {meaning} ")

    for slang, meaning in SLANG_DICT.items():
        pattern = r"\b" + re.escape(slang) + r"\b"
        if re.search(pattern, decoded_text, flags=re.IGNORECASE):
            insights.append({"original": slang, "decoded": meaning, "type": "slang"})
            decoded_text = re.sub(pattern, f" {meaning} ", decoded_text, flags=re.IGNORECASE)

    decoded_text = " ".join(decoded_text.split())
    return decoded_text, insights
