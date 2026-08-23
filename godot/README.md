# The Shattered Realms — Godot Client

This is the first UI vertical slice. Python remains the authoritative game backend; Godot renders the campaign and sends player actions.

## 1. Start the backend API

From the repository root:

```bash
python -m backend.api
```

Leave that terminal running. The API listens on `127.0.0.1:8765` by default and uses the same saved campaign as the terminal prototype.

## 2. Open the Godot project

In Godot 4:

1. Import/open the `godot` folder.
2. Open `project.godot` if Godot asks for a project file.
3. Press **F6/F5** or the Play button.

The client should load your current saved character, status, money, location, inventory, party, and campaign state. Type actions into the Game Master box or press one of the three suggested action buttons.

## Phase 1 scope

Working now:
- Saved campaign loading
- Player HUD (HP, Shield, Armor, Resource, Level/XP, SP/AP, money, location, weapon)
- DM narration
- Free-text player actions
- Three suggested-action buttons
- Roll-preview labels
- Inventory quick view
- Party quick view
- Player stats and campaign summary quick views
- Active combat state remains controlled by Python
- Direct `end turn` support through the API

Coming next:
- Full world + character creation screens
- Proper inventory/equipment panel with buttons
- Shop + haggling UI
- Dedicated combat screen/HUD and target selection
- Map system
- Party management
- Generated-image/video gallery
- Final art, animation, transitions, sound, and polish
