class SymbolRegistry:
    def __init__(self):
        self.name_to_id = {}
        self.id_to_name = []
        self.idempotent = []
        self.default_phase = []

    def register(self, name: str, idempotent: bool = False, default_phase: int = 0) -> int:
        if name not in self.name_to_id:
            idx = len(self.id_to_name)
            self.name_to_id[name] = idx
            self.id_to_name.append(name)
            self.idempotent.append(bool(idempotent))
            self.default_phase.append(int(default_phase))
        return self.name_to_id[name]

    def get_id(self, name: str) -> int:
        return self.name_to_id[name]

    def get_or_register(self, name: str, idempotent: bool = False, default_phase: int = 0) -> int:
        if name not in self.name_to_id:
            return self.register(name, idempotent, default_phase)
        return self.name_to_id[name]

    def is_idempotent(self, symbol_id: int) -> bool:
        return self.idempotent[symbol_id]

    def get_default_phase(self, symbol_id: int) -> int:
        return self.default_phase[symbol_id]

    def set_idempotent(self, name: str):
        idx = self.get_or_register(name)
        self.idempotent[idx] = True

    def set_default_phase(self, name: str, phase: int):
        if phase not in (0, 1):
            raise ValueError(f"Invalid default phase value for symbol {name}: {phase}")
        idx = self.get_or_register(name)
        self.default_phase[idx] = int(phase)