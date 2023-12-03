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

json_file_path = "data.json"
create_json_file(json_file_path)

START_STATE, FROMCITY_CHOICE, TOCITY_CHOICE, ATTRACTION_CHOICE, FINAL_STATE, TYPING_CHOICE, DONE = range(7)

# reply_keyboard = [
#     ["city1", "city2"],
#     ["Done"],
# ]
# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

# Define a few command handlers. These usually take the two arguments update and
# context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    id = update.message.text
    add_info_to_json(json_file_path, "userId", id)

    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Where do you want to start your trip?",
        reply_markup=ForceReply(selective=True),
    )
    return FROMCITY_CHOICE

async def fromCity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    
    #await update.message.reply_text(f"Provide in which city you want to finish your trip")
    #await update.message.reply_text(f"")
    fromCity = update.message.text
    add_info_to_json(json_file_path, "fromCity", fromCity)
    await update.message.reply_text(f"Provide in which city you want to finish your trip")

    return TOCITY_CHOICE

async def toCity_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    #await update.message.reply_text(f"Provide in which city you want to finish your trip")
    toCity = update.message.text
    add_info_to_json(json_file_path, "toCity", toCity)

    fromCity = get_info_from_json(json_file_path, "fromCity")
    await update.message.reply_text(f"You set your trip from {fromCity} to {toCity}. Ok?")
    return START_STATE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def start_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    client = OpenAI(api_key=OPENAI_KEY)
    model = "gpt-3.5-turbo-1106"

    fromCity = get_info_from_json(json_file_path, "fromCity")
    toCity = get_info_from_json(json_file_path, "toCity")
    

    ############################
    # Chatgpt question to get the viaAttractions fromCity toCity
    promptAttractions = f"""
        Can you provide 10 attractions on the route from {fromCity} to {toCity}, not further than 20 km from the route. Only names in list? Nothing more than names in a list.
        Dont add _ between words. The format of the output should be generated accroding to the example:
        1. Rigi Mountain
    2. Chapel Bridge
    3. Swiss Museum of Transport
    4. Lake Zug
    5. Hertenstein Castle
    6. Old Town of Zug
    7. Lindt Chocolate Factory Outlet
    8. Sihlwald Wildlife Park
    9. Uetliberg Mountain
    10. Bahnhofstrasse shopping street
        """

    # Create a chat completion request
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": promptAttractions}],
    )

    # Extract the assistant's message content from the response
    attractions_message = response.choices[0].message.content
    viaAttractions = preprocess_text(attractions_message)

    add_info_to_json(json_file_path, "viaAttractions", viaAttractions)

    await update.message.reply_text(f"""{attractions_message} \n Choose numbers of attractions you want to visit. You can select multiple attractions.""")
    #await update.message.reply_text(f"Choose numbers of attractions you want to visit. You can select multiple attractions")
    return ATTRACTION_CHOICE

async def attractions_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #print("Attractions choice")
    choosenNumbers = update.message.text
    attractions = get_info_from_json(json_file_path, "viaAttractions")

    choosenAttractions = [attractions[int(number)-1] for number in choosenNumbers.split(',')]
    add_info_to_json(json_file_path, "viaAttractions", choosenAttractions)

    #attractions_buttons = [[attraction] for attraction in attractions]
    #attractions_buttons.append(["Done"])
    # Create a ReplyKeyboardMarkup with the generated buttons
    #reply_markup = ReplyKeyboardMarkup(attractions_buttons, one_time_keyboard=False, resize_keyboard=True)
    #print(reply_markup)
    # Send a message with the generated buttons
    #add_info_to_json(json_file_path, "viaAttractions", reply_markup)

    await update.message.reply_text(f"You choose attractions: {', '.join(choosenAttractions)}. \nOk?")
    
    
    # if update.message.text == "Done":
    #     selected_attractions = context.user_data.get("selected_attractions", [])
    #     add_info_to_json(json_file_path, "selectedAttractions", selected_attractions)
        
    #     # End the conversation
    #     return ConversationHandler.END

    
    # selected_attractions = context.user_data.get("selected_attractions", [])
    # selected_attractions.append(update.message.text)
    # context.user_data["selected_attractions"] = selected_attractions
    
    
    return FINAL_STATE


