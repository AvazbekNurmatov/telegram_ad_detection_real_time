from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.types import InputPeerEmpty
import csv
import json

api_id = '23681808'
api_hash = 'eef4b030720087226f0f144e59000eef'

client = TelegramClient('session_name', api_id, api_hash)

try:
    client.start()
    print("Connected to Telegram successfully!")
    
    # Method 1: Get contacts using GetContactsRequest
    contacts = client(GetContactsRequest(hash=0))
    
    # Prepare contact list
    contact_list = []
    
    for user in contacts.users:
        contact_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username or '',
            'phone': user.phone or '',
            'is_contact': user.contact,
            'is_mutual_contact': user.mutual_contact
        }
        contact_list.append(contact_info)
    
    # Print contacts to console
    print(f"\nFound {len(contact_list)} contacts:")
    print("-" * 80)
    for contact in contact_list:
        full_name = f"{contact['first_name']} {contact['last_name']}".strip()
        print(f"ID: {contact['id']}")
        print(f"Name: {full_name}")
        print(f"Username: @{contact['username']}" if contact['username'] else "Username: N/A")
        print(f"Phone: {contact['phone']}" if contact['phone'] else "Phone: N/A")
        print("-" * 40)
    
    # Save to CSV file
    with open('telegram_contacts.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'first_name', 'last_name', 'username', 'phone', 'is_contact', 'is_mutual_contact']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for contact in contact_list:
            writer.writerow(contact)
    
    # Save to JSON file
    with open('telegram_contacts.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(contact_list, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"\nContacts saved to:")
    print(f"- telegram_contacts.csv ({len(contact_list)} contacts)")
    print(f"- telegram_contacts.json ({len(contact_list)} contacts)")
    
except Exception as e:
    print(f"Error occurred: {e}")
    print("Make sure you have authorized the application with your phone number.")

finally:
    client.disconnect()
    print("Disconnected from Telegram.")
