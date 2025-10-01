from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
import os
import sys 
from ad_classifier import AdClassifier
import subprocess
from telethon.tl.functions.contacts import BlockRequest
import pandas as pd
import asyncio

# Replace with your actual API ID and API Hash from my.telegram.org
api_id = 23681808
api_hash = 'eef4b030720087226f0f144e59000eef'

client = TelegramClient('anon', api_id, api_hash)
csv_name = "telegram_contacts.csv"

# Filter to only listen to private messages (user DMs)
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def my_event_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    chat_text = event.raw_text
    csv_generator = "create_list_contacts.py"
    
    # Your code to handle the new message event
    print(f"New message received from user {user_id}: {event.raw_text}")
    
    if not os.path.exists(csv_name):
        subprocess.run([sys.executable, csv_generator])
        df = pd.read_csv(csv_name)
    else:
        df = pd.read_csv(csv_name)
    
    # Check if user_id is in the dataframe
    if 'id' in df.columns and (user_id == df['id']).any():
        print("Your contact is calling you")
        return
    else: 
        clf = AdClassifier()
        if clf.predict(chat_text) == 1:
            print(f"Blocking user {user_id} for sending ad content")
            await client(BlockRequest(event.user_id))

async def main():
    await client.start()
    print("Client started! Listening for messages from users only...")
    await client.run_until_disconnected()

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
