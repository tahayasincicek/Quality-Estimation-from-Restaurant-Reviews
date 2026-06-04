import re

EMOJI_DICT = {
    "🔥": "excellent",
    "😡": "angry",
    "🤮": "disgusting",
    "🤢": "disgusting",
    "😍": "love",
    "❤️": "love",
    "👍": "good",
    "👎": "bad",
    "⭐": "star",
    "😋": "delicious",
    "💩": "terrible",
    "😊": "happy",
    "😞": "sad",
    "💯": "perfect",
    "👏": "bravo"
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
    "sus": "suspicious"
}

def decode_text(text):
    """
    Scans the text for emojis and slangs, translates them to NLP-friendly english words.
    Returns: (decoded_text, list_of_insights)
    list_of_insights format: [{'original': '🔥', 'decoded': 'excellent', 'type': 'emoji'}, ...]
    """
    insights = []
    decoded_text = text

    # Decode Emojis
    for emoji, meaning in EMOJI_DICT.items():
        if emoji in decoded_text:
            insights.append({'original': emoji, 'decoded': meaning, 'type': 'emoji'})
            # Emojileri aralara boşluk bırakarak yerleştir
            decoded_text = decoded_text.replace(emoji, f" {meaning} ")

    # Decode Slangs
    # Slang kelimelerini regex kelime sınırları (\b) ile aramak daha güvenlidir
    for slang, meaning in SLANG_DICT.items():
        # Case insensitive olarak ara
        pattern = r"\b" + re.escape(slang) + r"\b"
        if re.search(pattern, decoded_text, flags=re.IGNORECASE):
            insights.append({'original': slang, 'decoded': meaning, 'type': 'slang'})
            decoded_text = re.sub(pattern, f" {meaning} ", decoded_text, flags=re.IGNORECASE)
            
    # Temizlenmiş metindeki fazla boşlukları düzelt
    decoded_text = " ".join(decoded_text.split())

    return decoded_text, insights
