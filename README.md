# Add New Lore to the Black Brine Application

*A step-by-step authoring & wiring guide*

## 0) Quick principles

* **One file = one node** in the graph.
* Every file has **exactly one** `id` and **exactly one** `parent_location`.
* IDs are **canonical** (`bb:<namespace>:<slug>`) and never change once published.
* Many views require parents to list their children in **`child_locations`** as well as children pointing up via `parent_location`. Do both unless you know your viewer infers hierarchy automatically.
* Cross-page navigation is driven by **wiki links** in `related:` (e.g., `[[Little Sedna|bb:district:little-sedna]]`).

---

## 1) Pick the correct node type & ID

Choose the type:

* `district` – city sub-area (e.g., Little Sedna)
* `location` – place inside a district (tavern, temple, market)
* `site` – notable feature that isn’t a full district (Reefgate, Shipbreaker’s Yard)
* `lore` – hubs/overviews (e.g., Geography of Black Brine)
* `outskirts` – places beyond the city bounds
* `index` – curated lists/menus

Create a stable ID:

* Format: `bb:<namespace>:<kebab-slug>`

  * Examples:

    * `bb:district:little-sedna`
    * `bb:location:broadside-tavern`
    * `bb:lore:geography-black-brine`

**Do**

* lowercase
* hyphen-separate words
* keep short & permanent

**Don’t**

* use spaces or punctuation
* duplicate an existing id
* change ids after linking (breaks graphs)

---

## 2) Start from the right template

### A) District

```yaml
---
type: district
id: bb:district:<district-slug>
name: <District Name>
parent_location: bb:city:black-brine
location_type: district
tags: [district, black-brine]
child_locations: []   # add as you create children
---

# <District Name>

## Overview
<2–5 sentences>

## Notable Features
- <bullets>

## Connected Locations
- [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

### B) Location (inside a district)

```yaml
---
type: location
id: bb:location:<place-slug>
name: <Place Name>
parent_location: bb:district:<district-slug>
location_type: <tavern|temple|market|site|house>
maps_available: false
map_files: []
tags: [<district-slug>, <category>]
---

# <Place Name>

## Overview
<what it is & why it matters>

## Notable Features
- <bullets>

