#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.


Usage:

```python
python echobot.py
```

Press Ctrl-C on the command line to stop the bot.

"""

import logging

from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler,CallbackQueryHandler, filters
from urllib.parse import urlencode
from keys import TELEGRAM_KEY
from openai import OpenAI
from keys import OPENAI_KEY


import json

from utils import *
from utils_text import *


# Imports for the Google Maps API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

#################### IMPORTS FOR CONVERSATION ####################
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["city1", "city2"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Define a few command handlers. These usually take the two arguments update and
# context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    # user = update.effective_user
    # await update.message.reply_html(
    #     rf"Hi {user.mention_html()}!",
    #     reply_markup=ForceReply(selective=True),
    # )
    await update.message.reply_text(
    "Hi!  My name is TravelBot. I will hold a conversation with you. I would like to help you create your plan for a trip.",
    reply_markup=markup,
    )

    return CHOOSING


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#    """Echo the user message."""
#    await update.message.reply_text(update.message.text)

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Grabs an image of a brand and analzyes it.
    Args:
        update (Update): The update object from Telegram.
    """
    #photo_file = await update.message.photo[-1].get_file()
    #openai.api_key = OPENAI_KEY

    photo_file = await update.message.photo[-1].get_file()
    photo_path = photo_file.file_path

    client = OpenAI(api_key=OPENAI_KEY)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": """"Can you regonize device on this image?""" },
# """ 
# **Prompt for ChatGPT:**
# Hello ChatGPT, I need information about a monument. Based on the picture I want you to tell me what is the monument and if it is near our route . I don't remember
#     any more details. If you are not sure, please provide me info what could it be, even if you are not
#     sure about the answer. Please provide the following details based on the image or description provided:
# 1. **Name:** """}, 
                    {
                        #type of image is the local image file in photo_file
                        "type": "image",
                        "image_url": {
                            "url": photo_path,
                        },
                    },
                ],
            }
        ],
        max_tokens = 300,
    )

    # ...
    print(response.choices[0])
    # Extract the 'message' from the 'Choice' object and convert it to a JSON string
    message = json.dumps(response.choices[0].message.content)
    # Respond with the JSON string
    await update.message.reply_text(message)


# Assuming you are using aiogram for the async Telegram bot framework
async def text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ############################
    model = "gpt-3.5-turbo-1106"

    ############################
    json_file_path = "data.json"
    create_json_file(json_file_path)
    # Make sure to import necessary modules and types from aiogram

    # Use your OpenAI API key and initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_KEY)

    # Specify the prompt and other parameters for the chat completion
    #prompt = update.message.text

    ############################
    # Strap the text into from and to City
    # input = update.message.text
    # values = input.split(',')

    input_text = update.message.text
    input_text = input_text.replace(', ', ',').replace(' ,', ',').replace(' ', ',')
    values = [value.strip() for value in input_text.split(',')]

    # Extract the first two values (assuming at least two values are present)
    # fromCity = values[0].strip()
    # toCity = values[1].strip()

    if len(values) >= 2:
        fromCity, toCity = values[:2]
    else:
    # Handle the case where there are not enough values
        update.message.reply_text("Please provide at least two values for from and to cities.")
    add_info_to_json(json_file_path, "fromCity", fromCity)
    add_info_to_json(json_file_path, "toCity", toCity)
    

    ############################
    # Chatgpt question to get the viaAttractions fromCity toCity
    promptAttractions = f"""
        Can you provide 10 attractions on the route from {fromCity} to {toCity}, not further than 20 km from the route. Only names in list? Nothing more than names in a list."""

    # Create a chat completion request
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": promptAttractions}],
    )

    # Extract the assistant's message content from the response
    attractions_message = response.choices[0].message.content
    viaAttractions = preprocess_text(attractions_message)

    add_info_to_json(json_file_path, "viaAttractions", viaAttractions)

    ############################
    # Chatgpt question to get the viaCities fromCity toCity
    promptCities = f"""
        Are you able to provide me places for SBB and Google maps for those attractions: {promptAttractions}. Only names in list? Nothing more than places in a list"""

    # Create a chat completion request
    responseCities = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": promptCities}],
    )

    # Extract the assistant's message content from the response
    cities_message = responseCities.choices[0].message.content
    viaCities = preprocess_text(cities_message)

    add_info_to_json(json_file_path, "viaCities", viaCities)

    
    ############################
    # Chatgpt question to provide plan of the trip
    promptPlan = f"""
        Can you provide me a detailed plan of the trip from {fromCity} to {toCity} through attractions: {promptAttractions}. 
        Your response should include infomations where it is worth to eat around, which attractions are the most interesting.
        Which attractions are family-friendly. Your response should be more or less 500 words. Provide a response readable for humans."""
    
    responsePlan = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": promptPlan}],
    )

    # Extract the assistant's message content from the response
    plan_message = responsePlan.choices[0].message.content


    # Print the assistant's response details
    #print(response.choices[0])

    ############################
    # Maps
    #Google maps map

    viaCitiesGoogle = [city.replace(' ', '') for city in viaCities]
    viaCitiesGoogle = '/'.join(viaCitiesGoogle)
    google_map = f"https://www.google.com/maps/dir/{fromCity}/{viaCitiesGoogle}/{toCity}/"

    keyboard_google = [[InlineKeyboardButton("Google app link", url=google_map)]]
    # reply_markup_google = InlineKeyboardMarkup(keyboard_google)
    reply_markup_google = InlineKeyboardMarkup(keyboard_google, resize_keyboard=True, one_time_keyboard=True)
    
    # SBB map
    sbb_link = f"https://www.sbb.ch/en?date=%222023-12-02%22&moment=%22DEPARTURE%22&stops=%5B%7B%22value%22%3A%228501120%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{fromCity}"
    for city in viaCities:
        sbb_link += f"%22%7D%2C%7B%22value%22%3A%228504100%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{city}"
    sbb_map = sbb_link + f"%22%7D%2C%7B%22value%22%3A%228507000%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{toCity}%22%7D%5D&via=true"
    #sbb_map = f"https://www.sbb.ch/en?date=%222023-12-02%22&moment=%22DEPARTURE%22&stops=%5B%7B%22value%22%3A%228501120%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{fromCity}%22%7D%2C%7B%22value%22%3A%228504100%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{viaCities[0]}%22%7D%2C%7B%22value%22%3A%228507000%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{toCity}%22%7D%5D&"

    
    keyboard_sbb = [[InlineKeyboardButton("SBB app link", url=sbb_map)]]
    reply_markup_sbb = InlineKeyboardMarkup(keyboard_sbb)

    ############################
    # Response
    # Reply to the user with the assistant's message

    await update.message.reply_text(cities_message)
    await update.message.reply_text("Clink on the link below to see sbb route", reply_markup=reply_markup_sbb)
    await update.message.reply_text("Clink on the link below to see google map route", reply_markup=reply_markup_google)
    #await update.message.reply_text(attractions_message)
    await update.message.reply_text(plan_message)
    remove_json_file(json_file_path)

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

    return TYPING_REPLY


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE

async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.b
    application = Application.builder().token(TELEGRAM_KEY).build()
    
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(age|Favourite colour|Number of siblings)$"), regular_choice
                ),
                MessageHandler(filters.Regex("^Something else...$"), custom_choice),
            ],
             TYPING_CHOICE: [
                 MessageHandler(
                     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
                 )
             ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # application.add_handler(MessageHandler(filters.PHOTO, photo))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_prompt))

    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()