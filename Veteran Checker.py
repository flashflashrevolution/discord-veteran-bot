from datetime import datetime
import discord
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import mechanize
import http.cookiejar
import hashlib
import json
from discord import utils
import random


load_dotenv()
client = discord.Client()

# Prints in the terminal when the bot is able to access Discord upon start up.


@client.event
async def on_ready():
    print("We have connected to Discord as Veteran Checker. ")


def get_page(url: str) -> str:
    response: str = requests.get(url)
    # Checks if the bot was unable to connect to the server.
    if not response.ok:
        print("Server responded: " + response.status_code)
    else:
        # Reads the specified url's html contents and stores it in soup variable.
        soup: str = BeautifulSoup(response.text, "html.parser")
    return soup


def get_detail_data(soup) -> bool:
    # usergroup ug49 is the Veteran usergroup on the website.

    # Checks the html contents for the text "49".
    check: str = soup.contents
    if "49" in check[0]:
        vet: bool = True
        print(check)
        return vet
    else:
        vet: bool = False
        return vet


def main(name: str) -> str:
    # URL which allows the bot to check usergroups.
    f: str = f"{name}"
    url: str = os.getenv("url")
    url: str = url + f
    # Checks if the account with specified username is in the Veteran usergroup.
    vet: bool = get_detail_data(get_page(url))
    if vet is True:
        return (
            "Account is confirmed to be Veteran. \nA security code has been sent in "
            "a private message to the FFR account, "
            "please copy that code and send it here on Discord."
        )
    else:
        return f"This account is not Veteran yet: {name}"


# Log into the website


def log_in() -> None:
    # Opens the main page of the website.
    url = br.open("https://www.flashflashrevolution.com/")
    # Reads the HTML of the page.
    url.read()
    # Checks if the password related cookie has expired.
    for cookie in iter(cj):
        # If cookie not expired, exit the function.
        if cookie.name == "bbpassword":
            return
    # Locates the username input box and sets it to username.
    br.form = list(br.forms())[0]
    br["vb_login_username"] = os.getenv("uname")
    # Locates the password input box and sets it to password.
    br["vb_login_password"] = os.getenv("password")
    # Clicks the submit PM button.
    br.submit()


def send_pm(name: str, security_code: str) -> None:
    # URL which has the PM submission field.
    url: mechanize.response_seek_wrapper = br.open(
        "https://www.flashflashrevolution.com/vbz/private.php?do=newpm"
    )
    url.read()
    # Identifies and focuses on the required field to send a PM.
    br.select_form("vbform")
    # Fills out those fields.
    br["recipients"] = name
    br["title"] = "Discord Verification"
    br["message"] = (
        f"Here is your security code:\n[code]&{security_code}[/code]\n\n"
        "Please send it back to me in a Discord direct message."
    )
    # Sends the specified user a PM on the website.
    br.submit()


br = mechanize.Browser()
# Set Cookie Jar so we can stay logged in...
cj = http.cookiejar.LWPCookieJar()
br.set_cookiejar(cj)


