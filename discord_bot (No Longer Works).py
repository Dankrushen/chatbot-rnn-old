from chatbot import libchatbot
import discord
import asyncio

logName = "Discord-Bot_Session.log"
logFile = open(logName, "a")

print('Loading Chatbot-RNN...')
consumer = libchatbot()
# consumer("Hi")
print('Chatbot-RNN has been loaded.')

print('Preparing Discord Bot...')
client = discord.Client()

@client.event
async def on_ready():
    print()
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print()
    print('Discord Bot ready!')

@client.event
async def on_message(message):
    if message.content.startswith('>'):
        msgContent = '';
        if message.content.startswith('> '):
            msgContent = message.content.replace('> ', '', 1);
        elif message.content.startswith('>'):
            msgContent = message.content.replace('>', '', 1);
        
        if not msgContent == '':
            await client.send_typing(message.channel)
            print()
            print('\"' + msgContent + '\"')
            logFile.write('\n\"' + msgContent + '\"')
            result = consumer(msgContent)
            await client.send_message(message.channel, result)
            print('> ' + result)
            logFile.write('\n> ' + result)
            logFile.write('\n')
        else:
            await client.send_message(message.channel, 'Error: Missing message!')

client.run('Bot Token Goes Here')
