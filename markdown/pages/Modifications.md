---
title: "Modifications"
source: https://peak.wiki.gg/wiki/Modifications
pageid: 1494
revid: 7807
namespace: 0
---

# Modifications

![](https://commons.wiki.gg/images/Stub.svg?ddd5ba)

This page is a [stub](https://support.wiki.gg/wiki/Stub). You can help **PEAK Wiki** by expanding it.

![](../../images/Guidebook_Badges.png)

Disclaimer

*[PEAK](Peak%20%28game%29.md)* modifications are made by the community and are not tested by the [developers](https://peak.wiki.gg/wiki/Developers). Install and use them at your own risk.

**Modifications** in *[PEAK](Peak%20%28game%29.md)* allow the players to customize their experience. [Thunderstore.io](https://thunderstore.io/c/peak/) is currently a very popular mod repository among the *PEAK* community.

To enable mods, the most common method is to install a third-party framework called BepInEx, which is a popular modding framework for Unity-based games. This allows players to easily install and manage mods. Most mods are client-side, meaning they only affect the player's local game experience.

## How to Install Mods

### Manual Installation

- **Download BepInEx** Visit the official BepInEx website or the *PEAK* modding community page to download the version compatible with your game.
- **Install BepInEx** Extract the contents of the BepInEx zip file into your PEAK game directory (where the game executable is located).
- **Add Mods** Download mods from trusted sources like NexusMods or Thunderstore. Place the `.dll` files into the `BepInEx/plugins` folder in the game’s files.
- **Launch the Game** Start PEAK normally. BepInEx will load automatically, and any installed mods will be applied.

**Important Notice:**

If your game crashes, open the `BepInEx/config` folder and enable the console log to identify which mod may be causing issues.

### Mod Managers

Mod Managers allow for easier management of mods by allowing users to have separate profiles containing different mods. Mods can easily be enabled or disabled in one profile without affecting other profiles. Mod managers also handle installing dependencies for a mod. They allow sharing profiles with other users. Mod managers can also inform users when installed mods have newer versions available.

Mod managers should only be installed from their official sources. There are currently 3 established mod managers that source mods from <https://thunderstore.io/>:

- [Thunderstore Mod Manager](https://www.overwolf.com/app/thunderstore-thunderstore_mod_manager) - Ad-supported mod manager by Thunderstore built using the Overwolf client.
- [r2modman](https://thunderstore.io/c/peak/p/ebkr/r2modman/) - Ad-free open source mod manager with a similar interface to Thunderstore Mod Manager.
- [Gale](https://thunderstore.io/c/peak/p/Kesomannen/GaleModManager/) - Ad-free open source manager focused on looking modern and being lightweight.

For installation instructions, see the relevant mod manager's website.

## What to Remember

- **Use mods at your own risk!** *PEAK* does not officially support modding, and the developers will not provide support for issues caused by mods.
- Mods can break the game. Some mods may cause crashes, bugs, or performance problems.- *PEAK* updates may also break mod compatibility. If bugs begin to occur after a game update, check for a newer version of the mod.
- Always **backup your game files** before installing mods.
- Only download mods from **trusted sources** to avoid malicious files.
- Mods can significantly change the intended experience of *PEAK*, which may ruin the pacing, challenge, or original design of the game.
- Mods can also ruin the experience for other players.

## Community and Support

The *PEAK* modding community is active and helpful, making it easier to find mods, share ideas, and troubleshoot issues. Here are some great places to find support:

- **Discord servers** dedicated to PEAK modding — where modders and players discuss new mods, updates, and problems.
- **Reddit communities** for PEAK or Unity game modding in general.
- **Official forums or Steam discussions** — these often have modding guides and user support.

When installing mods, it’s a good idea to check community feedback and reviews to ensure the mods are stable and safe.

## Troubleshooting Tips

- If the game crashes after installing mods, try removing all mods and adding them back one by one to identify the problematic mod.
- Make sure BepInEx is updated to the latest compatible version with PEAK.
- Always read mod descriptions carefully — some mods may require additional dependencies or specific install steps.
- Backup your game files regularly, especially before installing new mods.
- If you encounter bugs, check the BepInEx console log for errors to help pinpoint issues. Bepinex console can be activated inside the bepinex.cfg inside the config files.
