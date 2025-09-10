---
type: campaign
id: bb:campaign:deep-green:skull-garden
name: The Deep Green - Part 1
summary: 'Sy, Franklin, and Pinch journey upriver aboard Rupert’s chartered fishing
  boat. Guided by Strange Bones, they reach a ruined barricade where the river is
  blocked and must continue on foot. On the sandy bank lies the Skull Garden, where
  carnivorous vines and scavengers await.

  '
location: bb:river:black-river
participants:
- bb:npc:franklin-pierce
- bb:npc:pinch
- bb:npc:rupert-richthorn
- bb:npc:strange-bones
- bb:npc:sy
factions:
- bb:faction:the-soiled
tags:
- encounter
- jungle
- black-river
---
# Act I – Up River
- Travel pace: 6 hours/hex, 3 hex/day
- Weather tables:
  - Dense Jungle Fog: ranged disadvantage, perception disadvantage, encounter chance +1
  - Jungle Silence: stealth advantage, encounter DC lowered
- Minor encounters:
  - Twisting currents force navigation or capsizing
  - Pod of river spirits vanish if spoken to
  - Floating fungal mats cause mild hallucinations

# Act II – River Barricade
- The Soiled have collapsed ruins, forcing the raft aground.
- PCs encounter the Skull Garden.

# Skull Garden Encounter
**Atmosphere**
- Left bank: vine-choked ruins, obelisk, silent jungle birds.
- Right bank: sandy beach, half-buried skull tangled in flowering vines, armored corpse.

**Hazards**
- False Beauty Vines (CR 3 plant hazard). Lure with blossoms, grapple and drag prey.
- Opportunists: Ravethings (CR ½ scavengers) wait to strike restrained targets.

**Tactics**
- Vines activate when approached.
- Ravethings rush in during chaos, drag bodies away, attempt to sink raft.

**Treasure**
- Armored corpse: Ritual mask of the Hollow Song (AC +1, induces nightmares).
- Scroll fragment: ancient map to the Temple of the Hollow Song.
- Sword “Final Verse” (see item entry).

# Lore Clues
- Skull carvings reference “The First Hunger.”
- Scroll fragment “The Fifth Mouth Never Closes” describes vines feeding on voice.
- True name of ship: “The Fifth Mouth,” linked to a forgotten sea god.

# Stat Blocks
## False Beauty Vines
type: hazard
id: bb:creatures:false-beauty-vines
summary: >
  Carnivorous flowering vines that grapple and dissolve prey, immune to charm,
  vulnerable to fire.
ac: 12
hp: 60
actions:
  - Vine Whip: +5 to hit, reach 10 ft, 2d6 piercing + 1d6 acid, grapple DC 14

## bb:creatures:ravething
type: monster
id: bb:beast:ravething
summary: >
  Hairless jungle scavenger with spines, hunts in packs, preys on restrained victims.
ac: 13
hp: 18
traits:
  - Pack Hunter: advantage vs grappled/ restrained targets
  - Opportunist: bonus 10 ft move when ally attacks nearby
actions:
  - Claw: +4 to hit, 1d6+3 slashing
  - Spine Flurry (Recharge 5–6): DC 13 DEX save, 2d6 piercing

# Item
## bb:items:Final-Verse
type: item
id: bb:item:final-verse
rarity: uncommon
slot: weapon
weapon_type: shortsword
properties: [finesse, light]
damage: 1d6 piercing
effects:
  - On kill: wielder hears fragment of target’s last memory
  - Once per long rest: wound self for 1d6 dmg to reroll failed CHA/WIS save vs charm/possession
