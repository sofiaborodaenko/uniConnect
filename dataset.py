import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

# List of websites to scrape
websites = {
    # "UTSU": "https://www.utsu.ca/sc-programming/",
    # "Folio_Activities": "https://folio.utoronto.ca/students/activities?endorsementIds=4623183&page=1&studentSiteId=1",
    # "Folio_Events": "https://folio.utoronto.ca/students/events",
    # "ASSU": "https://assu.ca/wp/get-involved/",
    "Vic": "https://www.vusac.ca/events",
    "UC": "https://www.uc.utoronto.ca/about-uc-connect-us-events",
    # "Trinity": "https://www.trinity.utoronto.ca/discover/calendar/",
    #"Innis": "https://innis.utoronto.ca/happening-at-innis/",
    "Woodsworth": "https://www.mywcsa.com/current-events-instagram"
}

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
driver = webdriver.Chrome(options=chrome_options)

# Dictionary to store all events
all_events = []

# Function to scrape list-based events
def scrape_list_events(soup, source):
    events = soup.find_all(['div', 'li', 'article'], class_=['event', 'event-item', 'post', 'calendar-event'])
    scraped_events = []
    for event in events:
        title_tag = event.find(['h2', 'h3', 'p', 'span'], class_=['title', 'event-title'])
        title = title_tag.text.strip() if title_tag else "No title"

        date_tag = event.find(['time', 'span', 'p'], class_=['date', 'event-date'])
        date = date_tag.text.strip() if date_tag else "No date"

        desc_tag = event.find('p', class_=['description', 'event-details', 'summary'])
        description = desc_tag.text.strip() if desc_tag else "No description"

        scraped_events.append({
            "source": source,
            "title": title,
            "date": date,
            "description": description
        })
    return scraped_events

# Function to scrape calendar-based events
def scrape_calendar_events(soup, source):
    # Look for a calendar table or grid
    calendar = soup.find(['table', 'div'], class_=['calendar', 'event-calendar'])
    if not calendar:
        return []

    scraped_events = []
    # Look for rows or day cells
    days = calendar.find_all(['tr', 'div'], class_=['day', 'calendar-day', 'event-day'])
    for day in days:
        date_tag = day.find(['th', 'td', 'span'], class_=['date', 'day-date'])
        date = date_tag.text.strip() if date_tag else "No date"

        event_tags = day.find_all(['td', 'div'], class_=['event', 'calendar-event'])
        for event in event_tags:
            title_tag = event.find(['h3', 'h4', 'span'], class_=['title', 'event-title'])
            title = title_tag.text.strip() if title_tag else "No title"

            desc_tag = event.find(['p', 'div'], class_=['description', 'event-details'])
            description = desc_tag.text.strip() if desc_tag else "No description"

            scraped_events.append({
                "source": source,
                "title": title,
                "date": date,
                "description": description
            })
    return scraped_events

# Function to scrape image-based events (e.g., Instagram embeds)
def scrape_image_events(soup, source):
    # Look for Instagram embeds or image captions
    images = soup.find_all(['div', 'iframe', 'img'], class_=['instagram-post', 'embed', 'event-image'])
    scraped_events = []
    for img in images:
        # Check if it's an Instagram embed
        if img.name == 'iframe' and 'instagram' in img.get('src', ''):
            title = "Instagram Event Post"
            desc_tag = img.find_next(['p', 'div'], class_=['caption', 'description'])
            description = desc_tag.text.strip() if desc_tag else "No description"
        else:
            # Extract from image alt text or caption
            title = img.get('alt', 'Image Event')
            desc_tag = img.find_next(['p', 'div'], class_=['caption', 'description'])
            description = desc_tag.text.strip() if desc_tag else "No description"

        # Date might be in a nearby element
        date_tag = img.find_previous(['time', 'span', 'p'], class_=['date', 'event-date'])
        date = date_tag.text.strip() if date_tag else "No date"

        scraped_events.append({
            "source": source,
            "title": title,
            "date": date,
            "description": description
        })
    return scraped_events

# Main scraping loop
for source, url in websites.items():
    print(f"Scraping {source} from {url}...")

    # Use Selenium for dynamic content (Folio, Woodsworth, and potentially others)
    if source in ["Folio_Activities", "Folio_Events", "Woodsworth"]:
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    else:
        # Use requests for static pages
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {source}. Status code: {response.status_code}")
            continue
        soup = BeautifulSoup(response.content, 'html.parser')

    # Determine the format and scrape accordingly
    if source == "Trinity":
        # Calendar format
        events = scrape_calendar_events(soup, source)
    elif source == "Woodsworth":
        # Image/Instagram format
        events = scrape_image_events(soup, source)
    else:
        # List format (default for UTSU, Folio, ASSU, Vic, UC, Innis)
        events = scrape_list_events(soup, source)

    all_events.extend(events)

# Close the Selenium driver
driver.quit()

# Save all events to a JSON file
with open('u_of_t_events.json', 'w', encoding='utf-8') as file:
    json.dump(all_events, file, indent=4, ensure_ascii=False)

# Print the scraped events for verification
print("\nAll Scraped Events:")
for i, event in enumerate(all_events, 1):
    print(f"\nEvent {i}:")
    print(f"Source: {event['source']}")
    print(f"Title: {event['title']}")
    print(f"Date: {event['date']}")
    print(f"Description: {event['description']}")
