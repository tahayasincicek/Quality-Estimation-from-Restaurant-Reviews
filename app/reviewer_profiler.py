def analyze_reviewer_profile(useful_votes, label, confidence_dict):
    """
    Evaluates review reliability based on real Yelp dataset 'useful' votes.
    useful_votes: integer from dataset
    label: predicted sentiment label ('Good', 'Average', 'Poor')
    confidence_dict: dictionary of prediction probabilities
    """
    is_spam_risk = False
    is_trusted = False
    warning_message = ""
    badge_message = ""
    
    if useful_votes is None:
        return None
        
    try:
        useful_votes = int(useful_votes)
    except:
        return None
        
    if useful_votes == 0:
        if label == 'Good' and confidence_dict.get('good', 0) > 80:
            is_spam_risk = True
            warning_message = "Low Reliability: This extreme review is from a user with 0 'useful' votes. Potential fake review."
        elif label == 'Poor' and confidence_dict.get('poor', 0) > 80:
            is_spam_risk = True
            warning_message = "Low Reliability: This extreme review is from a user with 0 'useful' votes. Potential competitor attack."
    elif useful_votes > 3:
        is_trusted = True
        badge_message = f"Trusted Reviewer: This user is validated by the community with {useful_votes} 'Useful' votes."
        
    if is_spam_risk or is_trusted:
        return {
            'is_spam_risk': is_spam_risk,
            'is_trusted': is_trusted,
            'warning_message': warning_message,
            'badge_message': badge_message,
            'useful_votes': useful_votes
        }
    return None
