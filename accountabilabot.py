import telebot
import redis


bot = telebot.TeleBot('5988436185:AAEoKsx1czluS7Ih6VM7vn82xhjqbr0SYcg')

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)


@bot.message_handler(commands=['start'])
def start(message):
    
    redis.hset(message.from_user.username, 'goal', '')
    redis.hset(message.from_user.username, 'points', 0)
    
    
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row("Set a goal")
    markup.row("Update progress")
    markup.row("Scoreboard")
    
    bot.send_message(message.chat.id, 'Welcome to the accountability bot!\n\n'
                     'Please choose an option:',
                     reply_markup=markup)
    # Move to the GOAL state
    bot.register_next_step_handler(message, handle_menu)

def handle_menu(message):
    
    if message.text == "Set a goal":
        ask_for_goal(message)
        print("setting goal")
    if message.text == "Update progress":
        update_progress(message)
        print("updating progress")
    if message.text == "Leaderboard":
        leaderboard()

def ask_for_goal(message):
    #check if goal already defined or not
    bot.send_message(message.chat.id, "Alright, what is your next goal?")
    bot.register_next_step_handler(message, set_goal)
    
# Define the set_goal function
def set_goal(message):
    # Save the goal in the user's data
    # redis.set('mykey', 'Hello from Python!')
    redis.hset(message.from_user.username, 'goal', message.text)
    
    # Add points for setting a goal
    redis.hincrby(message.from_user.username, 'points', 10)

    # Send a confirmation message
    bot.send_message(message.chat.id, f'Your goal "{message.text}" has been set. '
                     'Please update your progress regularly.')

    # Move to the UPDATE state
    bot.register_next_step_handler(message, update_progress)

# Define the update_progress function
def update_progress(message):
 # Save the progress update in Redis
    redis.hset(message.from_user.username, 'progress', message.text)

    # Add or subtract points based on progress
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
@bot.message_handler(commands=['leaderboard'])
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
@bot.message_handler(commands=['cancel'])
def cancel(message):
    # Send a cancel message
    bot.send_message(message.chat.id, 'Canceled.')

# Start the bot
bot.polling()