async def final_output(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    client = OpenAI(api_key=OPENAI_KEY)
    model = "gpt-3.5-turbo-1106"
    ############################
    # Chatgpt question to get the viaCities fromCity toCity
    promptAttractions = get_info_from_json(json_file_path, "viaAttractions")
    fromCity = get_info_from_json(json_file_path, "fromCity")
    toCity = get_info_from_json(json_file_path, "toCity")


    # Generate a prompt for chat completion
    promptCities = f"""
    Provide names of the closest bus or train stops for the following attractions: {', '.join(promptAttractions)}. Only names in the list, nothing more.
    This is example output we expect:
    While you have attractions list: ['Lausanne Cathedral', 'Geneve Plage', 'Luzern Museum', 'Ecublens Castle']
    1. Lausanne, Gare
    2. Geneva, Cornavin
    3. Luzern, Bahnhof
    4. Ecublens, Villars
    But with the length of the list of attractions you provided.
    One place on the map per attraction.
    """

    responseCities = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": promptCities}],
    )

    # Extract the assistant's message content from the response
    print("Iam here")
    print(responseCities)
    cities_message = responseCities.choices[0].message.content
    print(cities_message)
    viaCities = preprocess_text(cities_message)

    # Print and add viaCities information to the JSON file
    print(viaCities)
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
    reply_markup_google = InlineKeyboardMarkup(keyboard_google)
    #reply_markup_google = InlineKeyboardMarkup(keyboard_google, resize_keyboard=True, one_time_keyboard=True)
    
    #viaCitiesSbb = [city.replace(' ', '') for city in viaCities]
    #viaCitieSbb = '/'.join(viaCitiesGoogle)
    filtered_list = [item.split('_')[0] for item in viaCities if '_' in item]
    filtered_list = list(set(filtered_list))
    print(filtered_list)
    # SBB map
    sbb_link = f"https://www.sbb.ch/en?date=%222023-12-02%22&moment=%22DEPARTURE%22&stops=%5B%7B%22value%22%3A%228501120%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{fromCity}"
    for city in filtered_list:
        sbb_link += f"%22%7D%2C%7B%22value%22%3A%228504100%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{city}"
    sbb_map = sbb_link + f"%22%7D%2C%7B%22value%22%3A%228507000%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{toCity}%22%7D%5D&via=true"
    #sbb_map = f"https://www.sbb.ch/en?date=%222023-12-02%22&moment=%22DEPARTURE%22&stops=%5B%7B%22value%22%3A%228501120%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{fromCity}%22%7D%2C%7B%22value%22%3A%228504100%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{viaCities[0]}%22%7D%2C%7B%22value%22%3A%228507000%22%2C%22type%22%3A%22ID%22%2C%22label%22%3A%22{toCity}%22%7D%5D&"

    
    keyboard_sbb = [[InlineKeyboardButton("SBB app link", url=sbb_map)]]
    reply_markup_sbb = InlineKeyboardMarkup(keyboard_sbb)

    ############################
    # Response
    # Reply to the user with the assistant's message

    await update.message.reply_text("Clik on the link below to see sbb route", reply_markup=reply_markup_sbb)
    await update.message.reply_text("Clik on the link below to see google map route", reply_markup=reply_markup_google)
    await update.message.reply_text(plan_message)
    remove_json_file(json_file_path)
    return DONE

async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE

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
            FROMCITY_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    fromCity_choice,
                )
            ],
            TOCITY_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    toCity_choice,
                )
            ],
            START_STATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    start_prompt,
                )
            ],
            ATTRACTION_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    attractions_choice,
                )
            ],
            FINAL_STATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    final_output,
                )
            ],
            DONE: [
                 MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    done,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done111$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    #remove_json_file(json_file_path)