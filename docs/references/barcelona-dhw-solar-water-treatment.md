# Barcelona DHW, recirculation, solar and water-treatment references

This document is a working reference index for designing domestic hot-water
(DHW/ACS) hydraulic diagrams for a house in Barcelona, Spain.

It is not a legal design report. Use it as a source map and engineering checklist
before generating diagrams with the MCP agent.

---

## Project context

Target system:

- Domestic hot-water system with indirect boiler.
- Boiler heated by a solar thermal collector located on the roof.
- Technical room located in the basement.
- DHW distribution to three consumer branches:
  - first floor kitchen;
  - first floor bathroom;
  - second floor bathroom.
- DHW recirculation from all three branches into one recirculation manifold.
- Cold-water inlet includes water treatment / filtration before the boiler.
- Water meter is out of scope for this diagram.

---

## Primary Spanish references

### 1. CTE DB HS 4 — Suministro de agua

URL:
https://www.codigotecnico.org/pdf/Documentos/HS/DBHS.pdf

Why it matters:

- Main Spanish building-code reference for water supply installations.
- Includes cold-water supply, ACS distribution, return/recirculation and water-treatment requirements.

Design notes for this project:

- Use HS 4 as the main reference for the sanitary-water side of the diagram.
- For ACS, the document states that hot-water installations use conditions analogous to cold-water networks.
- A return network is required when the length of the supply pipe to the farthest consumption point is 15 m or more.
- Return networks should run parallel to supply networks.
- For risers/montantes, the return should be taken from the upper part and below the last private branch.
- Balancing valves should be represented on return branches where the diagram shows branch recirculation.
- Water-treatment systems should be bypassable / maintainable so temporary shutdown of treatment does not interrupt the building water supply.
- Water-treatment systems should include measuring devices to verify treatment effectiveness.

Relevant sections to revisit:

- HS 4, section 3.2.1.6 — Sistemas de tratamiento de agua.
- HS 4, section 3.2.2.1 — ACS distribution and return.
- HS 4, pressure limits at consumption points.

Diagram impact:

- Draw the cold-water treatment block with service isolation / bypass logic if the catalog supports it.
- Do not include the water meter in this project unless explicitly requested.
- Draw a DHW supply manifold and a DHW recirculation manifold.
- Add balancing valves on the recirculation branches where possible.

---

### 2. CTE DB HE 4 — Renewable contribution for ACS

URL:
https://www.codigotecnico.org/pdf/Documentos/HE/DBHE.pdf

Why it matters:

- Spanish energy-code reference for renewable energy contribution to domestic hot water.
- Relevant because the project uses a roof solar collector to heat the indirect boiler.

Design notes for this project:

- Use HE 4 as the energy-context reference for the solar thermal part of the diagram.
- The diagram should keep the solar primary circuit visually separate from potable DHW.
- Use separate line types for solar supply and solar return.
- Show the collector on the roof and the boiler / technical room in the basement.
- Show solar circulation pump and expansion tank in the solar loop when possible.

Relevant sections to revisit:

- HE 4 — Contribución mínima de energía renovable para cubrir la demanda de agua caliente sanitaria.

Diagram impact:

- Layout should make the solar loop clear: roof collector -> solar supply -> boiler coil -> solar return -> collector.
- The boiler is the interface between the solar thermal circuit and the potable-water/DHW circuit.

---

### 3. RITE — Reglamento de Instalaciones Térmicas en los Edificios

URL:
https://www.boe.es/buscar/act.php?id=BOE-A-2007-15820

Why it matters:

- Spanish regulation for thermal installations in buildings.
- Includes installations for production of domestic hot water (ACS), safety, efficiency, maintenance and documentation.

Design notes for this project:

- RITE points back to CTE HE 4 and CTE HS 4 for ACS dimensioning references.
- For the diagram, this means the hydraulic schematic should clearly separate:
  - potable cold water / DHW;
  - solar thermal primary loop;
  - recirculation loop;
  - service and maintenance elements.
- Maintenance-relevant devices should be visible where the catalog supports them: filters, valves, expansion vessel, safety devices, treatment unit, pumps.

Relevant sections to revisit:

- Article 1 — purpose: safety and energy efficiency of thermal installations.
- Article 2 — scope includes ACS production.
- IT 1.2.4.1.2.4 — preparation of hot water for sanitary uses.
- Preventive maintenance table, including water-treatment systems, filters and ACS preparation.

Diagram impact:

