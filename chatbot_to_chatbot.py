from chatbot import libchatbot
import os.path
import time
import pickle as cPickle
from random import randint

log_name = "Chatbot_to_Chatbot_Session.log"
log_file = open(log_name, "a")

main_states_file = "chat2chat"
temp_states_file = main_states_file + "_temp"
last_message_file = main_states_file + "_last_message"

total_bot_count = 8

bot_number = 0 # Starting value
last_message = ["Hi", 0] # Starts at 0 so the first chatbot has something to work off of
current_message = last_message

print('Loading Chatbot-RNN...')
save, load, reset, consumer = libchatbot()
print('Chatbot-RNN has been loaded.')

def save_last_message():
    global last_message
    with open(last_message_file + '.pkl', 'wb') as f:
            cPickle.dump(last_message, f)
            
def load_last_message():
    global last_message
    with open(last_message_file + '.pkl', 'rb') as f:
        last_message = cPickle.load(f)

if os.path.exists(last_message_file + ".pkl") and os.path.isfile(last_message_file + ".pkl"):
    load_last_message()
    print('Loaded the last message sent.')
    print()
    print('Chatbot #' + str(last_message[1]) + ' > ' + last_message[0])
else:
    print('Initial Message > ' + last_message[0])    

while True:
    reset()

    random_bot = randint(1, total_bot_count)
    bot_number = random_bot

    while random_bot == last_message[1]:
        random_bot = randint(1, total_bot_count)
        bot_number = random_bot

    # Let all bots get context from the last message
    for bot_num_index in range(1, total_bot_count + 1):
        if not bot_num_index == last_message[1]:
            # Chatbot Loading
            if os.path.exists(main_states_file + str(bot_num_index) + ".pkl") and os.path.isfile(main_states_file + str(bot_num_index) + ".pkl"):
                load(main_states_file + str(bot_num_index))
            
            # Chatbot Message
            print()
            print('Processing Chatbot #' + str(bot_num_index) + ' out of ' + str(total_bot_count) + (' (Chosen response)' if bot_num_index == bot_number else '') + '...')
            result = consumer(last_message[0])
            print('Done > ' + result)

            # If the bot is the random bot, set the current message to it's response
            if bot_num_index == bot_number:
                current_message = [result, bot_number]
            
            # Chatbot Temporary Saving (Instead of caching all the states now and using a lot of memory, save it)
            save(temp_states_file + str(bot_num_index))
        else:
            print()
            print('Skipping Chatbot #' + str(bot_num_index) + ', it was the sender...')

    # Save all bots from the temporary state files
    print()
    print('Do not close program! Saving bot states and the chosen response...')
    print()
    for bot_num_index in range(1, total_bot_count + 1):
        if not bot_num_index == last_message[1]:
            # Chatbot Loading (Doesn't check if it exists, it absolutely should)
            # If it doesn't, this will create an error, though that's good, because something did go wrong
            load(temp_states_file + str(bot_num_index))
            
            # Display current progress
            print('Saving Chatbot #' + str(bot_num_index) + ' out of ' + str(total_bot_count) + '...')
            
            # Chatbot Saving (From temporary file to main)
            save(main_states_file + str(bot_num_index))

            # Delete temporary file to clean up
            os.remove(temp_states_file + str(bot_num_index) + ".pkl")
        else:
            print('Skipping Chatbot #' + str(bot_num_index) + ', it was the sender...')

    print()
    print('Saving response...')
    last_message = current_message
    save_last_message()

    print()
    print('Bot states and the chosen response have been saved! You can close the program now.')
    
    print()
    print()
    print('Chatbot #' + str(bot_number) + ' > ' + last_message[0])
    log_file.write('Chatbot #' + str(bot_number) + ' > ' + last_message[0])
    print()
    log_file.write('\n\n')
