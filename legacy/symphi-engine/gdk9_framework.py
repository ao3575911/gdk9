import math
import numpy as np

# Symmetry sets (from handbook)
idemp_upper = set('AHIMOTUV WXY'.replace(' ', ''))
idemp_lower = set('amotuv wxy'.replace(' ', ''))
biphasic_upper = set('BCDEK')
biphasic_lower = set('bcdek')
invol_upper = set('NSZ')
invol_lower = set('nsz')
asym_upper = set('FGJLPQR')
asym_lower = set('fgjl pqr'.replace(' ', ''))

def get_symmetry_type(char):
    upper = char.upper()
    pos = ord(upper) - ord('A') + 1
    if char.isupper():
        if upper in idemp_upper: return 'idempotent'
        if upper in biphasic_upper: return 'biphasic'
        if upper in invol_upper: return 'involutive'
        if upper in asym_upper: return 'asymmetric'
    else:
        if upper in idemp_lower: return 'idempotent'
        if upper in biphasic_lower: return 'biphasic'
        if upper in invol_lower: return 'involutive'
        if upper in asym_lower: return 'asymmetric'
    return None

def energy(char):
    if not char.isalpha(): return 0.0
    upper = char.upper()
    pos = ord(upper) - ord('A') + 1
    sym = get_symmetry_type(char)
    if sym == 'idempotent':
        return float(pos)
    elif sym == 'biphasic':
        return math.sin(pos)
    elif sym == 'involutive':
        return 1.0 / pos
    elif sym == 'asymmetric':
        return pos + 1
    return 0.0

def word_energy(word):
    return sum(energy(c) for c in word)

def vectorize(char):
    if not char.isalpha(): return np.zeros(4)
    upper = char.upper()
    pos = ord(upper) - ord('A') + 1
    sym = get_symmetry_type(char)
    type_id = {'idempotent':1, 'biphasic':2, 'involutive':3, 'asymmetric':4}.get(sym, 0)
    e = energy(char)
    theta = pos * math.pi / 26  # Assumed angular pos
    return np.array([pos, type_id, math.sqrt(abs(e)), math.sin(theta)])
