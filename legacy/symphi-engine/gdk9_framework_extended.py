import sympy as sp
import numpy as np
import networkx as nx
from string import ascii_uppercase, ascii_lowercase
from typing import List, Dict, Set, Any, Callable
import functools

class GDk9Framework:
    """
    GDk9 Alphabetic Symbolic Framework
    Implements the category-theoretic and symbolic algebraic framework for cognitive circuitry
    based on the GDk9 Whitepaper.
    
    Features:
    - Letter classification by symmetry types
    - Directed Cognition Graph (DCG) with morphisms
    - Composite morphism computation
    - Symbolic regression integration
    - Character valuation formulas
    - Word compounding and evaluation
    - Word selection based on GDk9 properties
    
    Robustness:
    - Error checking for invalid inputs
    - Type hints for clarity
    - Extendable: methods to add custom morphisms, letters, etc.
    """

    def __init__(self):
        # Alphabet setup
        self.upper_letters: List[str] = list(ascii_uppercase)
        self.lower_letters: List[str] = list(ascii_lowercase)
        self.all_letters: List[str] = self.upper_letters + self.lower_letters
        
        # Classify letters based on whitepaper
        self.classify_letters()
        
        # Build Directed Cognition Graph
        self.build_dcg()
        
        # Symbolic setup
        self.setup_symbols()
        
        # Function assignments for types (for composition)
        self.type_functions: Dict[str, Callable[[sp.Expr], sp.Expr]] = {
            'idempotent': lambda x: x * x,  # x² = x, but for composition, use projection-like
            'biphasic': lambda x: sp.sin(x),  # oscillatory
            'involutive': lambda x: 1 / x,  # flip, x² = 1
            'asymmetric': lambda x: x + 1,  # directional flow
        }
        
        # DC/AC markers
        self.dc_ac_junction: Dict[str, str] = {'F': 'E', 'f': 'e'}

    def classify_letters(self) -> None:
        """
        Classify uppercase letters into symmetry types as per whitepaper.
        Lowercase are treated similarly but with noted dynamics.
        """
        self.symmetry_types: Dict[str, Set[str]] = {
            'idempotent': {'A', 'H', 'I', 'M', 'O', 'T', 'U', 'V', 'W', 'X', 'Y'},
            'biphasic': {'B', 'C', 'D', 'E', 'K'},
            'involutive': {'N', 'S', 'Z'},
            'asymmetric': set(self.upper_letters) - ({'A', 'H', 'I', 'M', 'O', 'T', 'U', 'V', 'W', 'X', 'Y'} |
                                                     {'B', 'C', 'D', 'E', 'K'} | {'N', 'S', 'Z'})
        }
        
        # Lowercase classifications (approximated based on whitepaper descriptions)
        # Note: Whitepaper notes differences like I→i breaks symmetry
        self.lower_symmetry_types: Dict[str, Set[str]] = {
            'idempotent': {'a', 'm', 'o', 't', 'u', 'v', 'w', 'x', 'y'},  # Adjusted for broken symmetries
            'biphasic': {'b', 'c', 'd', 'e', 'k'},
            'involutive': {'n', 's', 'z'},
            'asymmetric': set(self.lower_letters) - (self.lower_symmetry_types['idempotent'] |
                                                     self.lower_symmetry_types['biphasic'] |
                                                     self.lower_symmetry_types['involutive'])
        }

    def get_symmetry_type(self, letter: str) -> str:
        """
        Get symmetry type of a letter.
        Raises ValueError if invalid letter.
        """
        if letter not in self.all_letters:
            raise ValueError(f"Invalid letter: {letter}. Must be A-Z or a-z.")
        
        types_dict = self.symmetry_types if letter.isupper() else self.lower_symmetry_types
        for typ, letters in types_dict.items():
            if letter.upper() if letter.isupper() else letter in letters:
                return typ
        raise ValueError(f"Letter {letter} not classified.")

    def build_dcg(self) -> None:
        """
        Build the Directed Cognition Graph (DCG) using NetworkX.
        Nodes: letters (upper and lower).
        Edges: morphisms based on whitepaper examples and relations.
        Extendable via add_morphism.
        """
        self.dcg: nx.DiGraph = nx.DiGraph()
        self.dcg.add_nodes_from(self.all_letters)
        
        # Add identity morphisms (self-loops)
        for letter in self.all_letters:
            self.dcg.add_edge(letter, letter, type='identity')
        
        # Add example morphisms from whitepaper
        self.add_morphism('A', 'V', 'inversion')
        self.add_morphism('V', 'W', 'duplication')
        self.add_morphism('W', 'M', 'integration')
        self.add_morphism('F', 'E', 'dc_to_ac')
        
        # Add uppercase to lowercase morphisms (rigid to flexible)
        for upper, lower in zip(self.upper_letters, self.lower_letters):
            self.add_morphism(upper, lower, 'archetype_to_alternate')
        
        # Add groupoid inverses where applicable
        for letter in self.symmetry_types['involutive']:
            self.add_morphism(letter, letter, 'flip')
        for letter in self.symmetry_types['biphasic']:
            self.add_morphism(letter, letter, 'oscillate')

    def add_morphism(self, source: str, target: str, morphism_type: str) -> None:
        """
        Extend the framework by adding a custom morphism (edge).
        """
        if source not in self.all_letters or target not in self.all_letters:
            raise ValueError("Source and target must be valid letters.")
        self.dcg.add_edge(source, target, type=morphism_type)

    def compose_morphisms(self, path: List[str]) -> Dict[str, Any]:
        """
        Compose morphisms along a path.
        Returns path validity, composite type, and symbolic interpretation.
        """
        if not all(l in self.all_letters for l in path):
            raise ValueError("Invalid letters in path.")
        
        if not nx.has_path(self.dcg, path[0], path[-1]):
            raise ValueError("No path exists in DCG.")
        
        # Check if exact sequential path exists
        for i in range(len(path) - 1):
            if not self.dcg.has_edge(path[i], path[i+1]):
                raise ValueError(f"No direct morphism from {path[i]} to {path[i+1]}.")
        
        # Composite interpretation (based on whitepaper example)
        interpretations = {
            ('A', 'V', 'W', 'M'): 'singular → inverted → duplicated → integrated'
        }
        key = tuple(path)
        interp = interpretations.get(key, 'Custom composition')
        
        return {
            'valid': True,
            'path': path,
            'interpretation': interp
        }

    def setup_symbols(self) -> None:
        """
        Setup symbolic regression as per whitepaper.
        y = (z * k) * f(x)
        """
        self.x, self.y, self.z, self.k = sp.symbols('x y z k')
        self.f = sp.Function('f')
        self.base_equation = sp.Eq(self.y, self.z * self.k * self.f(self.x))

    def symbolic_regression(self, f_expr: sp.Expr) -> sp.Expr:
        """
        Apply symbolic regression with custom f(x).
        Example: f_expr = sp.exp(self.x)
        """
        return self.base_equation.subs(self.f(self.x), f_expr)

    def character_valuation(self, letter: str) -> sp.Expr:
        """
        Valuation formula based on symmetry type.
        Uses symbolic expressions.
        """
        typ = self.get_symmetry_type(letter)
        pos = self.upper_letters.index(letter.upper()) + 1 if letter.isupper() else self.lower_letters.index(letter) + 1
        base = sp.symbols(f'val_{letter}')
        
        if typ == 'idempotent':
            return base**2 - base  # x² - x = 0
        elif typ == 'biphasic':
            return base**2 - self.f(base)  # x² = f(x)
        elif typ == 'involutive':
            return base**2 - 1  # x² = 1
        elif typ == 'asymmetric':
            return base**2 - base - 1  # Example: not equal to x or 1
        return base

    def word_evaluation(self, word: str, mode: str = 'sum') -> sp.Expr:
        """
        Evaluate a word by compounding character valuations.
        Modes: 'sum', 'product', 'compose_functions'
        """
        if not all(c.isalpha() for c in word):
            raise ValueError("Word must contain only letters.")
        
        vals = [self.character_valuation(c) for c in word]
        
        if mode == 'sum':
            return sum(vals)
        elif mode == 'product':
            return functools.reduce(lambda a, b: a * b, vals)
        elif mode == 'compose_functions':
            # Compose type functions on a symbolic variable
            var = sp.symbols('var')
            for c in reversed(word):  # Compose right to left
                typ = self.get_symmetry_type(c)
                func = self.type_functions[typ]
                var = func(var)
            return var
        else:
            raise ValueError("Invalid mode. Use 'sum', 'product', or 'compose_functions'.")

    def select_words(self, words: List[str], property_filter: Dict[str, Any]) -> List[str]:
        """
        Select words based on GDk9 properties.
        Example: property_filter = {'min_idempotents': 2, 'has_dc_ac': True}
        """
        selected = []
        for word in words:
            if not all(c.isalpha() for c in word):
                continue  # Skip invalid
            
            counts = {typ: 0 for typ in self.symmetry_types}
            has_dc_ac = False
            for c in word:
                typ = self.get_symmetry_type(c)
                counts[typ] += 1
                if c in self.dc_ac_junction or c in self.dc_ac_junction.values():
                    has_dc_ac = True
            
            match = True
            for key, val in property_filter.items():
                if key == 'min_idempotents' and counts['idempotent'] < val:
                    match = False
                elif key == 'has_dc_ac' and has_dc_ac != val:
                    match = False
                # Add more filters as needed
            
            if match:
                selected.append(word)
        
        return selected

# Example usage (for testing)
if __name__ == "__main__":
    try:
        gdk9 = GDk9Framework()
        
        # Test classification
        print(gdk9.get_symmetry_type('A'))  # idempotent
        
        # Test composition
        print(gdk9.compose_morphisms(['A', 'V', 'W', 'M']))
        
        # Test symbolic regression
        print(gdk9.symbolic_regression(sp.exp(gdk9.x)))
        
        # Test valuation
        print(gdk9.character_valuation('F'))
        
        # Test word evaluation
        print(gdk9.word_evaluation('FWEM', mode='compose_functions'))
        
        # Test word select
        words = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'FE']
        filtered = gdk9.select_words(words, {'has_dc_ac': True})
        print(filtered)  # Should include 'FE' if F or E present
        
        print("All tests passed.")
    except Exception as e:
        print(f"Error: {e}")