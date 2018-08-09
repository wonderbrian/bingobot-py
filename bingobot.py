import datetime
import discord
from discord.ext import commands
import json
import os
import random
import sys

import config

# Define variables
prefix = config.prefix
admins = config.admins
max_rolls = config.max_rolls
enrollable = config.enrollable
user_selects_card = config.user_selects_card
timestamp = str(datetime.datetime.now()).split('.')[0]
bot = commands.Bot(command_prefix=prefix)

# Read predictions from file
predictions = [line.rstrip('\n') for line in open('predictions.txt')]

# Exit if not enough predictions
if len(predictions) < 25:
    sys.exit("Not enough predictions to generate a card. You need at least 24.")

# Define variables per each message
def retrieve_user_info(msg):
    user = msg.author
    bingo_card = f"./cards/{msg.author.name}.json"
    # Generate placeholder card if user does not have an existing card.
    if os.path.exists(bingo_card) == False:
        data = open(bingo_card, "w+")
        data.write('{"id": 0, "rolls": 0, "card": {}}')
        data.close()

    with open(bingo_card, "r") as data:
        card_content = json.load(data)
    data.close()

    return {"user": user, "bingo_card": bingo_card, "card_content": card_content}

# Roll bingo card
def roll_card():
    # Generating unique random indices. We'll use this for predictions.
    unique_randoms = random.sample(range(1, len(predictions)), 24)
    card = {}
    for x in range(1, 26):
        cell_name = f"cell-{x}"
        card[cell_name] = {}
        if x == 13:
            card[cell_name]["value"] = "Free Space"
            card[cell_name]["confirmed"] = True
        else:
            if x < 13:
                index = x - 1
            else:
                index = x - 2
            card[cell_name]["value"] = predictions[unique_randoms[index]]
            card[cell_name]["confirmed"] = False
    return card

# Save bingo card
def save_card(bingo_card, id, rolls, card_to_save):
    rolls += 1
    card = {
        "id": id,
        "rolls": rolls,
        "card": card_to_save
    }
    with open(bingo_card, "w") as data:
        json.dump(card, data)
    data.close()

# Show predictions
def show_predictions(card):
    string = ""
    for key in card:
        if card[key]["confirmed"]:
            string += "~~" + card[key]["value"] + "~~ :white_check_mark:\n"
        else:
            string += card[key]["value"] + "\n"
    return string

@bot.event
async def on_ready():
    print('-----------------')
    print(timestamp)
    print("Let's Play Bingo!")

@bot.command()
async def roll(ctx):
    # Check if enrollments are open
    if enrollable == False:
        await ctx.send("Enrollments are now closed. See you next time!")
        return
        
    # Retrieve user info
    user_info = retrieve_user_info(ctx.message)

    # Check if user qualifies for a (re-)roll
    if user_info["card_content"]["rolls"] >= max_rolls:
        await ctx.send("Out of re-rolls! Sorry, dood.")
        return

    # Save old card and generate new card
    await ctx.send("_Beep boop generating card..._")
    old_card = user_info["card_content"]
    new_card = roll_card()

    msg = "Done! Here are your predictions:\n"
    msg += show_predictions(new_card)
    await ctx.send(msg)

    # Prompt user to save card, if enabled and not initial roll.
    if (user_selects_card and user_info["card_content"]["rolls"] > 0):
        await ctx.send("Save Card? Yes or No")
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        response = await bot.wait_for('message', check=pred)
        # Validate response
        while (response.content.lower() != "yes" and response.content.lower() != "no"):
            await ctx.send("I don't understand. Save Card? Yes or No")
            response = await bot.wait_for('message', check=pred)
        if response.content.lower() == "yes":
            await ctx.send("OK, saving your new card.")
            save_card(user_info["bingo_card"], ctx.message.author.id, user_info["card_content"]["rolls"], new_card)
        elif response.content.lower() == "no":
            await ctx.send("Sure, you can keep your old card.")
            save_card(user_info["bingo_card"], ctx.message.author.id, user_info["card_content"]["rolls"], old_card)
    else:
        save_card(user_info["bingo_card"], ctx.message.author.id, user_info["card_content"]["rolls"], new_card)

    await ctx.send('Happy Bingo-ing!')

@bot.command()
async def mypredictions(ctx):
    # Retrieve user info
    user_info = retrieve_user_info(ctx.message)
    # Check if user has rolled a card.
    if user_info["card_content"]["rolls"] == 0:
        await ctx.send("You don't have a bingo card! `" + prefix + "roll` to create one.")
        return

    await ctx.send(show_predictions(user_info["card_content"]["card"]))

@bot.command()
async def mycard(ctx):
    # Retrieve user info
    user_info = retrieve_user_info(ctx.message)
    cell_count = 1
    card_display = "```|"

    for x in range(1, 26):
        cell_name = f"cell-{x}"
        if user_info["card_content"]["card"][cell_name]["confirmed"]:
            card_display += " ◯ |"
        else:
            card_display += " ✖ |"
        cell_count += 1
        if (cell_count == 6 and x != 25):
            card_display += "\n|"
            cell_count = 1
    card_display += "```"
    await ctx.send(card_display)

@bot.command()
async def confirm(ctx, *args):
    if ctx.message.author.id not in admins:
        await ctx.send("YOU ARE NOT AUTHORIZED TO USE THIS TOOL")
        return
    # Stop if enrollments are open.
    if enrollable:
        await ctx.author.send("Enrollments are still open. Update `config.py` to start confirming predictions.")
        return
    # Stop if no confirmation message.
    if len(args) == 0:
        await ctx.send("You didn't submit anything to confirm.")
        return

    # Sanitize confirmed prediction
    confirmed_prediction = ctx.message.content.replace(prefix + "confirm ", '')

    confirmation_message = ""
    # Iterate through all cards in directory, confirming any matching predictions
    file_paths = []
    for root, dirs, files in os.walk("cards"):
        for file in files:
            if file != ".placeholder":
                file_paths.append("./cards/" + file)
    for file_path in file_paths:
        with open(file_path, "r") as data:
            card_content = json.load(data)
            confirmed_card = {}
            for x in range(1, 26):
                cell_name = f"cell-{x}"
                confirmed_card[cell_name] = {}
                prediction = card_content["card"][cell_name]["value"]
                confirmed_card[cell_name]["value"] = prediction
                if prediction.lower() == confirmed_prediction.lower():
                    confirmed_card[cell_name]["confirmed"] = True
                    confirmation_message += f"<@{card_content['id']}>\n"
                    confirmation_message += "~~" + prediction + "~~ :white_check_mark:\n"
                else:
                    confirmed_card[cell_name]["confirmed"] = card_content["card"][cell_name]["confirmed"]
            save_card(file_path, card_content["id"], 0, confirmed_card)
        data.close()
    if confirmation_message == "":
        confirmation_message = "No one with that prediction. Make sure it's not a typo."
    await ctx.send(confirmation_message)

bot.run(config.token)
