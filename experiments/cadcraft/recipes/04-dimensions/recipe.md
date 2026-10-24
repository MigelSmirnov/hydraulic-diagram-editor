# 04 — Размерные цепочки по граням

**Цель:** настоящие CAD-объекты `DIMENSION`, точки которых совпадают с проверенными гранями стен.

**Вход:** координаты граней, точки размещения размерных линий, профиль аннотаций.

**Команды:**
```json
{"command":"setvar","params":{"name":"DIMSCALE","value":50}}
{"command":"setvar","params":{"name":"DIMTXT","value":2.5}}
{"command":"setvar","params":{"name":"DIMASZ","value":2.5}}
{"command":"setvar","params":{"name":"DIMGAP","value":1.0}}
{"command":"layer.new","params":{"name":"DIMENSIONS","current":true}}
{"command":"dimlinear","params":{"p1":[0,0],"p2":[3520,0],"at":[1760,-500]}}
{"command":"dimlinear","params":{"p1":[3520,0],"p2":[3610,0],"at":[3565,-750]}}
{"command":"dimlinear","params":{"p1":[3610,0],"p2":[8382,0],"at":[5996,-500]}}
```

**Результат:** цепочка 3520 + 90 + 4772 = 8382 мм в **экспериментальной** геометрии.

**Проверки:** `DIMENSION` существует в DXF, `defpoint2/defpoint3` совпадают с гранями, сумма цепочки совпадает с общей шириной. Нельзя подменять исходные обмеры 3565/100/4717 без согласования. `fit=true` при печати не гарантирует масштаб 1:50.

**Следующий рецепт:** 05 — розетки.

**Подтверждение:** `test_apartment_p01_integrated.py`, `test_apartment_mcp.py`.
