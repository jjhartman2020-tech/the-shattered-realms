# Equipment.md

Version: 1.1
Status: In Development

---

# Table of Contents

1. Equipment Philosophy
2. Equipment Types
3. Equipment Slots
4. Weapons
5. Armor
6. Shields
7. Accessories
8. Equipment Rarity
9. Attribute Requirements
10. Equipment Stats
11. Legendary Equipment
12. Set Bonuses
13. Durability
14. AI Generated Equipment
15. Balance Philosophy
16. Future Systems
17. Exact Mechanical Display Rules
18. Weapon Power and Resource-Cost Progression

---

# 1. Equipment Philosophy

## Design Goals

- Equipment should feel rewarding to obtain.
- Every piece of equipment should have a purpose.
- Equipment should support multiple playstyles.
- Better equipment should open new possibilities and may also become meaningfully stronger.
- Equipment progression should reward exploration and difficult encounters.
- The player must always be able to see the real mechanical values of an item before choosing, equipping, purchasing, or looting it.

---

# 2. Equipment Types

Equipment is divided into Weapons, Armor, Shields, and Accessories.

---

# 3. Equipment Slots

Default equipment slots include Main Hand, Off Hand, Helmet, Chest Armor, Gloves, Legs, Boots, Ring 1, Ring 2, Necklace, and Charm.

Future equipment slots may be added through special progression systems.

---

# 4. Weapons

Weapons determine or display:

- Base Damage
- Damage Type when relevant
- Range
- Attack Attribute
- Resource Cost per attack when applicable
- Special Effects
- Ability Synergies

Weapon examples include swords, greatswords, daggers, spears, axes, hammers, bows, crossbows, staves, wands, scythes, whips, and dual weapons.

**Every weapon with a damaging attack must show its exact damage expression.** A sword may display `Damage 1d6`, a stronger sword may display `Damage 2d6`, and a magical weapon may additionally show its exact special effect.

Weapons may consume the user's class resource when attacked with. Resource Cost is defined per weapon. A simple starter weapon may cost 0 or a small amount, while stronger weapons may require larger amounts of the character's established class resource.

If the character does not have enough current resource to pay a weapon's attack cost, that weapon may remain equipped but its resource-consuming attack cannot be used until the full cost can be paid.

---

# 5. Armor

Armor provides exact visible Defense, damage reduction, resistance, or other effects. Armor categories include Cloth, Leather, Medium Armor, and Heavy Armor.

---

# 6. Shields

Shields may provide Block Chance, damage reduction, knockback resistance, Armor/Defense bonuses, or special defensive effects. Any numeric effect must be displayed exactly.

---

# 7. Accessories

Accessories may provide passive bonuses such as increased critical chance, Resource regeneration, health regeneration, movement, elemental resistance, or other explicit effects.

---

# 8. Equipment Rarity

Equipment rarities include Common, Uncommon, Rare, Epic, Legendary, and Mythic.

Higher rarity equipment generally has stronger effects, additional bonuses, and unique abilities, but rarity alone does not replace actual displayed stats.

---

# 9. Attribute Requirements

Equipment may require minimum attributes. Attribute requirements use the current 0-100 attribute system defined in `Stats.md`.

If attribute requirements are not met, the item cannot be equipped unless a specific rule explicitly overrides the requirement.

---

# 10. Equipment Stats

Equipment may provide Strength, Dexterity, Agility, Constitution, Intelligence, Wisdom, Charisma, Speed, Defense, Luck, Magic, Health, Resource, Critical Chance, damage bonuses, Armor, resistances, or unique passive effects.

Any stat or effect provided by equipment must be explicit and visible.

---

# 11. Legendary Equipment

Legendary equipment is among the rarest equipment in the game and may have unique appearance, lore, powerful passive effects, special abilities, or build-defining mechanics.

---

# 12. Set Bonuses

Some equipment belongs to a set. Equipping multiple pieces from the same set grants additional bonuses. Every threshold and effect must state exact values.

---

# 13. Durability

Equipment durability is currently under consideration and remains undecided.

---

# 14. AI Generated Equipment

The AI may generate completely unique equipment, but generated equipment must follow the same mechanical rules as handcrafted equipment.

For every generated weapon the AI must determine:

- Name
- Type
- Description
- Rarity
- Damage
- Range
- Attack Attribute
- Resource Cost per attack when applicable
- Special Effects
- Attribute Requirements when applicable
- Value when relevant

Generated non-weapon equipment must similarly state exact bonuses or effects rather than vague descriptions.

---

# 15. Balance Philosophy

- No equipment should be mandatory.
- Every weapon type should remain viable.
- Every armor type should support different playstyles.
- Equipment should reward experimentation.
- Early-game equipment should be deliberately weaker than later equipment.
- Stronger weapons should normally demand greater investment through rarity, requirements, Resource Cost, risk, or other meaningful limitations.

---

# 16. Future Systems

Possible future additions include Equipment Transmogrification, Cosmetic Skins, Weapon Mastery, Equipment Upgrading, Equipment Crafting, Socketed Gems, and a Rune System.

---

# 17. Exact Mechanical Display Rules

Whenever the player views a weapon or other equipment option, the UI must display what it actually does.

Examples:

`Worn Iron Sword — Damage 1d6 | Range 1 | Cost 0 Trailmarks`

`Riftsteel Saber — Damage 2d8 | Range 1 | Cost 20 Trailmarks | On hit: move 1 square without provoking`

`Phase Bow — Damage 2d6 | Range 7 | Cost 15 Focus`

`Traveler Boots — Movement +1 square`

`Reinforced Buckler — Armor +1`

Flavor text may be shown, but never instead of these mechanical values.

---

# 18. Weapon Power and Resource-Cost Progression

Characters should begin with weak starter weapons. These weapons normally use small damage dice, short range, few or no special effects, and low Resource Costs.

As the player explores, levels, defeats stronger enemies, crafts items, completes quests, and finds rarer loot, stronger weapons become available. Stronger weapons may have:

- Larger damage expressions
- Greater range
- Stronger secondary effects
- Multiple effects
- Better target coverage
- Stronger scaling

Those improvements should generally be paired with higher Resource Costs, tougher requirements, higher rarity, or another meaningful limitation.

A weapon may be acquired and equipped even when its Resource Cost is currently impossible for the character to pay, provided its normal attribute/equipment requirements are met. The player simply cannot use its resource-consuming attack until enough current resource is available.

This creates long-term progression where discovering an extremely powerful weapon can become a future build goal rather than forcing the game to hide the item until the character is already strong enough to use it.
