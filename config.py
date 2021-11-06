import os

from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

# For Local Deploy
if os.path.exists(".env"):
    load_dotenv(".env")

# Necessary Vars
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
COMMAND_PREFIXES = list(os.getenv("COMMAND_PREFIXES", "T O M I / ! ?").split())
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS").split()))

# Cellmusic
bot = Client(SESSION, API_ID, API_HASH, plugins=dict(root="MusicAndVideo"))
call_py = PyTgCalls(bot)
