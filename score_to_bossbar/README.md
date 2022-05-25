# Score to bossbar
This program will create a mcfunction file that will update the bossbar using the scoreboard.

## Links
- [download](https://legopitstop.weebly.com/score_to_bossbar.html)

## Features
- Choose scoreboard name and objective to use.
- Choose the bossbar id to use.
- Includes an option to add a fixer that will fix the value if it's out of range.

## Planned Features
- Advanced options for more customizability
- Add timer calculator. converts any time to percentage. This way the bossbar max can stay at 100 but suports any time.

<!-- Calculate the time (N * 100 / max = bossbar) -->
scoreboard players set #100 timer 100
scoreboard players operation #bossbar timer = #time timer
scoreboard players operation #bossbar timer *= #100 timer
scoreboard players operation #bossbar timer /= #max timer