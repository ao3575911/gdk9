import sys
from gdk9_core_engine import ImplicationEngine
from gdk9_framework import word_energy

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <word>")
        sys.exit(1)
    word = sys.argv[1]
    engine = ImplicationEngine()
    reading = engine.read(word)
    print(f"Energy: {reading['energy']:.2f}")
    print(f"Classes: {reading['classes']}")
    print(f"Vector: {reading['vector_sum']}")
    print(f"Conserved: {engine.validate_conservation(word)}")