@client.event
async def on_message(message):

    # Ignores the message if it was sent by the bot.
    if message.author == client.user:
        return
    # Ignores the message if it was sent by another bot.
    if message.author.bot:
        return

    """Vet Command

    A command that checks if the specified account on the website is Veteran,
    sends it a PM with a code, and gives the Veteran role on Discord
    when given an active security key.
    """
    if message.content.startswith("$vet "):
        message.author

        # Stores the necessary info to mention the user.
        user_id: str = "<@!"
        user_id += str(message.author.id)
        user_id += ">"

        # Sets the boolean to false by default.
        uid_no_exists: bool = False
        # Opens the json file to read the archived users, if user is not found then boolean is set to true.
        with open("limited_IDs.json", "r") as limited_IDs:
            file = json.load(limited_IDs)
            # Sets to true if the Discord user has requested a code before.
            uid_no_exists = user_id not in file
        if uid_no_exists:

            # Stores the account name in a variable.
            name: str = message.content.replace("$vet ", "")
            # Makes name lower case to prevent duplicates in the archives.
            name = str(name.lower())

            # Checks if user has the Veteran role on Discord.
            veteran = discord.utils.get(message.author.roles, name="Veteran")
            if veteran is None:

                # Sets boolean to default false.
                received_pm: bool = False
                # Checks if the account has already received a PM.
                with open("logs.json", "r") as read_logs:
                    file = json.load(read_logs)
                    # Sets to true if account hasn't received PM.
                    received_pm = name in file
                if not received_pm:

                    # Checks to see if account is Veteran on the website.
                    check: str = main(name)
                    if check != f"This account is not Veteran yet: {name}":
                        # Tells the user the account is confirmed to be Veteran and that the PM has been sent.
                        await message.author.send(check)

                        # Logs in to the website.
                        log_in()
                        # Generates a new security code.
                        rndm: int = random.randrange(100000000, 999999999)
                        security_code: str = hashlib.sha1(
                            (str(rndm) + name + str(datetime.now())).encode("utf-8")
                        ).hexdigest()
                        # Sends the specified account a PM with a security code.
                        send_pm(name, security_code)
                        print("PM has been sent.")

                        # Since a & is added to the beginning in the function that sends the PM, we have to add it here.
                        security_code: str = "&" + security_code
                        # Ties the account name to the security code sent and archives it.
                        with open("logs.json", "r+") as write:
                            file = json.load(write)
                            write.seek(0)
                            write.truncate(0)
                            file[name] = security_code
                            json.dump(file, write)

                        # Archives the Discord user who requested the code so they may not send any more PMs.
                        with open("limited_IDs.json", "r+") as write:
                            limited_IDs = json.load(write)
                            limited_IDs.append(user_id)
                            write.seek(0)
                            write.truncate(0)
                            json.dump(limited_IDs, write)
                    else:
                        await message.channel.send(
                            f"This account is not Veteran yet: {name}"
                        )
                else:
                    await message.channel.send(
                        "This account has already received a PM."
                    )
            else:
                await message.channel.send(
                    "You already have the Veteran role on Discord."
                )
        else:
            await message.channel.send(
                "You can no longer request a vet code. If you feel this is a mistake, please ping a staff member."
            )
    """Allow command
    A command for staff members to let the user to request a vet code from the bot if they are currently restricted.
    """
    if message.content.startswith("$allow "):
        # Checks to see if the user trying to use the command is a staff member.
        staff = discord.utils.get(message.author.roles, name="FFR Staff")
        if staff != None:

            # Splits the content of the message by spaces.
            list = message.content.split()
            
            # Checks to see if the staff member mentioned a user.
            ID_num: str = str(list[1])
            if ID_num.startswith("<@!"):

                # Checks the archives to see if the specified mention is there.
                with open("limited_IDs.json", "r") as limited_IDs:
                    file = json.load(limited_IDs)

                # If the specified mention is there, unarchive it.
                if str(ID_num) in file:
                    file.remove(str(ID_num))
                    with open("limited_IDs.json", "r+") as write:
                        write.seek(0)
                        write.truncate(0)
                        json.dump(file, write)
                    await message.channel.send("The user may now request a code.")
                else:
                    await message.channel.send(
                        "The specified Discord user is not currently limited."
                    )
            else:
                await message.channel.send(
                    "Message needs to @mention the Discord user."
                )
        else:
            await message.channel.send("Only FFR staff may use this command.")
    """Resend command
    A command for staff members to override any archives and resend a security code to a newly specified account.
    """
    if message.content.startswith("$resend "):
        # Checks if the user attempting to use the command is a staff member.
        roles = discord.utils.get(message.author.roles, name="FFR Staff")
        staff = roles
        if staff is not None:

            # Identifies the name of the account.
            name: str = message.content.replace("$resend ", "")
            await message.channel.send("Another vet code has been sent.")

            # Logs in to the website.
            log_in()
            # Generates a new security code.
            rndm: int = random.randrange(100000000, 999999999)
            security_code: str = hashlib.sha1(
                (str(rndm) + name + str(datetime.now())).encode("utf-8")
            ).hexdigest()

            # Sends the account the security code.
            send_pm(name, security_code)
            print("PM has been sent.")

            # Since a & is added to the beginning in the function that sends the PM, we have to add it here.
            security_code: str = "&" + security_code
            # Ties the account name to the security code sent and archives it.
            with open("logs.json", "r+") as write:
                file = json.load(write)
                write.seek(0)
                write.truncate(0)  # CHECK IF IT CREATES DUPLICATES IN THE JSON
                file[name] = security_code
                json.dump(file, write)
        else:
            await message.channel.send("Only FFR staff may use this command.")
    """Auto Moderation
    Checks for security codes posted in chat.
    """
    # Checks if message is sent in the server.
    if not isinstance(message.channel, discord.channel.DMChannel):
        # If the message starts with a &, it is likely a Discord user trying to post their security code.
        if message.content.startswith("&"):
            potential_key: str = message.content

            # Checks if the message is an active security key.
            with open("logs.json", "r") as read:
                file = json.load(read)
                # key_identified and key,value are two different keys. First is the security key, second is the key in the dictionary archive.
                key_identified: bool = False
                # Iterates through the archives to see if the message matches a key.
                for key, value in file.items():
                    if potential_key == value:
                        key_identified = True
                if key_identified:
                    await message.delete()
                    await message.channel.send("Do not post a vet code in the server!")
                else:
                    # Checks to make sure the message isn't a disabled security key.
                    for key, value in file.items():
                        disabled_key: str = value
                        # Removes the # at the end of the key because users would not have that in their security key.
                        disabled_key: str = disabled_key.replace("#", "")
                        if disabled_key == potential_key:
                            await message.delete()
                            await message.channel.send(
                                "Do not post a vet code in the server!"
                            )
    """Auto moderation
    Moderation code for @ everyone and phishing links.
    """
    if not isinstance(message.channel, discord.channel.DMChannel):
        if message.content.startswith("@everyone"):
            # Checks if the Discord user is an admin, mod, or staff.
            staff = discord.utils.get(message.author.roles, name="FFR Staff")
            admin = discord.utils.get(message.author.roles, name="Discord Admin")
            mod = discord.utils.get(message.author.roles, name="Discord Mod")
            if mod is None and admin is None and staff is None:

                # Makes the message content all lower case to easily parse.
                check: str = message.content.lower()

                # Checks for common phishing keywords.
                if "nitro" in check or "http" in check:

                    # Deletes the message.
                    await message.delete()

                    # Server specific variable
                    channel = client.get_channel(683479124182171712)
                    # Server specific variable
                    guild_id: int = 196381154880782336
                    # Gives the Discord user the Timeout role.
                    guild = client.get_guild(guild_id)
                    var = utils.get(guild.roles, name="Timeout")
                    member = await guild.fetch_member(message.author.id)
                    await member.add_roles(var)

                    # Generates the message to send.
                    new_msg: str = f"Potential phishing scam by <@!{message.author.id}> detected.\n\n Message contents: ```{message.content}```"

                    # Checks if the bot has already notified about this user.
                    same: bool = False
                    with open("old_msg.json", "r") as read:
                        old_msg = json.load(read)
                        if old_msg == new_msg:
                            same = True
                    if not same:

                        # If the mods have not been notified of this user yet, archive the message and notify.
                        print("Phishing scam detected.")
                        with open("old_msg.json", "r+") as write:
                            file = json.load(write)
                            write.seek(0)
                            write.truncate(0)
                            json.dump(new_msg, write)
                        await channel.send(new_msg)
        else:
            # Checks if the Discord user has no roles and has mentioned more than 5 people.
            if (
                message.author.top_role.name == "@everyone"
                and len(message.mentions) > 5
                and "http" in message.content
            ):

                # Deletes the message.
                await message.delete()

                # Server specific variable
                channel = client.get_channel(683479124182171712)
                # Server specific variable
                guild_id: int = 196381154880782336
                # Gives the Discord user the Timeout role.
                guild = client.get_guild(guild_id)
                var = utils.get(guild.roles, name="Timeout")
                member = await guild.fetch_member(message.author.id)
                await member.add_roles(var)

                # Generates the message to send.
                new_msg: str = f"Potential phishing scam by <@!{message.author.id}> detected.\n\n Message contents: ```{message.content}```"

                # Checks if the bot has already notified about this user.
                same: bool = False
                with open("old_msg.json", "r") as read:
                    old_msg = json.load(read)
                    if old_msg == new_msg:
                        same = True
                if not same:

                    # If the mods have not been notified of this user yet, archive the message and notify.
                    print("Phishing scam detected.")
                    with open("old_msg.json", "r+") as write:
                        file = json.load(write)
                        write.seek(0)
                        write.truncate(0)
                        json.dump(new_msg, write)
                    await channel.send(new_msg)
    """DM checking script
    Checks direct messages for security keys"""
    if isinstance(message.channel, discord.channel.DMChannel):
        # If the message starts with a &, it is likely a Discord user trying to post their security code.
        if message.content.startswith("&"):
            potential_key: str = message.content

            # Checks if the message is an activated security key.
            correct_key: bool = False
            check: bool = True
            with open("logs.json", "r") as read:
                file = json.load(read)
                correct_key = potential_key in file.values()
                if not correct_key:

                    # Checks if the message is a deactivated security key.
                    for key, value in file.items():
                        disabled_key = value
                        disabled_key = disabled_key.replace("#", "")
                        if disabled_key == potential_key:
                            check: bool = False
                            await message.channel.send(
                                "You have tried to use a vet code that has been deactivated."
                            )
            if correct_key:
                # Disables the security key if currently activated.
                with open("logs.json", "r+") as write:
                    file = json.load(write)
                    for key, value in file.items():
                        if value == potential_key:
                            write.seek(0)
                            write.truncate(0)
                            disabled_key = str(value)
                            disabled_key += "#"
                            file[key] = disabled_key
                            json.dump(file, write)
                            
                # Server specific variable
                guild_id: int = 196381154880782336
                # Gives the Discord user the Veteran role on the Discord server.
                guild = client.get_guild(guild_id)
                var = utils.get(guild.roles, name="Veteran")
                member = await guild.fetch_member(message.author.id)
                await member.add_roles(var)
                print("Key has been received; Veteran given out.")
                await message.channel.send(
                    "You have been given the Veteran role on the Discord server!"
                )
            elif check:
                # Sends this string to the user if their message starts with & and isn't a known security key.
                await message.channel.send("Invalid vet code.")


client.run(os.getenv("token"))
