import telebot
import redis
import time
import threading
import update_watcher



bot = telebot.TeleBot('TOKEN')

redis = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
# redis = redis.Redis(connection_pool=pool)

reminder_thread = threading.Thread(target=update_watcher.remind_user, args=(bot,redis), daemon=True)
reminder_thread.start()


@bot.message_handler(commands=['start'])
def start(message):
    
    
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row("Set a goal")
    markup.row("Update progress")
    markup.row("Stats")
    
    bot.send_message(message.chat.id, 'Welcome to the accountability bot!\n\n'
                     'Please choose an option:',
                     reply_markup=markup)
    # Move to the GOAL state
    bot.register_next_step_handler(message, handle_menu)

def handle_menu(message):
    
    if message.text == "Set a goal":
        if is_goal_defined(message):
            confirm_goal_overwrite(message)
        else:
            ask_for_goal(message)
            print("setting goal")
    if message.text == "Update progress":
        update_progress(message)
        print("updating progress")
    if message.text == "Stats":
        leaderboard()

def confirm_goal_overwrite(message):
    goal = redis.hget(message.from_user.username, 'goal')
    bot.send_message(message.chat.id, f"It seems you already have a goal defined: {goal} \n"
                                     "If you would like to remove the goal and reset your score type: /reset")

    
@bot.message_handler(commands=['reset'])
def reset_goal(message):
    bot.send_message(message.chat.id, "Your goal and score have been reset.\n"
                                        "Type /start to see the menu again")
    redis.hset(message.from_user.username, 'goal', "")
    redis.hset(message.from_user.username, 'goal_set_time', "")
    redis.hset(message.from_user.username, 'last_update_time', "")
    redis.hset(message.from_user.username, 'points', 0)
    redis.hset(message.from_user.username, 'progress', "")
    #ask_for_goal(message)
    

def is_goal_defined(message):
    
    if redis.hget(message.from_user.username, 'goal') != "":
        return True
    else:
        return False

def ask_for_goal(message):
    
    bot.send_message(message.chat.id, "Alright, what is your next goal?")
    bot.register_next_step_handler(message, set_goal)
    
def set_goal(message):
    # Save the goal in the user's data
    redis.hset(message.from_user.username, 'goal', message.text)
    redis.hset(message.from_user.username, 'goal_set_time', round(time.time()))
    redis.hset(message.from_user.username, 'last_update_time', round(time.time()))
    redis.hset(message.from_user.username, 'points', 10)
    redis.hset(message.from_user.username, 'chat_id', message.chat.id)
    
    
    bot.send_message(message.chat.id, f'Your goal "{message.text}" has been set.')
                     
    ask_frequency(message)
    
    
def ask_frequency(message):
    
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row("Minutely")
    markup.row("Daily")
    markup.row("Weekly")

    # Send a confirmation message
    bot.send_message(message.chat.id,"How often do you want to update your progress?", reply_markup=markup)
    
    print(message.text)
    bot.register_next_step_handler(message, set_frequency)

def set_frequency(message):
    
    redis.hset(message.from_user.username, 'freq', message.text)
    frequency = redis.hget(message.from_user.username, 'freq')

    bot.send_message(message.chat.id, f"Alright, your target for progress updates is {frequency}")


def update_progress(message):


    if message.text:
        redis.hincrby(message.from_user.username, 'points', 5)
    else:
        redis.hincrby(message.from_user.username, 'points', -5)
        points = redis.hget(message.from_user.username, 'points')
        if points < 0:
            redis.hset(message.from_user.username, 'points', 0)

    # Send a confirmation message
    bot.send_message(message.from_user.username, f'Your progress update "{message.text}" has been saved. '
                     'Keep up the good work!')

    # Move back to the GOAL state
    bot.register_next_step_handler(message, set_goal)



# Define the leaderboard function
@bot.message_handler(commands=['stats'])
def leaderboard(message):
    # Get all user data
    user_data = bot.user_data

    # Sort by points
    sorted_user_data = sorted(user_data.items(), key=lambda x: x[1].get('points', 0), reverse=True)

    # Create the leaderboard message
    leaderboard_message = 'Leaderboard:\n'
    for i, (user_id, data) in enumerate(sorted_user_data):
        points = data.get('points', 0)
        leaderboard_message += f'{i+1}. {data.get("name", "Unknown")}: {points} points\n'

    # Send the leaderboard message
    bot.send_message(message.chat.id, leaderboard_message)

# Define the cancel function
@bot.message_handler(commands=['dump'])
def dump(message):
    # Send a cancel message
    all = redis.hgetall(message.from_user.username)
    print(all)
    bot.send_message(message.chat.id, str(all))

# Start the bot
# bot.polling()
bot.infinity_polling()
