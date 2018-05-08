from chatbot import libchatbot
import discord
import os
import json

try: # Unicode patch for Windows
    import win_unicode_console
    win_unicode_console.enable()
except:
    if os.name == 'nt':
        import sys
        if sys.version_info < (3,6):
            print("Please install the 'win_unicode_console' module.")

log_name = "Discord-Bot_Session.log"

states_file = "general"
autosave = True

user_settings_folder = "user_settings"
ult_operators_file = user_settings_folder + "/" + "ult_operators.cfg"
operators_file = user_settings_folder + "/" + "operators.cfg"
banned_users_file = user_settings_folder + "/" + "banned_users.cfg"

ult_operators = []
operators = []
banned_users = []

temperature = 1.2
relevance = 0.2
topn = 6
max_length = 500

print('Loading Chatbot-RNN...')
save, load, reset, change_settings, consumer = libchatbot(temperature=temperature, relevance=relevance, topn=topn, max_length=max_length)
if os.path.exists(states_file + ".pkl") and os.path.isfile(states_file + ".pkl"):
    load(states_file)
    print('Loaded pre-existing Chatbot-RNN states.')
print('Chatbot-RNN has been loaded.')

print('Preparing Discord Bot...')
client = discord.Client()

def log(message):
    with open(log_name, "a", encoding="utf-8") as log_file:
        log_file.write(message)

@client.event
async def on_ready():
    print()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print()
    print('Discord Bot ready!')

def make_folders():
    if not os.path.exists(user_settings_folder):
        os.makedirs(user_settings_folder)

def is_discord_id(user_id):
    # Quick general check to see if it matches the ID formatting
    return user_id.isdigit and len(user_id) == 18

def remove_invalid_ids(id_list):
    for user in id_list:
        if not is_discord_id(user):
            id_list.remove(user)

def save_ops_bans():
    global ult_operators, operators, banned_users

    make_folders()

    # Sort and remove duplicate entries
    ult_operators = list(set(ult_operators))
    operators = list(set(operators))
    banned_users = list(set(banned_users))

    # Remove from list if ID is invalid
    remove_invalid_ids(ult_operators)

    # Remove them from the ban list if they were added
    # Op them if they were removed
    for user in ult_operators:
        operators.append(user)
        if user in banned_users:
            banned_users.remove(user)

    # Remove from list if ID is invalid
    remove_invalid_ids(operators)

    # Remove from list if ID is invalid
    remove_invalid_ids(banned_users)

    # Sort and remove duplicate entries
    ult_operators = list(set(ult_operators))
    operators = list(set(operators))
    banned_users = list(set(banned_users))

    with open(ult_operators_file, 'w') as f:
        f.write(json.dumps(ult_operators))
    with open(operators_file, 'w') as f:
        f.write(json.dumps(operators))
    with open(banned_users_file, 'w') as f:
        f.write(json.dumps(banned_users))

def load_ops_bans():
    global ult_operators, operators, banned_users

    make_folders()

    if os.path.exists(ult_operators_file) and os.path.isfile(ult_operators_file):
        with open(ult_operators_file, 'r') as f:
            try:
                ult_operators = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                ult_operators = []

    if os.path.exists(operators_file) and os.path.isfile(operators_file):
        with open(operators_file, 'r') as f:
            try:
                operators = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                operators = []

    if os.path.exists(banned_users_file) and os.path.isfile(banned_users_file):
        with open(banned_users_file, 'r') as f:
            try:
                banned_users = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                banned_users = []

    save_ops_bans()

# Prepare the operators and ban lists
load_ops_bans()

