import re

def is_sarcastic(text):
    """
    Detects sarcasm in text using rule-based heuristics.
    Looks for contradiction between positive/praising words and negative/complaining contexts,
    as well as known sarcastic phrase patterns.
    """
    text_lower = text.lower()
    
    # 1. Known sarcastic phrase patterns
    sarcasm_patterns = [
        r"yeah\s+right",
        r"sure\s+it\s+was",
        r"what\s+a\s+joke",
        r"thanks\s+for\s+nothing",
        r"brilliant\s+.*\(?\!+\)?",
        r"so\s+glad\s+i",
        r"just\s+what\s+i\s+wanted",
        r"great\s+wait",
        r"fantastic\s+wait",
        r"good\s+luck\s+getting",
        r"only\s+took",
        r"\d+\s+hour.*great",
        r"\d+\s+hour.*amazing",
    ]
    
    for pat in sarcasm_patterns:
        if re.search(pat, text_lower):
            return True
            
    # 2. Sentiment Contradiction (Positive Words + Severe Negative Context + Exclamation)
    # E.g. "Amazing food, we only waited 2 hours!" -> sarcasm
    negative_context_words = [
        "wait", "cold", "expensive", "rude", "never", "terrible", 
        "bad", "hour", "hours", "late", "forgot", "awful"
    ]
    positive_praise_words = [
        "great", "amazing", "best", "perfect", "brilliant", "wonderful", 
        "love", "fantastic", "excellent"
    ]
    
    has_neg = any(w in text_lower for w in negative_context_words)
    has_pos = any(w in text_lower for w in positive_praise_words)
    
    # If the text has high praise but also negative context, and ends with or contains an exclamation
    # it is very likely sarcastic.
    if has_pos and has_neg and text.count('!') >= 1:
        return True
        
    return False