## Related
- [[<District Name>|bb:district:<district-slug>]]
- [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

### C) Lore hub (e.g., Geography)

```yaml
---
type: lore
id: bb:lore:<hub-slug>
name: <Hub Name>
parent_location: bb:city:black-brine
location_type: geography
tags: [lore, geography, black-brine]
child_locations: []   # list districts/sites this hub surfaces
---

# <Hub Name>

## Overview
<summary of the theme>

## Sections
- <outline or links>
```

### D) Site / Outskirts (non-district feature)

```yaml
---
type: site
id: bb:site:<site-slug>
name: <Site Name>
parent_location: bb:city:black-brine
tags: [site, <keywords>]
summary: <1–2 sentence summary>
related:
  - [[Geography of Black Brine|bb:lore:geography-black-brine]]
---
```

---

## 3) File creation & naming

* File name = **slug.md** or **slug.yaml.md** (whatever your system expects).
  Examples:

  * `little-sedna.md`
  * `broadside-tavern.md`
* Keep assets under a consistent root, e.g.:

  * `assets/maps/<slug>.jpg`
  * `assets/images/<slug>/<image>.png`

---

## 4) Wire the node into the graph (the important bit)

### Step 4.1 — Point **up** from the child

In your new file, set:

* `parent_location: bb:district:<name>` for locations
* `parent_location: bb:city:black-brine` for districts/lore hubs

### Step 4.2 — List the child **down** from the parent

Open the parent file and add your child ID to `child_locations:`.

**Example:** Adding Powder Keg to Salt Crown

```yaml
# Salt Crown (parent)
child_locations:
  - bb:location:powder-keg-tavern
  # keep other children…
```

### Step 4.3 — Add cross-links for navigation

Add `related:` blocks on both sides when helpful.

Child (Powder Keg):

```yaml
related:
  - [[Salt Crown|bb:district:salt-crown]]
  - [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

Parent (Salt Crown) – optional polish:

```yaml
related:
  - [[Powder Keg Tavern|bb:location:powder-keg-tavern]]
```

### Step 4.4 — Add to indexes/hubs

* **Districts Index**: add new districts
* **Geography hub**: keep `child_locations` current (districts + major sites)

---

## 5) Maps & media

If the node has a map or reference image:

```yaml
maps_available: true
map_files:
  - assets/maps/<slug>.jpg
```

* Use relative paths the viewer can serve.
* Keep filenames lowercase, hyphenated.
* Large images: prefer JPEG for maps; PNG for UI/line art.

---

## 6) Tagging for filters

* Always include the **district slug** on locations (`salt-crown`, `little-sedna`).
* Add a **category** tag (`tavern`, `temple`, `market`, `dock`, `ruin`, `faction`, etc.).
* Hubs: `geography`, `history`, `factions`.

Examples:

```yaml
tags: [salt-crown, tavern, brawls, explosives, smuggling]
tags: [little-sedna, temple, sedna, sea-goddess]
```

---

## 7) Validation checklist (before you refresh)

* Front-matter fences start with `---` (and end with `---` if required by your engine).
* Exactly **one** `id`; exactly **one** `parent_location`.
* Parent’s `id` **exactly matches** child’s `parent_location`.
* If your viewer needs it: parent has `child_locations` including the child.
* No stray spaces or hidden characters on id lines.
* Links use your engine’s wikilink format:

  * `[[Display Name|bb:namespace:slug]]` or `[[bb:namespace:slug]]`.

---

## 8) Refresh & test the graph

1. Save files.
2. Rebuild or refresh the viewer cache.
3. Click-through test:

   * City → Geography → District → Location → back to District → back to City.
4. If missing: recheck **IDs**, **parent/child wiring**, and **indexes**.

---

## 9) Worked examples

### Example A — Add a new district “Gallows Market”

1. Create `gallows-market.md`:

```yaml
---
type: district
id: bb:district:gallows-market
name: Gallows Market
parent_location: bb:city:black-brine
location_type: district
tags: [district, bazaar, contraband, magic]
child_locations: []
---

# Gallows Market

## Overview
Bazaar of stolen goods and illegal magic under watchful eyes.

## Connected Locations
- [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

2. Add to **City** (Black Brine) `child_locations` (if you list districts there).
3. Add to **Geography** hub `child_locations`.
4. Add to **Districts Index**.

### Example B — Add a location “Velvet Hammer” inside Gallows Market

1. Create `velvet-hammer.md`:

```yaml
---
type: location
id: bb:venue:velvet-hammer
name: Velvet Hammer
parent_location: bb:district:gallows-market
location_type: gambling-hall
tags: [gallows-market, gambling, brothel, thieves-guild]
---

# Velvet Hammer

## Overview
A thieves’ guild front—cards, favors, and markers that never die.

## Related
- [[Gallows Market|bb:district:gallows-market]]
- [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

2. Edit **Gallows Market**: add to `child_locations`.
3. (Optional) Add to a “Venues” index.

---

## 10) Troubleshooting (fast)

**Child not visible under parent**

* Parent file’s `id` ≠ child’s `parent_location`.
* Parent missing `child_locations` entry (add it).
* Duplicate `parent_location` keys (remove extras).
* Hidden whitespace: retype the id lines.

**Backlinks don’t click**

* Wrong wikilink syntax or target id doesn’t exist.
* Use `[[Display|bb:namespace:slug]]`.

**Map not loading**

* Wrong path or extension. Confirm `maps_available: true`.

**Geography hub not showing new entries**

* Forgot to add the node to `child_locations` on the hub.

---

## 11) Optional quality bar (nice to have)

* Add a `summary:` (1–2 lines) to sites/districts for list views.
* Keep **tone** consistent with Black Brine (salt, politics, occult tech).
* Maintain **crosslinks** between related factions/places so discovery feels rich.

---

## 12) Copy-paste snippet library

**Backlink to Geography**

```yaml
related:
  - [[Geography of Black Brine|bb:lore:geography-black-brine]]
```

**Register a child on a parent**

```yaml
child_locations:
  - bb:location:<child-id>
```

**Standard tags**

```yaml
tags: [<district-slug>, <category-1>, <category-2>]
```

---

## 13) Minimum viable steps (TL;DR)

1. Create file from correct **template** with unique `id`.
2. Set correct **`parent_location`**.
3. Add your node to parent’s **`child_locations`**.
4. Add **`related:`** links (parent + Geography).
5. (If used) register in indexes.
6. Refresh → click test.

---

If you want, tell me a few entries you plan to add next, and I’ll generate the exact ready-to-paste YAML files plus the corresponding parent/hub patches so you can drop them in with zero guesswork.