- Draw the scheme so the technical-room equipment is maintainable and readable.
- Include valves around pumps/treatment elements when we decide to expand detail.

---

### 4. Real Decreto 487/2022 — Legionella prevention and control

URL:
https://www.boe.es/buscar/act.php?id=BOE-A-2022-10297

Why it matters:

- Spanish sanitary regulation for prevention and control of legionellosis.
- Relevant because DHW accumulation and recirculation can create Legionella risk if badly designed or maintained.

Design notes for this project:

- Avoid dead legs and stagnant zones in the conceptual diagram.
- Recirculation is a positive design feature for long DHW distribution branches, but it should be balanced.
- Accumulator / indirect boiler should be represented as inspectable/maintainable equipment.
- For private dwelling scope, check applicability carefully with a qualified local professional, but still use the principles as good design practice.

Relevant sections to revisit:

- Preamble: Legionella proliferation factors include temperature variation, stagnation, biofilm, limescale and corrosion.
- Article 1 and Article 2: object and definitions.
- Annexes concerning water systems and ACS.
- Measures mentioning ACS service temperature ranges and cleaning/disinfection logic.

Diagram impact:

- Show recirculation returning all three branches, not a single blind-ended DHW branch.
- Show balancing on recirculation branches.
- Do not create unnecessary dead-end stubs in the generated scheme.

---

## Barcelona-specific water considerations

### Water hardness / limescale

Barcelona-area domestic water is commonly treated by installers as hard or limescale-prone, but the exact hardness should be confirmed for the specific address or supply zone using the local supplier water-quality data.

Working assumption for this project:

- Include filtration / water-treatment before the boiler.
- Do not specify exact softener size or chemistry in the diagram until real water-quality values are known.
- Avoid making claims about required treatment without a local water analysis or supplier data.

Sources to find / add later:

- Aigües de Barcelona water-quality page for the exact address or supply zone.
- Any downloadable water analysis report listing hardness, conductivity, pH, calcium and magnesium.

Diagram impact:

- For now, draw water treatment as a functional block or available catalog component.
- Add bypass / isolation concept around the water-treatment block if possible.
- Exclude the water meter from the diagram because it is outside project scope.

---

## Current editor catalog mapping

Current pushed catalog findings:

- `water-connection` — cold-water connection point.
- `filter` — available in category `treatment`; has inlet, outlet and drain ports.
- `pressure-reducer` — available valve for cold water.
- `water-meter` — available, but out of scope for this project.
- `indirect-boiler` — available; currently has cold inlet, hot outlet, solar coil ports and drain.
- `solar-collector` — available.
- `circulation-pump` — available.
- `expansion-tank` — available.
- `balancing-valve` — available.
- `junction` — available and can temporarily emulate simple manifolds.

Potential catalog gaps for this project:

- Dedicated DHW supply manifold, 1 inlet + 3 outlets.
- Dedicated DHW recirculation manifold, 3 inlets + 1 outlet.
- Dedicated water-treatment block if we do not want to represent treatment only as a filter.
- Dedicated consumer/end-use node for kitchen and bathrooms.
- Dedicated DHW recirculation return port on the indirect boiler.

---

## Initial design decisions for the first generated diagram

1. Do not draw a water meter.
2. Draw water treatment before the boiler on the cold-water inlet side.
3. Draw three DHW branches:
   - `Кухня 1 эт.`
   - `С/У 1 эт.`
   - `С/У 2 эт.`
4. Draw three recirculation returns, one from each branch.
5. Collect the three recirculation returns into a return manifold.
6. Add balancing valves on the three recirculation returns if layout remains readable.
7. Add a recirculation pump after the return manifold and before the boiler return point.
8. Keep roof solar collector and basement technical room visually separated.
9. Use separate line types for:
   - cold water;
   - hot water;
   - DHW recirculation;
   - solar supply;
   - solar return;
   - drain.
10. Treat this as a functional hydraulic scheme, not a construction drawing or final legal design.

---

## Next engineering tasks

1. Confirm exact water-treatment element in the current local library if it differs from the pushed GitHub catalog.
2. Decide whether to add dedicated manifold elements before asking the MCP agent to generate the final diagram.
3. Decide how to model DHW consumer endpoints: connection nodes, junctions, or new catalog elements.
4. Decide how recirculation returns to the boiler: temporary junction near cold inlet, or add a dedicated boiler port.
5. Add Aigües de Barcelona address-specific water-quality link/report when available.
