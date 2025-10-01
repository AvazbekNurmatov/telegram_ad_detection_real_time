from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
import os
import sys 
import subprocess
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest, ReportSpamRequest
import pandas as pd
import asyncio
import atexit
import sqlite3
import signal
from naive_bayes_classifier import NaiveBayesClassifier

# Replace with your actual API ID and API Hash from my.telegram.org
api_id = 23681808
api_hash = 'eef4b030720087226f0f144e59000eef'

# CHANGED: Use a descriptive session name instead of 'anon'
# This will create 'telegram_bot_session.session' file
session_name = 'telegram_bot_session'

# Add connection_retries to handle database locks gracefully
client = TelegramClient(
    session_name, 
    api_id, 
    api_hash,
    connection_retries=5,
    retry_delay=1
)

csv_name = "telegram_contacts.csv"
pid_file = "telegram_bot.pid"

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_event.set()

class SingleInstance:
    """Ensure only one instance of the script runs at a time"""
    
    def __init__(self, pid_file):
        self.pid_file = pid_file
        self.acquired = False
    
    def __enter__(self):
        # Check if PID file exists
        if os.path.exists(self.pid_file):
            with open(self.pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if that process is still running
            if self._is_process_running(old_pid):
                print(f"Another instance is already running (PID: {old_pid})")
                print("Please stop the other instance first, or wait for it to finish.")
                sys.exit(1)
            else:
                print(f"Removing stale PID file (process {old_pid} no longer exists)")
                os.remove(self.pid_file)
        
        # Write current PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.acquired = True
        # Register cleanup on exit
        atexit.register(self.cleanup)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Remove PID file on exit"""
        if self.acquired and os.path.exists(self.pid_file):
            try:
                os.remove(self.pid_file)
            except Exception:
                pass
    
    @staticmethod
    def _is_process_running(pid):
        """Check if a process with given PID is running"""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
            return True
        except OSError:
            return False

def remove_session_lock():
    """Remove session lock file if it exists"""
    lock_file = f"{session_name}.session-journal"
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print(f"Removed stale lock file: {lock_file}")
        except Exception as e:
            print(f"Could not remove lock file: {e}")

def fix_session_permissions():
    """Ensure session file has correct permissions"""
    session_file = f"{session_name}.session"
    if os.path.exists(session_file):
        try:
            # Set to rw-rw-r-- (664)
            os.chmod(session_file, 0o664)
            print(f"Fixed permissions for {session_file}")
        except Exception as e:
            print(f"Could not fix permissions: {e}")

def cleanup_old_sessions():
    """Clean up old anon.session files that might cause conflicts"""
    old_sessions = ['anon.session', 'anon.session-journal']
    for old_file in old_sessions:
        if os.path.exists(old_file):
            try:
                os.remove(old_file)
                print(f"Removed old session file: {old_file}")
            except Exception as e:
                print(f"Could not remove {old_file}: {e}")


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
        clf = NaiveBayesClassifier() 
        if clf.predict(chat_text) == 1:
            print(f"Blocking user {user_id} for sending ad content")
            try:
                # Get the sender entity from the event
                sender = await event.get_sender()
                
                # Step 1: Delete the spam message
                await event.delete()
                print(f"✓ Deleted spam message from user {user_id}")
                
                # Step 2: Delete entire chat history with this user (makes them invisible)
                await client(DeleteHistoryRequest(
                    peer=sender,
                    max_id=0,  # Delete all messages
                    just_clear=False,  # Actually delete, don't just clear
                    revoke=True  # Delete for both sides if possible
                ))
                print(f"✓ Deleted entire chat history with user {user_id}")
                
                # Step 3: Report as spam to Telegram
                await client(ReportSpamRequest(peer=sender))
                print(f"✓ Reported user {user_id} as spam to Telegram")
                
                # Step 4: Block the user
                await client(BlockRequest(sender))
                print(f"✓ Blocked user {user_id}")
                
                print(f"✅ Successfully removed all traces of spammer {user_id}")
                
            except Exception as e:
                print(f"❌ Error handling spam from user {user_id}: {e}")

async def main():
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # This will only ask for phone + OTP on first run
            # After that, it reads from telegram_bot_session.session
            await client.start()
            print("Client started! Listening for messages from users only...")
            print("Press Ctrl+C to stop gracefully")
            
            # Run until disconnected or shutdown signal
            disconnect_task = asyncio.create_task(client.run_until_disconnected())
            shutdown_task = asyncio.create_task(shutdown_event.wait())
            
            # Wait for either disconnect or shutdown signal
            done, pending = await asyncio.wait(
                [disconnect_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            break  # Exit loop if successful
            
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                if attempt < max_retries - 1:
                    print(f"Database locked, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    # Try to remove lock file
                    remove_session_lock()
                else:
                    print("Failed to connect after multiple retries.")
                    print("Please ensure no other instances are running:")
                    print("  pkill -f main.py")
                    print("  rm -f telegram_bot_session.session-journal")
                    raise
            else:
                raise
                
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            break
            
        finally:
            # Ensure proper disconnection
            try:
                if client.is_connected():
                    print("Disconnecting client...")
                    await client.disconnect()
                    print("Client disconnected.")
            except Exception as e:
                print(f"Error during disconnect: {e}")

# Run the main function
if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill command
    
    # Use SingleInstance context manager to ensure only one instance runs
    with SingleInstance(pid_file):
        # Clean up old session files
        cleanup_old_sessions()
        
        # Fix session file permissions
        fix_session_permissions()
        
        # Remove any stale lock files
        remove_session_lock()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nShutdown complete.")
        finally:
            print("Cleanup finished.")