async def process_command(msg_content, message):
    global states_file, save, load, reset, change_settings, consumer, autosave
    user_command_entered = False
    response = ""

    load_ops_bans()

    if message.author.id in banned_users:
        user_command_entered = True
        
        response = "Sorry, you have been banned."
    else:
        if msg_content.startswith('--reset'):
            user_command_entered = True
            if message.author.id in operators:
                reset()
                print()
                print("[Model state reset]")
                response = "Chatbot state reset."
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--save '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--save '):]
                save(input_text)
                print()
                print("[Saved states to \"{}.pkl\"]".format(input_text))
                response = "Saved Chatbot state to \"{}.pkl\".".format(input_text)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--load '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--load '):]
                load(input_text)
                print()
                print("[Loaded saved states from \"{}.pkl\"]".format(input_text))
                response = "Loaded saved Chatbot state from \"{}.pkl\".".format(input_text)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--autosave '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--autosave '):]
                states_file = input_text
                load(states_file)
                print()
                print("[Loaded saved states from \"{}.pkl\" and is now the default autosave destination]".format(input_text))
                response = "Loaded saved Chatbot state from \"{}.pkl\" and is now default autosave destination.".format(input_text)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--autosaveon'):
            user_command_entered = True
            if message.author.id in operators:
                if not autosave:
                    autosave = True
                    print()
                    print("[Turned on autosaving (Currently saving to \"{}.pkl\")]".format(states_file))
                    response = "Turned on autosaving (Currently saving to \"{}.pkl\").".format(states_file)
                else:
                    response = "Autosaving is already on (Currently saving to \"{}.pkl\").".format(states_file)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--autosaveoff'):
            user_command_entered = True
            if message.author.id in operators:
                if autosave:
                    autosave = False
                    print()
                    print("[Turned off autosaving]")
                    response = "Turned off autosaving."
                else:
                    response = "Autosaving is already off."
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--op '):
            user_command_entered = True
            if message.author.id in operators:
                # Replacements are to support mentioned users
                input_text = msg_content[len('--op '):].replace('<@', '').replace('!', '').replace('>', '')
                user_exists = True
                
                # Check if user actually exists
                try:
                    await client.get_user_info(input_text)
                except discord.NotFound:
                    user_exists = False
                except discord.HTTPException:
                    user_exists = False
                
                if not input_text in ult_operators and user_exists:
                    load_ops_bans()
                    operators.append(input_text)
                    save_ops_bans()
                    print()
                    print("[Opped \"{}\"]".format(input_text))
                    response = "Opped \"{}\".".format(input_text)
                else:
                    response = "Error: Unable to op user \"{}\".".format(input_text)
            else:
                response = "Error: Insufficient permissions."

        elif msg_content.startswith('--deop '):
            user_command_entered = True
            if message.author.id in operators:
                # Replacements are to support mentioned users
                input_text = msg_content[len('--deop '):].replace('<@', '').replace('!', '').replace('>', '')
                user_exists = True
                
                # Check if user actually exists
                try:
                    await client.get_user_info(input_text)
                except discord.NotFound:
                    user_exists = False
                except discord.HTTPException:
                    user_exists = False
                
                if not input_text in ult_operators and user_exists:
                    load_ops_bans()
                    if input_text in operators:
                        operators.remove(input_text)
                    save_ops_bans()
                    print()
                    print("[De-opped \"{}\"]".format(input_text))
                    response = "De-opped \"{}\".".format(input_text)
                else:
                    response = "Error: Unable to de-op user \"{}\".".format(input_text)
            else:
                response = "Error: Insufficient permissions."

        elif msg_content.startswith('--ban '):
            user_command_entered = True
            if message.author.id in operators:
                # Replacements are to support mentioned users
                input_text = msg_content[len('--ban '):].replace('<@', '').replace('!', '').replace('>', '')
                user_exists = True
                
                # Check if user actually exists
                try:
                    await client.get_user_info(input_text)
                except discord.NotFound:
                    user_exists = False
                except discord.HTTPException:
                    user_exists = False
                
                if not input_text in ult_operators and user_exists:
                    load_ops_bans()
                    banned_users.append(input_text)
                    save_ops_bans()
                    print()
                    print("[Banned \"{}\"]".format(input_text))
                    response = "Banned \"{}\".".format(input_text)
                else:
                    response = "Error: Unable to ban user \"{}\".".format(input_text)
            else:
                response = "Error: Insufficient permissions."

        elif msg_content.startswith('--unban '):
            user_command_entered = True
            if message.author.id in operators:
                # Replacements are to support mentioned users
                input_text = msg_content[len('--unban '):].replace('<@', '').replace('!', '').replace('>', '')
                user_exists = True
                
                # Check if user actually exists
                try:
                    await client.get_user_info(input_text)
                except discord.NotFound:
                    user_exists = False
                except discord.HTTPException:
                    user_exists = False
                
                if not input_text in ult_operators and user_exists:
                    load_ops_bans()
                    if input_text in banned_users:
                        banned_users.remove(input_text)
                    save_ops_bans()
                    print()
                    print("[Un-banned \"{}\"]".format(input_text))
                    response = "Un-banned \"{}\".".format(input_text)
                else:
                    response = "Error: Unable to un-ban user \"{}\".".format(input_text)
            else:
                response = "Error: Insufficient permissions."
        
        elif msg_content.startswith('--temperature '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--temperature '):]
                returned = change_settings('temperature', input_text)
                print()
                print(str(returned))
                response = str(returned)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--relevance '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--relevance '):]
                returned = change_settings('relevance', input_text)
                print()
                print(str(returned))
                response = str(returned)
            else:
                response = "Insufficient permissions."
        
        elif msg_content.startswith('--topn '):
            user_command_entered = True
            if message.author.id in operators:
                input_text = msg_content[len('--topn '):]
                returned = change_settings('topn', input_text)
                print()
                print(str(returned))
                response = str(returned)
            else:
                response = "Insufficient permissions."
    
    return user_command_entered, response

@client.event
async def on_message(message):
    global save, load, reset, change_settings, consumer, states_file, autosave
    
    if message.content.startswith('>') and not message.author.bot:
        msg_content = '';
        if message.content.startswith('> '):
            msg_content = message.content[len('> '):]
        elif message.content.startswith('>'):
            msg_content = message.content[len('>'):]
        
        await client.send_typing(message.channel)
        
        if not msg_content == '':
            if not len(msg_content) > max_length:
                user_command_entered, response = await process_command(msg_content, message)

                if user_command_entered:
                    response = "<@" + message.author.id + "> - " + response
                    await client.send_message(message.channel, response)
                else:
                    print()
                    print('> ' + msg_content)
                    log('\n> ' + msg_content)
                    result = consumer(msg_content)

                    print()

                    if result == '':
                        result = "..."

                    result = "<@" + message.author.id + "> -" + result
                    
                    await client.send_message(message.channel, result)
                    #print('> ' + result)
                    log('\n' + result)
                    log('\n')
                    if autosave:
                        save(states_file)
            else:
                result = "<@" + message.author.id + "> - Error: Message too long, you sent " + str(len(msg_content)) + " characters, the maximum is " + str(max_length) + "!"
                await client.send_message(message.channel, result)
        else:
            result = "<@" + message.author.id + "> - Error: Missing message!"
            await client.send_message(message.channel, result)

client.run('Bot Token Goes Here', reconnect=True)
