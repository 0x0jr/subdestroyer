#!/usr/bin/python3
# author: mxnty
# description: Subdirectory brute-forcing tool
# usage: python3 subdestroyer.py <target_url> <wordlist>

import sys
import requests
import random
from queue import Queue
from threading import Thread, Lock, Event
import colorama
from colorama import Fore, Style
from datetime import datetime

banner = """
               __        __          __                            
   _______  __/ /_  ____/ /__  _____/ /__________  __  _____  _____
  / ___/ / / / __ \/ __  / _ \/ ___/ __/ ___/ __ \/ / / / _ \/ ___/
 (__  ) /_/ / /_/ / /_/ /  __(__  ) /_/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/\__,_/\___/____/\__/_/   \____/\__, /\___/_/     
                                                /____/             
by mxnty
"""

print(f"{Fore.RED}{banner}")

currentTime = datetime.now()

colorama.init()

# Command-line argument parsing
if len(sys.argv) != 3:
    print(f"{Fore.RED}Usage: python3 {sys.argv[0]} <target_url> <wordlist>")
    sys.exit(1)

target_url = sys.argv[1].rstrip('/')  # Ensure no trailing slash
wordlist = sys.argv[2]

def count_lines(filename):
    try:
        with open(filename, 'r') as file:
            return sum(1 for line in file)
    except FileNotFoundError:
        print(f"{Fore.RED}[-] ERROR: Wordlist file not found!")
        sys.exit(1)

wordlistSize = count_lines(wordlist)

# User agent variables
randomUserAgent = input(f"{Fore.BLUE}Do you wanna use random user agents (yes/no): ").strip().lower()
defaultUserAgent = 'subdestroyer v1.0'
user_agents = []

if randomUserAgent == 'yes':
    userAgentPath = input(f'{Fore.BLUE}Enter the path to the wordlist of user agents: ')
    try:
        with open(userAgentPath, 'r') as useragents_file:
            for line in useragents_file:
                user_agents.append(line.strip())
    except FileNotFoundError:
        print(f"{Fore.RED}[-] ERROR: User agent wordlist file not found!")
        sys.exit(1)

# Load wordlist
subdirectories = Queue()

try:
    with open(wordlist, 'r') as file:
        for line in file:
            subdirectories.put(line.strip())
except FileNotFoundError:
    print(f"{Fore.RED}[-] ERROR: Wordlist file not found!")
    sys.exit(1)

# Define worker function
lock = Lock()
stop_event = Event()

def test_subdirectory():
    while not subdirectories.empty() and not stop_event.is_set():
        subdirectory = subdirectories.get()
        url = f"{target_url}/{subdirectory}"
        
        if randomUserAgent == 'yes':
            headers = {"User-Agent": random.choice(user_agents)}
        else:
            headers = {"User-Agent": defaultUserAgent}

        try:
            response = requests.head(url, headers=headers)  # Use HEAD request to reduce bandwidth usage
            if response.status_code in [200, 301, 302, 403]:  # Common valid response codes
                with lock:
                    print(f"{Fore.GREEN}[+] INFO: Found subdirectory: {url} [Status code: {response.status_code}]")
        except requests.ConnectionError:
            pass
        finally:
            subdirectories.task_done()

# Multi-threading
num_threads = 100 # Change here to add threads
threads = []

print(f"""
{Fore.YELLOW}[+] STATUS:
Scan started at {currentTime}
Wordlist size: {wordlistSize}
Threads: {num_threads}
Random User-Agent: {randomUserAgent}
""")

try:
    for _ in range(num_threads):
        thread = Thread(target=test_subdirectory)
        thread.start()
        threads.append(thread)

    # Wait for the queues to be empty
    subdirectories.join()

except KeyboardInterrupt:
    print(f"{Fore.RED}[+] ERROR: Scan interrupted by user.")
    stop_event.set()
finally:
    for thread in threads:
        thread.join()

print(f"{Fore.YELLOW}[+] STATUS: Scan completed at {currentTime}")

colorama.deinit()
