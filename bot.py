from playwright.sync_api import sync_playwright
import requests
import time
import os

# Məlumatlar artıq GitHub Secrets-dən gələcək
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
