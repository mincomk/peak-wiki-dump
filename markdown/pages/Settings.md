---
title: "Settings"
source: https://peak.wiki.gg/wiki/Settings
pageid: 1344
revid: 11891
namespace: 0
---

# Settings

The **Settings** menu allows the player to fine-tune their gameplay experience. Multiple tabs are found along the top of the menu that allow the player to navigate the various groups of settings.

On Windows, the settings are stored in the registry under `HKEY_CURRENT_USER/SOFTWARE/LandCrab/PEAK`.

## List of settings

### General

| Setting | Default | Options & Notes |
| --- | --- | --- |
| Language | System language | - English - Français - Italiano - Deutsch - Español (España) - Español (LatAm) - Português (BR) - Русский - Українська - 简体中文 - 繁體中文 - 日本語 - 한국어 - Polski - Türkçe |
| Field Of View | 70.00 | 60.00 – 100.00 |
| Climbing Extra Field Of View | 40.00 | 0.00 – 50.00 |
| Lobby Mode | Invite Only | - Open To Friends - Invite Only |
| Hide Room Code | On | - Off - On |

### Controls

| Setting | Default | Options & Notes |
| --- | --- | --- |
| Mouse Sensitivity | 2.00 | 0.10 – 5.00 |
| Controller Sensitivity | 2.00 | 0.10 – 5.00 |
| Input Icons | Auto | - Auto - Gamepad Style 1 - Gamepad Style 2 - Keyboard & Mouse |
| Invert X | Off | - Off - On |
| Invert Y | Off | - Off - On |
| Jump To Grab Wall | On | - Off - On |

### Accessibility

These settings can only be adjusted on the main menu, and not during a game session.

| Setting | Default | Options & Notes |
| --- | --- | --- |
| Reduce Camera Bobbing | Off | - Off - On |
| Enable [Cannibalism](Cannibalism.md) | On | - Off - On |
| [Bug Phobia Mode](Bug%20Phobia%20Mode.md) | Off | - Off - On |
| [Zombie Phobia Mode](Zombie%20Phobia%20Mode.md) | Off | - Off - On |
| [Photosensitivity Mode](Photosensitivity%20Mode.md) | Off | - Off - On |
| [Color Blindness Mode](Color%20Blindness%20Mode.md) | Off | - Off - On |
| Enable The [Looker](Looker.md) | On | - Off - On |

### Graphics

| Setting | Default | Options & Notes |
| --- | --- | --- |
| Window Mode | Windowed Fullscreen | - Windowed - Fullscreen - Windowed Fullscreen |
| Resolution | System's resolution | - Set the desired screen resolution for gameplay based on a list of resolutions supported by the player's hardware. |
| Max Framerate | 400.00 | 30.00 – 600.00 |
| Vsync | Off | - Off - On |
| Render Scale | - High - (Medium on Steam Deck) | - Native - High - Medium - Low |
| Shadow Distance | - Medium - (Low on Steam Deck) | - High - Medium - Low - Off |
| Texture Quality | - Native - (High on Steam Deck) | - Native - High - Medium - Low |
| World Quality | - Medium - (Low on Steam Deck) | - Low - Medium - High |
| Ambient Occlusion | - On - (Off on Steam Deck) | - Off - On |

### Audio

| Setting | Default | Options & Notes |
| --- | --- | --- |
| Microphone | User choice | - Set the desired connected microphone for in-game communication. - Upon first launch, the game will present a list of available microphones. |
| Microphone Mode | Voice Activation | - Voice Activation - Push To talk - Push To Mute |
| Master Volume | 1.00 | 0.00 – 1.00 |
| SFX Volume | 1.00 | 0.00 – 1.00 |
| Music Volume | 1.00 | 0.00 – 1.00 |
| Voices Volume | 1.00 | 0.00 – 1.00 |

## Patch history

![Peak Badge.png](../../images/Peak_Badge.png) **[1.0](1.0.md) (2025-06-16):** Introduced.
![Peak Badge.png](../../images/Peak_Badge.png) **[1.1.a](1.1.a.md) (2025-06-17):** Added a framerate cap to the settings menu. This should be your second step to try!
![Peak Badge.png](../../images/Peak_Badge.png) **[1.2.a](1.2.a.md) (2025-06-18):**

- Added Invert X and Y settings to the options menu.
- Fixed issue where push-to-talk could break when travelling to the island from the airport.

![Peak Badge.png](../../images/Peak_Badge.png) **[1.4.a](1.4.a.md) (2025-06-22):**

- The game will now default to a new fullscreen mode: "Fullscreen Windowed". This will hopefully fix issues where people aren’t seeing the cursor in Fullscreen Exclusive mode as well as issues when alt-tabbing.
- There is now a settings option called "Lobby Mode" The default is the same as it is now but you can change it to "Invite Only" which will prevent others from being able to join the game without an invite.

