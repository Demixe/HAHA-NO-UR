import discord
import random
import json
import requests
import asyncio
import scout_image_generator

API_URL = "http://schoolido.lu/api/"

# Constants for scouting rates
R_RATE = 0.80
SR_RATE = 0.15
SSR_RATE = 0.04
UR_RATE = 0.01

client = discord.Client()

'''
Generates a random rarity based on the defined scouting rates

guarenteed_sr: Boolean -

return: String - rarity represented as a string ("UR", "SSR", "SR", "R")
'''
def roll_rarity(guarenteed_sr = False):
    roll = random.uniform(0, 1)

    if roll < UR_RATE:
        return "UR"
    elif roll < SSR_RATE:
        return "SSR"
    elif roll < SR_RATE:
        return "SR"
    else:
        if guarenteed_sr:
            return "SR"
        else:
            return "R"

'''
Scouts a single card

return: Dictionary - card scouted
'''
async def scout_card():
        # Build request url
        request_url = API_URL + "cards/?rarity=" + roll_rarity()
        request_url += "&ordering=random"
        request_url += "&is_promo=False"
        request_url += "&is_special=False"
        request_url += "&page_size=1"

        response = requests.get(request_url)
        response_obj = json.loads(response.text)

        return response_obj["results"][0]

'''
Scouts a specified number of cards of a given rarity

count: Integer - number of cards to scouted
rarity: String - rarity of all cards in scout

return: List - cards scouted
'''
def scout_by_rarity(count, rarity):
    # Build request url
    request_url = API_URL + "cards/?rarity=" + rarity
    request_url += "&ordering=random"
    request_url += "&is_promo=False"
    request_url += "&is_special=False"
    request_url += "&page_size=" + str(count)

    response = requests.get(request_url)
    response_obj = json.loads(response.text)

    return response_obj["results"]

'''
Scouts a specified number of cards

count: Integer - number of cards to scouted
guarenteed_sr: Boolean - whether at least one card in the scout will be an SR

return: List - cards scouted
'''
def scout_cards(count, guarenteed_sr = False):
    rarities = []

    if guarenteed_sr:
        for r in range(0, count - 1):
            rarities.append(roll_rarity())

        if rarities.count("R") == count:
            rarities.append(roll_rarity(True))
    else:
        for r in range(0, count):
            rarities.append(roll_rarity())

    results = []
    results.append(scout_by_rarity(rarities.count("R"), "R"))
    results.append(scout_by_rarity(rarities.count("SR"), "SR"))
    results.append(scout_by_rarity(rarities.count("SSR"), "SSR"))
    results.append(scout_by_rarity(rarities.count("UR"), "UR"))

    return results

'''
Checks if a card belongs to a minor idol unit (Saint Snow, A-RISE)

card: Dictionary - card being checked

return: Boolean - True if minor unit, otherwise False
'''
def is_minor_unit(card):
    unit = card["idol"]["main_unit"]
    return (unit == "A-RISE") or (unit == "Saint Snow")

@client.event
async def on_message(message):
    reply = ""

    try:
        if message.content.startswith("!scout"):
            card = scout_card()
            reply = "<@" + message.author.id + "> "

            if card["card_image"] == None:
                reply += "http:" + card["card_idolized_image"]
            else:
                reply += "http:" + card["card_image"]

        if message.content.startswith("!scout11"):
            cards = scout_cards(11, True)
            circle_image_urls = []

            for each card in cards:
                if card["round_card_image"] == None:
                    circle_image_urls.append(
                        "http:" + card["round_card_image"]
                    )
                else:
                    circle_image_urls.append(
                        "http:" + card["round_card_idolized_image"]
                    )

            scout_image_generator(
                create_image(circle_image_urls, 2, message.author.id + ".png")
            )


    except Exception as e:
        reply = "<@" + message.author.id + "> A transmission error occured."
        print(str(e))

    await client.send_message(message.channel, reply)

@client.event
async def on_ready():
    print("Logged in")

# Get login token from text file and run client
fp_token = open("token.txt", "r")
token = fp_token.read().strip("\n")
client.run(token)
