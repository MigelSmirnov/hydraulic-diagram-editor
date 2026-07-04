# Редактор гидравлических схем

Визуальный редактор простых бытовых гидравлических схем.
Текущая версия: полотно, палитра элементов, портовые соединения, свойства,
JSON save/load, autosave, PNG export и CAD-style быстрые действия.

**Стек:** React · TypeScript · Vite · React Flow · Zustand · html-to-image · без backend.

---

## 1. Как запустить локально

```bash
npm install
npm run dev
```

Vite выведет адрес (обычно `http://localhost:5173`). Открой его в браузере.

Сборка продакшн-версии:

```bash
npm run build      # проверка типов + сборка в dist/
npm run preview    # локальный просмотр собранной версии
```

MCP-сервер для агентского редактирования JSON-схем:

```bash
npm run mcp
```

Подробнее: [`docs/mcp.md`](docs/mcp.md). Готовые промпты для проверки MCP:
[`docs/agent-prompts.md`](docs/agent-prompts.md). Пример схемы, созданной в агентском
формате: [`examples/mcp/boiler-agent-diagram.json`](examples/mcp/boiler-agent-diagram.json).
Для PNG-рендера через MCP установи браузер Playwright один раз:

```bash
npx playwright install chromium
```

Требуется Node.js 18+.

### Что уже умеет

- Добавление элементов перетаскиванием из палитры на полотно.
- Короткий **ПКМ** по пустому полотну повторяет добавление последнего элемента.
- Длинный **ПКМ** по элементу открывает меню действий: повернуть / удалить.
- Перемещение и масштабирование элементов.
- Соединение элементов линиями (тянуть от точки подключения к точке).
  Точки подключения задаются в каталоге элементов; направление соединения свободное
  (`ConnectionMode.Loose`).
- Удаление выбранного элемента или линии клавишей **Delete** / **Backspace**.
- Сетка — отключаемая, **по умолчанию выключена** (кнопка «Показать сетку»).
- Привязка к сетке — вкл/выкл.
- Undo / redo для командных действий и перемещения drag'ом.
- Очистка полотна и загрузка демо-шаблона.
- Save / Load JSON.
- Autosave в `localStorage`, чтобы refresh/HMR/dev-server restart не стирали схему.
- Export PNG.
- Панель свойств: id / тип / название выбранного элемента или линии; смена типа линии.

---

## 2. Какие файлы за что отвечают

Полное описание — в [`docs/architecture.yaml`](docs/architecture.yaml). Кратко:

```
src/
  app/
    App.tsx                     Оболочка приложения — только композиция layout, без логики
    providers/AppProviders.tsx  Глобальные провайдеры (ReactFlowProvider)
  features/diagram-editor/
    components/
      DiagramAutosave.tsx        restore/save autosave через localStorage
      DiagramCanvas.tsx          <ReactFlow>, drag-drop, ПКМ repeat, сетка, привязка, Delete
      Palette.tsx                Левая палитра элементов (draggable)
      Toolbar.tsx                Верхняя панель: сетка, JSON, PNG export, undo/redo, демо
      PropertiesPanel.tsx        Правая панель свойств
    nodes/
      HydraulicNode.tsx          Единый узел для всех элементов + long-ПКМ action menu
      nodeTypes.ts               Реестр типов узлов React Flow
    edges/
      HydraulicEdge.tsx          Ортогональная линия, цвет/стиль из типа линии
      edgeTypes.ts               Реестр типов линий React Flow
    export/
      exportPng.ts               Экспорт текущей схемы в PNG
      index.ts                   Публичная граница export-модуля
    model/
      types.ts                   Все доменные типы
      elementCatalog.ts          ⬅ ИСТОЧНИК ПРАВДЫ по элементам
      lineTypes.ts               ⬅ ИСТОЧНИК ПРАВДЫ по типам линий
      templates.ts               ⬅ ИСТОЧНИК ПРАВДЫ по шаблонам
      diagramDocument.ts         JSON-формат схемы + schemaVersion
      diagramValidation.ts       Проверка загружаемой схемы
    persistence/
      diagramJson.ts             Save/load JSON
      diagramAutosave.ts         Autosave/restore localStorage
      index.ts                   Публичная граница persistence-модуля
    store/
      diagramStore.ts            Zustand-хранилище: nodes, edges, настройки, undo/redo
      diagramCommands.ts         Тестируемые команды редактора
      diagramHistory.ts          Undo/redo snapshots
    utils/
      createNode.ts              Элемент каталога → узел React Flow
      edgeRouting.ts             Ортогональная маршрутизация линий
      portGeometry.ts            Поворот портов и размеров символа
  shared/
    ui/PropertyRow.tsx           Переиспользуемая строка «label / value»
    icons/*Icon.tsx              Чистые SVG-иконки (без бизнес-логики)
    icons/index.ts               Реестр иконок
  lib/
    id.ts                        Генератор уникальных id
  mcp/
    diagramFile.ts               Файловые команды MCP для JSON-схем
    server.ts                    stdio MCP-сервер
docs/
  architecture.yaml              Зоны ответственности модулей + правила + roadmap
  adding-elements.md             Правила добавления элементов
  mcp.md                         Запуск и tools MCP-сервера
  agent-prompts.md               Готовые промпты для проверки MCP-агента
  invariants.md                  Архитектурные инварианты
  skill-compliance-plan.md       План соответствия skills
examples/
  mcp/boiler-agent-diagram.json  Пример схемы для Load JSON / MCP
architecture/
  app-architecture.yaml          Машинно-читаемый граф модулей
tests/
  diagram-editor/*.test.ts       Unit-тесты команд, геометрии, validation, autosave
```

