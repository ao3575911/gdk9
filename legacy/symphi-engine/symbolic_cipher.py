
import hashlib
import numpy as np
import base64
import string
import argparse
import os

# --- Symbolic Cipher System ---

def build_symbolic_db():
    import pandas as pd

    def build_letter_entry(letter, case_type):
        base = ord(letter.upper()) - 65
        grid_pos = base % 9
        hollow_letters = {
            'A': 1, 'B': 2, 'D': 1, 'O': 1, 'P': 1, 'Q': 1, 'R': 1,
            'a': 1, 'b': 1, 'd': 1, 'e': 1, 'g': 1, 'o': 1, 'p': 1, 'q': 1
        }
        semantic_tags = {
            'A': 'pinnacle', 'B': 'duality', 'C': 'arc', 'D': 'half-shell', 'E': 'fork',
            'F': 'flag', 'G': 'hook', 'H': 'bridge', 'I': 'pillar', 'J': 'hook',
            'K': 'branch', 'L': 'corner', 'M': 'mountain', 'N': 'zigzag', 'O': 'circle',
            'P': 'flagpole', 'Q': 'orb with tail', 'R': 'branch-container', 'S': 'wave',
            'T': 'axis', 'U': 'cup', 'V': 'valley', 'W': 'double-valley', 'X': 'cross',
            'Y': 'split', 'Z': 'zigzag',
            'a': 'seed', 'b': 'stalk', 'c': 'curve', 'd': 'stem-container', 'e': 'spiral',
            'f': 'crook', 'g': 'hooked-seed', 'h': 'pillar', 'i': 'dot', 'j': 'dot-hook',
            'k': 'kick', 'l': 'line', 'm': 'hills', 'n': 'arch', 'o': 'circle',
            'p': 'descender', 'q': 'reverse-descender', 'r': 'flick', 's': 'wavelet',
            't': 'crossbar', 'u': 'cup', 'v': 'angle', 'w': 'double-angle', 'x': 'cross',
            'y': 'tail', 'z': 'zip'
        }
        shape_vectors = {
            'O': [1, 0.2, 0.3], 'A': [0.5, 0.8, 0.7], 'B': [0.8, 0.9, 0.9], 'C': [0.6, 0.4, 0.3],
            'D': [0.9, 0.5, 0.6], 'E': [0.2, 0.8, 0.5], 'F': [0.1, 0.9, 0.4], 'G': [0.7, 0.5, 0.6],
            'H': [0.3, 0.8, 0.7], 'I': [0.1, 0.9, 0.2], 'J': [0.4, 0.6, 0.5], 'K': [0.3, 0.9, 0.6],
            'L': [0.1, 0.8, 0.3], 'M': [0.2, 0.9, 0.8], 'N': [0.2, 0.9, 0.7], 'P': [0.6, 0.6, 0.5],
            'Q': [0.9, 0.4, 0.6], 'R': [0.7, 0.7, 0.7], 'S': [0.8, 0.6, 0.6], 'T': [0.2, 0.9, 0.4],
            'U': [0.7, 0.5, 0.4], 'V': [0.4, 0.7, 0.5], 'W': [0.3, 0.9, 0.8], 'X': [0.5, 0.8, 0.7],
            'Y': [0.5, 0.7, 0.5], 'Z': [0.3, 0.9, 0.6]
        }
        letter_base = letter.upper() if case_type == "lower" else letter
        base_vector = shape_vectors.get(letter_base, [0.5, 0.5, 0.5])
        if case_type == "lower":
            base_vector = [v * 0.9 for v in base_vector]
        return {
            "letter": letter,
            "case": case_type,
            "grid_position": grid_pos,
            "hollow_count": hollow_letters.get(letter, 0),
            "shape_vector": base_vector,
            "semantic_tag": semantic_tags.get(letter, "unknown")
        }

    letters = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
    symbolic_db = [build_letter_entry(l, "upper" if l.isupper() else "lower") for l in letters]
    df = pd.DataFrame(symbolic_db).set_index("letter")

    extra_chars = string.digits + string.punctuation + " "
    extra_entries = []
    for char in extra_chars:
        extra_entries.append({
            "letter": char,
            "case": "symbol",
            "grid_position": 0,
            "hollow_count": 0,
            "shape_vector": [0.1, 0.1, 0.1],
            "semantic_tag": "symbolic"
        })
    df_extra = pd.DataFrame(extra_entries).set_index("letter")
    return pd.concat([df, df_extra])

df_symbolic_letters = build_symbolic_db()

def get_symbolic_data(char):
    if char in df_symbolic_letters.index:
        row = df_symbolic_letters.loc[char]
        return {
            "vector": np.array(row["shape_vector"]),
            "hollow": row["hollow_count"],
            "grid": row["grid_position"]
        }
    else:
        return {
            "vector": np.array([0.1, 0.1, 0.1]),
            "hollow": 0,
            "grid": 0
        }

def symbolic_key_seed_safe(key):
    key_bytes = key.encode('utf-8')
    hash_digest = hashlib.sha256(key_bytes).hexdigest()
    seed = int(hash_digest, 16) % (2**32)
    return seed

def symbolic_cipher_encrypt_full(text, key):
    np.random.seed(symbolic_key_seed_safe(key))
    encrypted_codes = []
    for i, char in enumerate(text):
        data = get_symbolic_data(char)
        vec = data["vector"]
        hollow = data["hollow"]
        grid = data["grid"]
        rand_mod = np.random.rand(3)
        value = (vec + rand_mod) * (hollow + 1) * (grid + 1) * (i + 1)
        cipher_val = int(np.sum(value) * 100) % 256
        encrypted_codes.append(cipher_val)
    return encrypted_codes

def symbolic_cipher_decrypt_full(encrypted_codes, key):
    np.random.seed(symbolic_key_seed_safe(key))
    recovered_chars = []
    for i, code in enumerate(encrypted_codes):
        rand_mod = np.random.rand(3)
        found_char = '?'
        for char in df_symbolic_letters.index:
            data = get_symbolic_data(char)
            vec = data["vector"]
            hollow = data["hollow"]
            grid = data["grid"]
            value = (vec + rand_mod) * (hollow + 1) * (grid + 1) * (i + 1)
            test_val = int(np.sum(value) * 100) % 256
            if test_val == code:
                found_char = char
                break
        recovered_chars.append(found_char)
    return ''.join(recovered_chars)

def encrypt_text_file(text, key):
    encrypted = symbolic_cipher_encrypt_full(text, key)
    byte_array = bytes(encrypted)
    return base64.b64encode(byte_array).decode('utf-8')

def decrypt_text_file(b64_string, key):
    byte_array = base64.b64decode(b64_string.encode('utf-8'))
    encrypted = list(byte_array)
    return symbolic_cipher_decrypt_full(encrypted, key)

def main():
    parser = argparse.ArgumentParser(description="Symbolic Cipher Tool")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Choose to encrypt or decrypt")
    parser.add_argument("input", help="Path to input .txt or .cipher file")
    parser.add_argument("output", help="Path to output file")
    parser.add_argument("key", help="Secret key")

    args = parser.parse_args()

    if args.mode == "encrypt":
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        cipher_text = encrypt_text_file(text, args.key)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(cipher_text)
        print("File encrypted and saved to", args.output)

    elif args.mode == "decrypt":
        with open(args.input, "r", encoding="utf-8") as f:
            b64_text = f.read()
        plain_text = decrypt_text_file(b64_text, args.key)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(plain_text)
        print("File decrypted and saved to", args.output)

if __name__ == "__main__":
    main()
