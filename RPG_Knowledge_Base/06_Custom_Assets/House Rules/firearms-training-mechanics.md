---
type: house-rules
id: bb:house-rules:firearms-training-mechanics
collection: Black Brine
collection: The Deep Green
parent_location: bb:hub:house-rules
title: "Firearms Training Mechanics"
description: >
  Fenrith’s brutal firearms training mini-game, “The Black Powder Crucible,”
  turns reckless shooters into disciplined gunners through a three-phase series
  of skill challenges that test speed, precision, and composure under fire.
icon: null
tags: [GameMechanics, Encounter, Firearms, Training, MiniGame]
coverImage: null

overview: >
  Fenrith doesn’t train amateurs—he breaks them down and rebuilds them into disciplined gunners.
  His regimen focuses on speed, precision, and unflinching nerve under live-fire conditions.
  The training sequence consists of three escalating phases, followed by a final integrated test.

phases:
  - phase: 1
    name: "Loading Under Fire (Speed & Stress)"
    goal: >
      Successfully load and fire a musket or flintlock pistol before an advancing enemy reaches you.
    mechanics:
      - "Firearms have a loading time requiring a Dexterity (Sleight of Hand) check."
      - "The enemy advances each round while the shooter attempts to reload before melee range."
    loading_difficulty_table:
      - weapon: Musket
        loading_dc: 14
        rounds: 2
        modifiers:
          - "-1 DC if using pre-measured powder."
      - weapon: Pistol
        loading_dc: 12
        rounds: 1
        modifiers:
          - "+2 DC if under duress (enemy within 10 feet)."
    process:
      - "Each round, roll Dexterity (Sleight of Hand) to reload."
      - "Failure: The enemy closes distance; retry next round."
      - "Success: Weapon is loaded; shooter can fire next turn."
    failure_consequences:
      - "If enemy reaches melee before firing, shooter must either:"
      - "• Strength Check (DC 15) to push them back."
      - "• Draw a melee weapon (losing next turn)."
      - "• Attempt risky point-blank shot (disadvantage)."
    trainee_perks:
      - "+2 on loading rolls under pressure."
      - "Advantage when using pre-measured powder charges."

  - phase: 2
    name: "The Iron Eye (Marksmanship & Control)"
    goal: >
      Hit three moving targets at different distances before time runs out.
    mechanics:
      - "Shooters make attack rolls against three targets at varying distances."
      - "Each target has an AC based on distance and movement."
      - "Shooter may choose between careful aiming (bonus to hit) or quick firing (reload speed)."
    marksmanship_table:
      - target_type: Stationary (Dummy)
        distance: 30 ft
        ac_musket: 10
        ac_pistol: 12
        modifiers:
          - "+2 if aiming carefully (skip next round)."
      - target_type: Walking (Slow Moving)
        distance: 50 ft
        ac_musket: 12
        ac_pistol: 15
        modifiers:
          - "-2 if firing quickly."
      - target_type: Running (Dashing Target)
        distance: 70 ft
        ac_musket: 15
        ac_pistol: 18
        modifiers:
          - "-5 unless spending a full round aiming."
    process:
      - "Shooter picks a target and fires."
      - "Roll attack using Dexterity + Proficiency with firearms."
      - "On hit: advance to next target."
      - "On miss: choose to re-aim (lose a round, +3 bonus) or fire immediately (no bonus)."
    trainee_perks:
      - "+1 to ranged attacks with firearms."
      - "Advantage on one firearm attack per long rest."

  - phase: 3
    name: "Firearms Are Liars (Misfires & Malfunctions)"
    goal: >
      Learn to manage gun malfunctions without panicking.
    mechanics:
      - "Each shot has a chance to misfire, especially in poor conditions or under stress."
      - "On misfire, the shooter must fix the weapon before firing again."
    misfire_table:
      - weapon: Musket
        misfire_on: [1, 2]
        fix: "Action: DC 15 Tinker’s Tools or Strength check."
      - weapon: Pistol
        misfire_on: [1]
        fix: "Bonus Action: DC 12 Tinker’s Tools or Strength check."
    process:
      - "On a natural 1 (or 2 for muskets), the weapon misfires."
      - "Roll Dexterity (Tinker’s Tools) or Strength to clear jam."
      - "Failure: weapon remains jammed until next turn."
      - "Critical failure: firearm disabled for remainder of fight."
    weather_modifiers:
      - "Heavy Rain: misfires on 1–3 instead of 1–2."
      - "Humid Jungle Conditions: misfires on 1–4 unless powder properly stored."
    trainee_perks:
      - "+1 to checks for clearing misfires."
      - "Once per day, may automatically clear a misfire as a free action."

final_test:
  name: "The Gauntlet (Combined Trial)"
  goal: >
    Fire three shots at moving targets while under fire, avoiding misfires and completing the drill
    before the enemy reaches the trainee.
  sequence:
    - "Roll to load → success allows firing; failure lets enemy advance."
    - "Roll to hit → choose careful or fast shooting."
    - "Roll for misfire → fix or adapt."
  scoring:
    perfect: "3/3 hits, no misfires, never reached by enemy."
    good: "2/3 hits, minimal issues."
    mediocre: "1/3 hit or forced into melee."
    failure: "No hits, jammed gun, or tackled before firing."
  trainee_perks:
    - "Fenrith’s Drills: once per long rest, reload instantly (no roll required)."
    - "Nerves of Steel: on misfire, may still take another action."

flavor_text: >
  “Firearms ain't for the weak-hearted. The musket don’t care if you’re scared.
  The pistol don’t care if you’re slow. You get one shot—make it count. Or someone else will.”
  — Fenrith
---
