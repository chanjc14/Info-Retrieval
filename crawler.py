from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import signal
import json

def exit_handler(signum, frame): # Handle CTRL-C exit
    res = input("Do you really want to exit? y/n ")
    if res == 'y':
        filename = "crawled_websites.json"
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(dictionary, f)
        exit(1)

signal.signal(signal.SIGINT, exit_handler)
url = 'https://www.wsu.edu/'
print(f"Default website to crawl = {url}")
while True:
    try:
        pages_to_crawl = int(input("Input number of sites to crawl: "))
        assert(pages_to_crawl > 0)
        break
    except: print("Please enter a positive integer!")
new = deque([url]) # Data structure used to keep track of sites to process
processed, local, foreign, dont_crawl = (set() for i in range(4)) # Used to track various sites
count = 0 # Iterator for tracking how many sites to crawl
dictionary = {} # Dict used to dynamically add urls and content
filename = "crawled_websites.json"
print("Begin crawling from", url)
while len(new): # While there are still sites, keep crawling
    if count == pages_to_crawl: # Number of sites to crawl
        break
    url = new.popleft() # Move url from new to url
    output_url = url # Use to save url in dictionary
    processed.add(url) # Add url to processed list
    print("Processing %s" % url) # Print out indicating what is currently going on
    try: response = requests.get(url)
    except requests.exceptions.RequestException as e: print("Website error")
    # Parse url in parts
    parts = urlsplit(url) # Split url into various parts
    base = "{0.netloc}".format(parts) # Get the base of the url
    strip_base = base.replace("www.", "") # Remove the www. from url
    base_url = "{0.scheme}://{0.netloc}".format(parts) # Get the base url
    path = url[:url.rfind('/')+1] if '/' in parts.path else url
    soup = BeautifulSoup(response.text, "lxml") # Used to easily grab relevant text from html
    content = soup.get_text(" ", strip=True) # Get the text from the soup
    url = url.replace('/','').replace(':','') # Strip off unnecessary stuff
    # Save each crawled site in the dictionary as url:body
    dictionary[output_url] = content
    # Get all links on page
    for link in soup.find_all('a'):
        anchor = link.attrs["href"] if "href" in link.attrs else ''
        if anchor.startswith('mailto:'):
            dont_crawl.add(anchor)
        elif anchor.endswith(".jpg" or ".png"):
            dont_crawl.add(anchor)
        elif anchor.startswith('/'): # Add base url and anchor
            local_link = base_url + anchor
            local.add(local_link)
        elif strip_base in anchor: # base of url in anchor
            local.add(anchor)
        elif not anchor.startswith('http'): # Link doesn't start with http
            local_link = path + anchor
            local.add(local_link)
        else: # Not in local domain, add to foreign list
            foreign.add(anchor)
        for i in local: # Go through links in local
            if not i in new and not i in processed: # If not in new or processed, add to new list
                new.append(i)
    count += 1 # Increase count for site counter

# Write dictionary out to JSON file after crawling all the sites
with open(filename, 'w', encoding="utf-8") as f:
    json.dump(dictionary, f)
    
print(f"{pages_to_crawl} pages crawled. Crawl complete!")
