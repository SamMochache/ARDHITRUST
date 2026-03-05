# apps/verification/services/trust_score.py

def calculate_trust_score(verification_result, property_obj) -> int:
    score = 0
    if verification_result.ownership_confirmed:  score += 30
    if not verification_result.encumbrances_json: score += 20
    if not verification_result.caveat_present:    score += 25
    if verification_result.rates_cleared:         score += 15
    score += 10  # base score for clean submission
    return min(score, 100)