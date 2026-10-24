# 02 — Г-образная перегородка, OFFSET + PEDIT JOIN

**Цель:** одна замкнутая Г-образная `LWPOLYLINE` толщиной 90 мм, без осевой линии.

**Вход:** `axis_points` (не менее трёх точек, образующих угол), `width=90`, `side_left`, `side_right`.

**Последовательность:**
```json
{"command":"pline","params":{"vertices":[[0,0],[2000,0],[2000,1400]],"closed":false}}
{"command":"offset","params":{"handle":"${axis_handle}","distance":45,"side":"${side_left}"}}
{"command":"offset","params":{"handle":"${axis_handle}","distance":45,"side":"${side_right}"}}
{"command":"erase","params":{"handles":["${axis_handle}"]}}
```
Сохранить промежуточный DXF и прочитать **фактические начальные/конечные вершины** обеих смещённых полилиний. Затем выполнить:
```json
{"command":"line","params":{"points":["${left_start}","${right_start}"]}}
{"command":"line","params":{"points":["${left_end}","${right_end}"]}}
{"command":"pedit","params":{"handle":"${left_handle}","option":"join","handles2":["${right_handle}","${cap1_handle}","${cap2_handle}"],"fuzz":0.01,"convert":true}}
```

**Проверки:** ровно одна замкнутая полилиния перегородки, ноль оставшихся осевых/торцевых отдельных линий, ширина 90 мм на прямых участках, корректный наружный угол. Обновить handle после `pedit`.

**Следующий рецепт:** 03 — примыкания.

**Подтверждение:** `test_l_wall_closed.py`, `test_apartment_native_l_walls.py`.
