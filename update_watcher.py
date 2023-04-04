import time

def remind_user(bot, redis):
    
    while True:
        
        users = redis.keys()
        for user in users:
            print(user)
            try:
                last_update = int(redis.hget(user, 'last_update_time'))
                chat_id = redis.hget(user, 'chat_id')
                print(f"chat id: {chat_id}")
                
                now = int(round(time.time()))
                
                print(last_update)
                
                if now-last_update > 15:
                    print("sending message")
                    bot.send_message(chat_id, "HEY!")
            except:
                print("user has no updates")
        
        time.sleep(10)    