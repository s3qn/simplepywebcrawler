import requests
from lxml import html
from urllib.parse import urlparse
import argparse
from bs4 import BeautifulSoup
from bs4 import Comment
print("""       
-----------------------------------------
Super Duper Simple Web Crawler v0.1 (BETA)
Author: Sean (bustdownrarri)
-----------------------------------------
""")

# Handling arguments
parser = argparse.ArgumentParser(
    description="Simple crawler to scrape items from a website, made to work on my python skills.",
    usage="%(prog)s [options] -u url\ncrawler.py --help for help.\nFor now it will scrape http://inlanefreight.com if no url is specified"
)
parser.add_argument('-u', '--url', type=str, help='URL to start crawling on.')
parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity.')
parser.add_argument('-s','--scrape', choices=['emails', 'comments'], required=False, help='Scrape an element of choice')
args = parser.parse_args()


if args.url:
    start_url = args.url
else:
    start_url = 'http://inlanefreight.com'
if isinstance(args.scrape, str):
    print("Modes enabled: {}".format(args.scrape))

print("Attempting to connect to site...")

# Grabbing Domain name
domain_name = urlparse(start_url).netloc
print(f"Domain: {domain_name}")


# Lists
processed_links = []
urls_to_visit = [start_url]
found_links = []

# Optional sets
if args.scrape == 'emails': email_set = set()
if args.scrape == 'comments': comments_set = set()

# Function for Testing connectivity, exiting if not connecting
def connect_to_url(url):
    try:
        page = requests.get(url, timeout=5)
        if args.verbose: print(f"Connected to: {page.url}")
        found_links.append(url)
        # if page.url not in processed_links and urls_to_visit:
        #     urls_to_visit.append(page.url)
        #
        return page

    except:
        if args.verbose: print("Error, no connection")
        return None

# Function to grab links from a page
def grab_links_from_page(grabbed_page, domain):
    html_page = html.fromstring(grabbed_page.content)
    raw_links = html_page.xpath('//@href')
    page_links = []
    for link in raw_links:
        if domain in link and link not in page_links and link not in processed_links:

            if link not in found_links:
                test_link = connect_to_url(link)
                try:
                    if test_link.status_code == 200:
                        page_links.append(link)
                except:
                    continue
            else:
                page_links.append(link)

        else:
            continue
    return page_links


def scrape_comments(page_soup, url):


    if args.verbose: print(f"Scraping comments for {url}")
    comments = page_soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if args.verbose: print(f"Found: {comment}")
        try: comments_set.add(comment)
        except: continue

def scrape_emails(page_soup, url):
    if args.verbose: print(f"Scraping emails for {url}")
    for parsed_link in page_soup.find_all('a',href=True):
        href = parsed_link['href']
        if href.startswith('mailto:'):
            email = href[len('mailto:'):]
            if args.verbose: print(f"Found: {email}")
            try: email_set.add(email)
            except: continue


# Test connectivity
while urls_to_visit:
    current_url = urls_to_visit[0]
    if current_url in processed_links:
        continue
    page = connect_to_url(current_url)
    if args.verbose: print(f" Scanning link: {current_url}")
    if isinstance(args.scrape, str): parsed_page = BeautifulSoup(page.text, 'html.parser')

    # Scrape comments
    if args.scrape == 'comments': scrape_comments(parsed_page, current_url)

    # Scrape emails
    if args.scrape == 'emails': scrape_emails(parsed_page, current_url)

    for link in grab_links_from_page(page, domain_name):
        if args.verbose: print(f"Found link in {current_url}: {link}")
        if link not in processed_links and link not in urls_to_visit:

            urls_to_visit.append(link)
    processed_links.append(current_url)
    urls_to_visit.remove(current_url)




# Print Results
print('--------------Output Links--------------')
print(f"Links Extracted: {len(processed_links)}")
print(*processed_links,sep='\n')

if args.scrape == 'comments': print('--------------Output Comments--------------')
if args.scrape == 'comments': print(comments_set)

if args.scrape == 'emails': print('--------------Output Emails--------------')
if args.scrape == 'emails': print(email_set)
