# Gdk9 Handbook (EN)

Gdk9 is a symbolic energy platform. It measures, transforms, and composes energy-preserving
operations over characters, numbers, and symbols. This handbook covers CLI usage, plugins,
rules, and best practices.

- Project: open, evolving. License: Proprietary (see `pyproject.toml`).
- Copyright: Adam Grange | adamgrange@proton.me

## 1. Concepts
- Digital root (1..9): Total energy reduces modulo 9; 9 represents the full cycle.
- Principle: Configuration for letter/number modes, weights, and `symbol_energy` mapping.
- Conservation: All implication rules conserve energy within tolerance.
- Rules: Fusion (many→one) and Split (one→two) with parameters; validated on apply.

## 2. Quick Start
- Analyze: `gdk9 an "Hello"` or profile: `gdk9 prof -f file.txt`
- Tokenize by energy-1 delimiters: `gdk9 tok "<a|b> c" -e 1 -F table`
- Attune to target 7: `gdk9 att -f file.txt -t 7 -m intersperse -a '.!?*' -I`
- Encode per-char energy: `gdk9 enc "Hi" -s annotate`
- Rules: define split: `gdk9 im ds HALVE L R 0.5`; apply: `gdk9 im ap HALVE X --commit`
- Plugins: `gdk9 pl list`, validate: `gdk9 pl validate ./plugins/example.yaml`,
  load: `gdk9 pl load ./plugins/example.yaml`

## 3. CLI Overview
- Global flags: `-P/--principle` (file), `-S/--state` (state.json), `-d/--debug`, `-C/--color`, `-N/--no-color`.
- Core commands: `an|analyze`, `prof|profile`, `asg|assign`, `att|attune`, `cmp|compare`,
  `enc|encode`, `dec|decode`, `sig|synthesize`, `tok|tokenize`, `prin|principles`, `opt|optimize`,
  `ui|tui`, `sym|symbol`, `im|imply`, `pl|plugin`, `sh|repl`.
- Help: `gdk9 help`, `gdk9 help plugin`, `gdk9 handbook` to print this guide.

## 4. Plugins
Plugins convert Gdk9 from a fixed engine into a modular platform.
- Locations: `./plugins/`, `~/.gdk9/plugins/`
- Formats: JSON/YAML or Python (`PLUGIN = {...}` literal only; parsed via AST, no exec)
- Auto-boot: enabled in `~/.gdk9/plugins.json`; loaded at CLI startup.
- Schema fields:
  - `name`, `version`, `description`
  - `symbol_energy`: merges into active principle
  - `symbols`: seeds named symbols in state
  - `rules`: list of `split` and `fusion` definitions
  - `checks`: optional energy-conservation tests at load
- Commands: `gdk9 pl list|validate|info|load|enable|disable` (see `docs/PLUGINS.md`).

## 5. Rules and Conservation
- Fusion: `arity >= 2`, output name can be `AUTO` (concatenate inputs).
- Split: `0 <= ratio <= 1`, outputs named `out_a`, `out_b`.
- Conservation: The engine validates in both fusion and split; plugins can add `checks` with input energies.

## 6. Attunement and Optimization
- Methods: `append`, `prepend`, `intersperse`, `substitute`, `edit`.
- Short flags: `-t` target, `-m` method, `-a` allowed symbols, `-s` max steps, `-p` spread, `-I` include text.
- Use `opt|optimize` to compute a plan without editing text.

## 7. State and Symbols
- State file: `~/.gdk9/state.json` or override with `-S path`.
- Manage: `gdk9 sym add NAME ENERGY`, `gdk9 sym ls`.
- List rules: `gdk9 im ls`.

## 8. Troubleshooting
- Invalid principle: `gdk9 prin validate --file my.json`.
- Plugin errors: `gdk9 pl validate <pack>` to get detailed schema/energy check failures.
- Set `-d` to enable debug logs.

---

# Руководство Gdk9 (RU)

