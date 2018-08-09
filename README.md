# bingobot
Discord.py bot for Bingo

## Introduction
bingobot was a sad attempt to generate Bingo cards for the upcoming E3 2018 which was not adopted by guild members. He now exists here for your own enjoyment.

## Prerequisites
bingobot requires the Python 3.5+, discord.py rewrite and a token for your own Discord bot.

[How to create a Discord Bot user](https://twentysix26.github.io/Red-Docs/red_guide_bot_accounts/)

## Installation

`git clone https://github.com/wonderbrian/bingobot.py.git`  
`cd bingobot`

You can find out more about installing the [discord.py rewrite here](https://github.com/Rapptz/discord.py)

## Configuration
There are configuration variables accessible in config.py
* token - Your bot token
* prefix - Prefix for your bot commands
* enrollable - Whether or not users can roll Bingo cards and if an admin can confirm predictions
* max_rolls - Maximum number of times user can roll a Bingo card
* user_selects_card - Whether a user can choose between current card and newly rolled card. Disable if users are stuck with rerolls
* admins - Array containing Discord user IDs for admins who are able to confirm predictions.

You can find someone's user ID by entering `\@username-mention` into chat.

## Bot Commands

* `roll` - Roll Bingo card up to `maxRolls` times.
* `mypredictions` - List the predictions on your card. Confirmed predictions are indicated.
* `mycard` - Display in traditional Bingo format
* `confirm` - Confirm predictions on existing Bingo cards.

## Dependencies
bingobot requires `./config.py` and `./predictions.txt` to play.

## Authors
**Yuping** -*Initial Work* - [that's me](https://github.com/wonderbrian)
