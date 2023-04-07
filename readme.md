# Accountabilabot

A telegram bot that helps you be consistent in progressing towards your goals.

## Dependencies

- redis
- TelegramBotAPI

You can:
`pip install redis`

`pip install pyTelegrambotAPI`

Or just run:
`pip install -r requirements.txt`
 

## Usage

First, the redis server needs to be started with this command:

`redis-server`

By default, the server creates a port at 127.0.0.1:6379.
You can now try to connect to the server in the terminal with:

`redis-cli 127.0.0.1:6379`

Now that the redis database server is running, the accountabilabot can be started using:

`python3 accountablilabot.py`

## Bot usage

To reach the bot, open Telegram and search for the bot called AM_accountabilabot
Once in a chat with the bot you can type:

`/start`
For an interactive inline keyboard

`/reset`
To erase your goal and score

`/dump`
To get a dump of all the database values stored for the current username

