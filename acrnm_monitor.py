import requests
from bs4 import BeautifulSoup
from utils.utils import send_email

url = 'https://acrnm.com/'
filename = 'source/links.txt'

# Get the current list of links
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
links = [a['href'] for a in soup.find_all('a') if a.has_attr('href')]

try:
    # Read the previous list of links from file
    with open(filename, 'r') as f:
        previous_links = f.read().splitlines()
except FileNotFoundError:
    previous_links = []

# Compare the current and previous lists of links
new_links = set(links) - set(previous_links)
if new_links:
    print('New links found:')
    for link in new_links:
        print(link)
        previous_links.append(link)

    with open(filename, 'w') as f:
        for link in links:
            f.write(link + '\n')

    subject = "New links found on ACRNM website"
    body = "\n".join(new_links)
    send_email(subject, body)
else:
    print('No new links found.')