![Peak Badge.png](../../images/Peak_Badge.png) **[1.6.a](1.6.a.md) (2025-07-04):**

- Fixed an issue where the Max Framerate setting wouldn't work.
- Fixed an issue where Invert X is displayed as Invert Y in the Settings
- Fixed bug where switching scenes didn't apply voice volume slider settings correctly
- Fixed Push To Talk disables itself on every loading screen

![Peak Badge.png](../../images/Peak_Badge.png) **[1.7](1.7.md) (2025-07-10):**

- Translations are in! The game is now available in the following languages:- English, French, Italian, German, Spanish (Spain), Spanish (LATAM), Brazilian Portuguese, Russian, Ukrainian, Chinese (Simplified), Japanese, Korean

![Peak Badge.png](../../images/Peak_Badge.png) **[1.8](1.8.md) (2025-07-21):**

- REDUCE CAMERA BOBBING OPTION - You can now go into the settings (ON THE MAIN MENU) to enable this option to reduce camera bobbing...- Please note that since this game is entirely physics-based we had to do a workaround solution that’s not entirely perfect. Hopefully this is enough to make the game more playable for those with motion sickness so please try it out and give us your feedback!
  - [!!] NOTE: This had bugs when toggled during gameplay in beta so for now it is only accessible via the main menu.

![Peak Badge.png](../../images/Peak_Badge.png) **[1.9.a](1.9.a.md) (2025-07-22):** Undid a change to Fullscreen Windowed mode.
![Peak Badge.png](../../images/Peak_Badge.png) **[1.10.a](1.10.a.md) (2025-07-30):**

- Polish and Turkish translations are in!
- New Setting: "Climbing Extra Field Of View". This lets you adjust how the FOV changes while climbing.
- New Setting: PUSH TO MUTE. This works the opposite way of "Push To Talk." No more having to listen to your streamer friend talk to chat.
- Settings that were previously hidden outside of the Main Menu will now show up but be disabled. Hopefully this reduces some confusion!

![Peak Badge.png](../../images/Peak_Badge.png) **[1.11.a](1.11.a.md) (2025-08-01):** Added an option called "ENABLE CANNIBALISM" which is on by default. For folks who don’t want to engage with this mechanic simply turn it off at the Main Menu. By turning it off you will no longer see other players become chickens or be able to eat them and other players will not be allowed to see you as a chicken or eat you.
![Peak Badge.png](../../images/Peak_Badge.png) **[1.20.a](1.20.a.md) (2025-08-11):**

- There is now a "Bug Phobia Mode" option for players who don’t want to see arachnids and other creepy crawlies because you guessed it the Mesa has some of those.
- The Settings menu is now navigable via controller. Finally!

![Peak Badge.png](../../images/Peak_Badge.png) **[1.27.a](1.27.a.md) (2025-08-27):**

- NEW GRAPHICS SETTING: Texture Quality- This is actually huge. You can now lower the texture quality across the game, which is important for players with low VRAM. This can resolve issues with low framerate, missing graphics, and even crashes. Also it doesn’t even look much worse. Check it out!
- NEW ACCESSIBILITY SETTING: Photosensitive Mode.- This mode changes the following:- [Dynamite](Dynamite.md), [Flare](Flare.md), and [Scout Cannon](Scout%20Cannon.md) lit fuse effects are less flashy
    - Screenshake is lessened.
    - Bright lights from the dynamite explosion are disabled.
    - Fullscreen VFX from taking various sources of damage are less intense and more gradual.
    - Fullscreen VFX from the [Energy Drink](Energy%20Drink.md), [Lollipop](Big%20Lollipop.md), and [Heat Pack](Heat%20Pack.md) are less intense.

![Peak Badge.png](../../images/Peak_Badge.png) **[1.28.a](1.28.a.md) (2025-09-08):**

- FEATURES- Color Blindness Mode! This adds patterns to differently-colored [berries](https://peak.wiki.gg/wiki/Berry) to further differentiate them.
- MINOR FIXES- Removed [Scoutmaster](https://peak.wiki.gg/wiki/Scoutmaster) grain effect in Photosensitive Mode.
  - Rainbow [stamina bar](Stamina%20bar.md) is now slower in Photosensitive Mode.

![Peak Badge.png](../../images/Peak_Badge.png) **[1.31.a](1.31.a.md) (2025-09-25):** Added a "Jump to Grab Wall" option in General Settings that is on by default.
![Peak Badge.png](../../images/Peak_Badge.png) **[2.0.a](2.0.a.md) (2026-08-11):** The game is now localized in Traditional Chinese!
![Peak Badge.png](../../images/Peak_Badge.png) **[2.4.a](2.4.a.md) (2026-09-02):** In the Settings menu, there is an option to hide the room code
