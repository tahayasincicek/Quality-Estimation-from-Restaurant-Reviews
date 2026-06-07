import nltk
import re
from textblob import TextBlob
from nltk.tokenize import sent_tokenize

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Dictionary of aspect keywords
aspect_keywords = {
    'Food': ['food', 'meal', 'delicious', 'taste', 'chicken', 'meat', 'burger', 'pizza', 'soup', 'cold', 'hot', 'fresh', 'tasty', 'flavor'],
    'Service': ['service', 'waiter', 'staff', 'manager', 'rude', 'friendly', 'slow', 'fast', 'wait', 'hour', 'minutes', 'table'],
    'Ambience': ['place', 'atmosphere', 'vibe', 'clean', 'dirty', 'loud', 'quiet', 'music', 'environment', 'decor'],
    'Price': ['price', 'cost', 'expensive', 'cheap', 'worth', 'value', 'bill', 'money', 'pay']
}

SPLIT_PATTERN = re.compile(
    r"\s*(?:[,;]|\b(?:but|however|although|though|yet|whereas)\b)\s*",
    flags=re.IGNORECASE,
)

SENTENCE_FALLBACK_PATTERN = re.compile(r"[^.!?]+(?:[.!?]+|$)")


def split_opinion_units(text):
    """
    Split a review into short clauses that usually contain one opinion target.
    This keeps mixed input like "service is bad, soup is delicious" from giving
    both aspects the same sentence-level sentiment.
    """
    try:
        sentences = sent_tokenize(text)
    except LookupError:
        sentences = [m.group(0).strip() for m in SENTENCE_FALLBACK_PATTERN.finditer(text)]

    units = []
    for sentence in sentences:
        for unit in SPLIT_PATTERN.split(sentence):
            unit = unit.strip()
            if unit:
                units.append(unit)

    return units or [text.strip()] if text.strip() else []

def get_aspects_from_sentence(sentence):
    """Identify which aspects are mentioned in a single sentence."""
    sentence_lower = sentence.lower()
    detected_aspects = []
    for aspect, keywords in aspect_keywords.items():
        if any(re.search(r"\b" + re.escape(keyword) + r"\b", sentence_lower) for keyword in keywords):
            detected_aspects.append(aspect)
    return detected_aspects

def get_unit_sentiment(unit):
    """Determine sentiment of an opinion unit using TextBlob polarity."""
    blob = TextBlob(unit)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'Good'
    elif polarity < -0.1:
        return 'Poor'
    else:
        return 'Average'

def analyze_aspects(text):
    """
    Splits text into opinion units, finds aspects, and determines sentiment per aspect.
    Returns a dictionary grouping aspects by their sentiments.
    """
    units = split_opinion_units(text)
    
    aspect_results = {
        'Food': [],
        'Service': [],
        'Ambience': [],
        'Price': []
    }
    
    for unit in units:
        aspects = get_aspects_from_sentence(unit)
        if aspects:
            sentiment = get_unit_sentiment(unit)
            for aspect in aspects:
                aspect_results[aspect].append({'sentence': unit, 'sentiment': sentiment})
                
    # Aggregate sentiments
    final_insights = []
    for aspect, items in aspect_results.items():
        if items:
            # Simple majority voting for the aspect sentiment
            good_c = sum(1 for i in items if i['sentiment'] == 'Good')
            poor_c = sum(1 for i in items if i['sentiment'] == 'Poor')
            avg_c = sum(1 for i in items if i['sentiment'] == 'Average')
            
            if good_c > poor_c and good_c >= avg_c:
                overall = 'Good'
            elif poor_c > good_c and poor_c >= avg_c:
                overall = 'Poor'
            elif avg_c >= good_c and avg_c >= poor_c:
                overall = 'Average'
            else:
                overall = 'Average'
                
            final_insights.append({
                'aspect': aspect,
                'sentiment': overall,
                'sentences': [i['sentence'] for i in items]
            })
            
    return final_insights
