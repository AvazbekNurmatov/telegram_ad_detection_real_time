######
##FIRST STEP IS SETTING UP DOCKER and creating minimcal telegram bot for basic functionality

#Starting the process
./start_bot.sh

#stopping the process
./stop_bot.sh

Manually cleaning up
pkill -f main.py
rm -f telegram_bot.pid telegram_bot_session.session-journal
