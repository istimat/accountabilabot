import time

def remind_user(bot, redis):
    
    #how much to wait after update is late before notifying user:
    delay_factor = 1.5
    reminder_sent = False
    
    while True:
        
        users = redis.keys()
        for user in users:
            print(user)
            try:
                last_update = int(redis.hget(user, 'last_update_time'))
                update_frequency = redis.hget(user, 'freq')
                period = freq_to_period(update_frequency)
                chat_id = redis.hget(user, 'chat_id')
                print(f"chat id: {chat_id}")
                
                now = int(round(time.time()))
                
                print(last_update)
                
                if now-last_update > period * delay_factor and not reminder_sent:
                    print("sending message")
                    bot.send_message(chat_id, "HEY!")
                    reminder_sent = True
            except:
                print("user has no updates")
        
        time.sleep(10)    
        
def freq_to_period(update_frequency):
    if update_frequency == 'Minutely':
        return 60
    if update_frequency == 'Daily':
        return 3600*24
    if update_frequency == 'Weekly':
        return 3600*24*7
    else:
        return None