Gdk9 — платформа «символической энергии». Она измеряет, преобразует и композиционно
применяет сохраняющие энергию операции над символами, числами и текстом.

- Проект: открытый, развивающийся. Лицензия: Proprietary (см. `pyproject.toml`).
- Авторское право: Adam Grange | adamgrange@proton.me

## 1. Концепции
- Цифровой корень (1..9): суммарная энергия сворачивается по модулю 9; 9 — полный цикл.
- Принцип: конфигурация режимов для букв/чисел, весов и карты `symbol_energy`.
- Сохранение энергии: все правила импликации сохраняют энергию в пределах допуска.
- Правила: «слияние» (многие→один) и «разделение» (один→два) с параметрами; проверяются при применении.

## 2. Быстрый старт
- Анализ: `gdk9 an "Hello"`; профиль: `gdk9 prof -f file.txt`
- Токенизация по разделителям энергии=1: `gdk9 tok "<a|b> c" -e 1 -F table`
- Настройка к цели 7: `gdk9 att -f file.txt -t 7 -m intersperse -a '.!?*' -I`
- Пометки энергий по символам: `gdk9 enc "Hi" -s annotate`
- Правила: split: `gdk9 im ds HALVE L R 0.5`; применить: `gdk9 im ap HALVE X --commit`
- Плагины: `gdk9 pl list`, проверка: `gdk9 pl validate ./plugins/example.yaml`,
  загрузка: `gdk9 pl load ./plugins/example.yaml`

## 3. Обзор CLI
- Глобальные флаги: `-P/--principle`, `-S/--state`, `-d/--debug`, `-C/--color`, `-N/--no-color`.
- Команды: `an|analyze`, `prof|profile`, `asg|assign`, `att|attune`, `cmp|compare`,
  `enc|encode`, `dec|decode`, `sig|synthesize`, `tok|tokenize`, `prin|principles`, `opt|optimize`,
  `ui|tui`, `sym|symbol`, `im|imply`, `pl|plugin`, `sh|repl`.
- Справка: `gdk9 help`, `gdk9 help plugin`, `gdk9 handbook` — вывод этого руководства.

## 4. Плагины
Плагины превращают Gdk9 из фиксированного движка в модульную платформу.
- Каталоги: `./plugins/`, `~/.gdk9/plugins/`
- Форматы: JSON/YAML или Python (`PLUGIN = {...}` только литерал; парсинг AST, без выполнения кода)
- Автозагрузка: `~/.gdk9/plugins.json`; включённые пакеты подхватываются при старте CLI.
- Схема:
  - `name`, `version`, `description`
  - `symbol_energy`: объединяется с активным принципом
  - `symbols`: начальные именованные символы в state
  - `rules`: список правил `split` и `fusion`
  - `checks`: опциональные проверки сохранения энергии при загрузке
- Команды: `gdk9 pl list|validate|info|load|enable|disable` (см. `docs/PLUGINS.md`).

## 5. Правила и сохранение
- Слияние: `arity >= 2`, имя результата может быть `AUTO` (конкатенация входов).
- Разделение: `0 <= ratio <= 1`, имена выходов: `out_a`, `out_b`.
- Сохранение энергии: ядро проверяет и для split, и для fusion; плагины могут добавлять `checks` с входными энергиями.

## 6. Настройка и оптимизация
- Методы: `append`, `prepend`, `intersperse`, `substitute`, `edit`.
- Короткие флаги: `-t`, `-m`, `-a`, `-s`, `-p`, `-I`.
- `opt|optimize` — вывести план без изменения текста.

## 7. Состояние и символы
- Файл состояния: `~/.gdk9/state.json` или `-S path`.
- Управление: `gdk9 sym add NAME ENERGY`, `gdk9 sym ls`.
- Правила: `gdk9 im ls`.

## 8. Диагностика
- Принцип: `gdk9 prin validate --file my.json`.
- Плагин: `gdk9 pl validate <pack>` — подробные ошибки схемы/энергии.
- `-d` — детальные логи.

