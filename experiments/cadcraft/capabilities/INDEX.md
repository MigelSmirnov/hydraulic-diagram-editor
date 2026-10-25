# CADCraft — индекс операций

Опора для сценариев: что агент может вызвать и насколько этому можно верить.
Сценарии и граф собираются только из строк «проверено нами».

Источник: `storytold/cadcraft` @ `e86d895` (2026-10-25). CI собирает ветку `main` без пина,
поэтому прогон #71 мог идти на более раннем коммите. Пин коммита — критерий продвижения
в `CHECKPOINT.md`.

Статусы:
- **проверено нами** — тест в `experiments/cadcraft/`, зелёный в CI, проверка по DXF;
- **создаётся** — команда отработала в тесте, но результат проверен только счётом сущностей;
- **есть в CADCraft** — есть в каталоге команд (у части команд есть свои unit-тесты в upstream), нашим тестом не проверено;
- **нет** — в CADCraft отсутствует.

Все вызовы: MCP-инструмент `execute {command, params}`, если не указано иное.
Полный каталог с параметрами: инструмент `list_commands {filter?}`.

## Геометрия стен (проверено)

| Операция | Команда | Статус | Тест |
|---|---|---|---|
| Замкнутый контур | `pline {vertices, closed:true}` | проверено нами | `test_exterior_offset.py` |
| Смещение внутрь на толщину | `offset {handle, distance, side}` | проверено нами | `test_exterior_offset.py` |
| Г-стена 90 мм | `pline` ось → `offset` ±45 → `erase` ось → `line` торцы → `pedit join` | проверено нами | `test_l_wall_closed.py` |
| Разрыв полилинии на интервале | `break {handle, p1, p2}` | проверено нами | `test_break_junction.py` |
| Обрезка LINE по режущей | `trim {handle, pick, edges, mode}` | проверено нами | `test_junction_trim.py` |
| TRIM замкнутой полилинии | `trim` | не проверено | см. `recipes/03-wall-junction/branches.md` B4 |
| Стена мультилинией | `mlstyle` + `mline` | создаётся | `test_l_wall_tools.py` |
| Скругление/стык | `fillet {h1,p1,h2,p2,radius:0,trim}` | создаётся | `test_l_wall_tools.py` |

## Размеры и аннотации

| Операция | Команда | Статус | Тест |
|---|---|---|---|
| Масштаб размерных стилей 1:50 | `setvar DIMSCALE/DIMTXT/DIMASZ/DIMGAP` | проверено нами | `test_apartment_p01_integrated.py` |
| Линейный размер | `dimlinear {p1, p2, at}` | проверено нами (точки определения) | `test_apartment_p01_integrated.py` |
| Текст | `text {at, text, height}` | создаётся | `test_apartment_p01_integrated.py` |
| Штриховка стен / помещений | `hatch {points? \| handles?, pattern}` | есть в CADCraft | — |
| Площадь, периметр замкнутых контуров | `shapes {layer?, window?}` | есть в CADCraft | — |

## Слои — следующий шаг исследования

Сейчас мы только создаём слои (`layer.new`, во всех тестах). Видимость не проверялась.

| Операция | Команда | Статус |
|---|---|---|
| Создать / сделать текущим | `layer.new {name, color?, linetype?, lineweight?, current?}` | проверено нами |
| Вкл/выкл, заморозить, блокировать, печать | `layer.set {name, on?, frozen?, locked?, plot?, color?, …}` | есть в CADCraft |
| Сохранить набор видимости («сантехника», «электрика») | `layerstate.save {name}` | есть в CADCraft (unit-тест в upstream) |
| Восстановить набор | `layerstate.restore {name}` | есть в CADCraft (unit-тест в upstream) |
| Список / удаление / переименование наборов | `layerstate.list`, `.delete`, `.rename` | есть в CADCraft |
| Изолировать слой объекта / вернуть | `layiso {handles}` / `layuniso` | есть в CADCraft |
| Всё включить / разморозить | `layon`, `laythw` | есть в CADCraft |
| Перенести объекты на слой / слить слои | `laymch {handles, layer}`, `laymrg {from, to}` | есть в CADCraft |
| Кто использует слой / блок | `usage {type?}` | есть в CADCraft |

Открытые вопросы для пробного теста:
1. Влияют ли `on:false` / `frozen:true` на `plot` в PNG? Ожидание: скрытые слои не печатаются.
2. Сохраняются ли layer states в DXF и восстанавливаются ли после `open`?
3. Видят ли `query_entities` и `render` выключенные слои?
4. Нельзя заморозить текущий слой (это ошибка в коде) — сценарий должен сначала сменить текущий.

## Блоки и библиотека

| Операция | Команда | Статус | Тест |
|---|---|---|---|
| Блок из нарисованных сущностей | `block {name, base, handles, keep}` | проверено нами | `test_apartment_p01_integrated.py` |
| Вставка с поворотом | `insert {name, at, rotation, scale}` | проверено нами | `test_apartment_p01_integrated.py` |
| Список блоков | `blocks.list` | создаётся | `test_electrical_mcp.py` |
| Записать блок в отдельный файл | `wblock {path, name? \| handles?, base?}` | есть в CADCraft |  |
| Вставить блок **из файла** библиотеки | `insert {name, file, at, rotation?, scale?, attribs?}` | есть в CADCraft |  |
| Атрибуты блока (ширина проёма, марка) | `attdef {tag, prompt?, default?, at, height?, invisible?}`, `insert … attribs:{TAG: value}` | есть в CADCraft |  |
| Подменить блок во всех вставках | `blockreplace` | есть в CADCraft |  |
| Подложка из другого чертежа (xref) | `xattach {path, overlay?, at?}` | есть в CADCraft |  |
| Динамический блок: **читать и менять** готовый | `blocks.dynamic`, `blocks.reference.set`, `blocks.reference.grip` | есть в CADCraft |  |
| Динамический блок: **создать** | — | **нет** (upstream `docs/gaps.md`, F3: нет авторинга параметров и действий) |  |

## Проверка результата

| Операция | Инструмент | Статус |
|---|---|---|
| Сохранить DXF и перечитать через ezdxf | `save` + Python | проверено нами (основной способ) |
| PNG на белом листе | `plot {path, output:"png", …}` | проверено нами (сигнатура PNG, не содержимое) |
| Сводка чертежа | `inspect_drawing {entities?}` | создаётся |
| Сущности по слою/окну с геометрией | `query_entities {type?, layer?, window?}` | есть в CADCraft |
| PNG фрагмента | `render {window?}` | есть в CADCraft |
| Найти тексты | `find_text {contains?, layer?}` | есть в CADCraft |