Ключевое правило архитектуры: **вся логика редактора живёт в `features/diagram-editor`
и проходит через `diagramStore`**. `App.tsx` ничего не знает о гидравлике.

---

## 3. Как добавить новый элемент в палитру

1. Нарисуй иконку: `src/shared/icons/MyThingIcon.tsx` (чистый SVG, `stroke="currentColor"`).
2. Зарегистрируй её в `src/shared/icons/index.ts` под строковым ключом:
   ```ts
   'my-thing': MyThingIcon,
   ```
3. Добавь запись в `src/features/diagram-editor/model/elementCatalog.ts`:
   ```ts
   {
     type: 'my-thing',
     label: 'Моя железка',
     category: 'valves',            // одна из categories
     icon: 'my-thing',              // ключ из реестра иконок
     defaultSize: { width: 72, height: 72 },
     ports: [
       { id: 'inlet', label: 'Вход', side: 'left', direction: 'left', x: 0, y: 36, kind: 'inlet' },
       { id: 'outlet', label: 'Выход', side: 'right', direction: 'right', x: 72, y: 36, kind: 'outlet' },
     ],
   }
   ```

Всё. Палитра, узел на полотне и панель свойств подхватят элемент автоматически —
новый компонент писать не нужно.

Подробные правила по SVG, портам и общей оси фитингов — в
[`docs/adding-elements.md`](docs/adding-elements.md).

---

## 4. Как добавить новый тип линии

1. В `src/features/diagram-editor/model/lineTypes.ts` добавь запись:
   ```ts
   {
     id: 'pipe_example',
     label: 'Пример',
     category: 'water',
     visualStyle: 'solid',
     color: '#dc2626',
     strokeWidth: 2,
     description: 'Описание линии.',
   },
   ```
2. Если порт должен принимать только конкретные линии, укажи `allowedLineTypes`
   в `elementCatalog.ts`.

Линия рисуется единым `HydraulicEdge`, который берёт цвет/толщину/пунктир из типа —
менять код рендера не нужно.

Активный тип линии выбирается в тулбаре; новые соединения создаются этим типом.

---

## 5. Следующие шаги (рекомендованный порядок)

1. **Редактируемые свойства** — переименование элемента прямо в `PropertiesPanel`.
2. **Проверка схемы** — правила допустимых соединений, обязательные элементы.
3. **Экспорт SVG / PDF** — PNG уже реализован.
4. **Расширение домена** — ГВС, солнечный контур, водоочистка: новые категории
   в `elementCatalog.ts` и типы линий в `lineTypes.ts`, без переписывания ядра.
5. **Чистая доменная модель** — постепенно отделить durable diagram model от React Flow `Node`/`Edge`.
6. **Ограничение истории** — лимит undo/redo snapshots.

Осознанно **не** входит сейчас: расчёты, полноценная проверка схемы,
водоочистка как отдельный доменный блок, backend, авторизация.
