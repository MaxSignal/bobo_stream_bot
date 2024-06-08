import csv
import json
import time

import discord
import requests

# https://github.com/NGnius/rcbup/tree/master/rcapi
from rcapi import factory, auth

WEBHOOK_URL = ""

tier = [1000, 6434, 79999, 1299999]
with open("./cube_database.csv", "r", encoding='UTF-8') as f:
    data_name, data, health, mass = zip(*[(row[0], row[1], row[2], row[3]) for row in csv.reader(f) if row[1].isdecimal()])
last = int(factory.factory_list(auth.fj_login()['Token'], factory.make_search_body())[0]["itemId"])

def get_bots():
    global last
    result = []

    count_bot = 0
    failed = 0
    while(1):
        try:
            if failed >= 2:
                count_bot -= failed
                break
            bot_info = factory.factory_bot("", last + count_bot + 1)
            print('Getting %s...' % (bot_info["name"]))
            result.append(bot_info)
            failed = 0
            count_bot += 1
        except:
            failed += 1
            count_bot += 1

    if len(result) > 0:
        last = result[-1]["id"]
    else:
        return result

    embeds = []
    for i in range(len(result)):
        if int(result[i]["cpu"]) > 2000:
            _tier = "TM"
        elif int(result[i]["totalRobotRanking"]) <= tier[0]:
            _tier = 1
        elif int(result[i]["totalRobotRanking"]) <= tier[1]:
            _tier = 2
        elif int(result[i]["totalRobotRanking"]) <= tier[2]:
            _tier = 3
        elif int(result[i]["totalRobotRanking"]) <= tier[3]:
            _tier = 4
        else:
            _tier = 5

        cubelist = ""
        cubedata = json.loads(result[i]["cubeAmounts"])
        keys = list(cubedata.keys())
        for k in range(len(data)):
            for j in range(len(cubedata)):
                if data[k] == keys[j]:
                    cubelist += data_name[k] + ": " + str(cubedata[keys[j]]) + "\n"
                    btmass += float(mass[k]) * cubedata[keys[j]]
                    bthealth += int(health[k]) * cubedata[keys[j]]

        embeds.append(discord.Embed(description=
                                    "**Name**: `" + result[i]["name"] + "`\n" +
                                    "**Builder**: " + result[i]["addedBy"] + " aka " + result[i]["addedByDisplayName"] + "\n" +
                                    "**CPU**: " + str(result[i]["cpu"]) + "\n" +
                                    "**Tier**: " + str(_tier) + "\n" +
                                    "**Health**: " + '{:,}'.format(bthealth) + "\n" + 
                                    "**Mass**: " + str(btmass) + "\n" +
                                    "**Cubes**: \n" + cubelist +
                                    "**Description**: \n```" + result[i]["description"] + "```" +
                                    "**ExpireDate**: " + result[i]["expiryDate"]))
        embeds[i].set_footer(text="ID: " + str(result[i]["id"]) + " • " + result[i]["addedDate"])
        embeds[i].set_image(url=result[i]["thumbnail"])

    n = 10
    result = [embeds[idx:idx + n] for idx in range(0,len(embeds), n)]
    return result

def loop():
    embeds = get_bots()
    if len(embeds) == 0:
        return

    for i in range(len(embeds)):
        data = {'embeds': [embed.to_dict() for embed in embeds[i]]}
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code >= 400:
            print(f'Failed to send embeds. Status code: {response.status}, Response: {response.text()}')

while(1):
    loop()
    time.sleep(5)