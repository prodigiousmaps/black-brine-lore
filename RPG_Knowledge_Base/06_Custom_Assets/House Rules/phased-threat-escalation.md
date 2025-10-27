---
type: house-rules
id: bb:page:phased-threat-escalation
collection: The Deep Green
title: "PHASED THREAT ESCALATION – The Road to the Hollow Song"
description: >
  A phased threat-progression framework for The Deep Green campaign arc.
  Each phase represents an escalation of danger, corruption, and environmental influence
  as the party approaches Vexir and the Hollow Song Temple.
icon: null
tags: [GameMechanics, LandFeatures, Encounter, ForgottenWind]
coverImage: null

phases:
  - phase: 1
    name: "Wild Jungle (Outer Hexes)"
    mood: "Tense, oppressive, but natural."
    threats: ["Predators", "Curses", "Old ruins", "Weather"]
    encounters:
      - "Beast ambushes (serpent swarms, corpse lizards)"
      - "Jungle diseases"
      - "Forgotten shrines to Sedna and false gods"
      - "Warnings carved in druidic or abyssal script"
    effect: >
      Threats feel indifferent but deadly—nature is not yet aware of the intruders.

  - phase: 2
    name: "The Encroached Zone (Mid-Jungle)"
    mood: "Wrongness seeps into the air—rot without flies, trees without birds, stone with veins."
    trigger: "Once within three hexes of Vexir."
    effects:
      - "Normal jungle encounters shift to include cult influence and residual magic."
      - "All Perception and Insight checks are made with disadvantage unless a light source is carried."
      - "Pinch’s map tools start to draw symbols on their own during long rests."
    encounters:
      - "Disfigured animals with extra eyes or fused limbs."
      - "Unborn scouts hiding in trees (silent observers)."
      - "Cult totems made from knotted hair and bone."
      - "Whispering plants—investigating causes psychic damage."
      - "A ruined camp of explorers who worshiped the Pretender after succumbing to madness."
      - "Possessed beasts that act with synchronized, intelligent aggression."
    effect: >
      The party begins to feel watched. Rest becomes less effective.
      Divine casters may experience ominous dreams or blocked guidance.

  - phase: 3
    name: "The Hollow Grove (Temple Perimeter)"
    mood: "Sacrilege made manifest—the jungle is not dead, it’s listening."
    trigger: "Last one to two hexes surrounding Vexir."
    terrain_changes:
      - "Twisted trees grow in impossible shapes, leaning toward the mountain."
      - "Air is thick with droning, like a song beneath the threshold of hearing."
      - "Sound is muffled—speech echoes wrong, music distorts."
      - "The sun never fully penetrates the canopy, even at noon."
    mechanics:
      - "Stealth is nearly impossible due to muttering roots and noise-warping flora."
      - "Spellcasting within this zone risks wild effects (DM may roll or apply narrative glitches)."
      - "Unnatural darkness spreads from the Temple at dusk—no mundane light can pierce it."
    encounters:
      - category: "Cult of the Hollow Song"
        details:
          - "Malformed warlocks wielding silence magic."
          - "Vermin-Lord acolytes performing rituals with flesh-made instruments."
          - "Sacrificed Unborn bound to trees, still aware, whispering."
      - "Hollow Echo Beasts that steal voices."
      - "Shrines that hum if touched—channel Atropus’ will."
      - "A welcoming party of cultists who offer to guide the PCs to the Temple—but not back."
    effect: >
      The jungle itself becomes a weapon.
      The party is in a place forgotten by gods but remembered by something else.

optional_mechanics:
  - "Rite of Silence: Players may attempt a holy rite or magical silence to mask their presence—limited uses."
  - "Sacrificial Shortcut: A mad cultist may offer a faster path in exchange for something dear."
  - "Mutated Jungle Pathways: Trails open or close depending on party behavior—
     if they burn something holy, the jungle lets them pass; if they speak the name of Sedna, the vines tighten."
---
