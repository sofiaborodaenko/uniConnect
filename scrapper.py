import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from typing import Optional
import requests
import json
import ast

def add_event(name: str, desc: str, location: Optional[str], sorting_info: tuple[int, str, str], posted_time: int, image: Optional[str]) -> None:
    scraped_events.append({
        "name": name,
        "desc": desc,
        "location": location,
        "sorting_info": sorting_info,
        "posted_time": posted_time,
        "image": image
    })

def extract_data(url: str, source: str, college_name: str) -> dict:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {
                    "role": "user",
                    "content": "Use this HTML Page" + source
                               + "And extract these information in this format of this event, where sorting_info is time in UNIX, category, the string \'" + college_name + "\' and image is the url of one image"
                               + "name: str, desc: str, location: str, sorting_info: tuple[int, str, str], post_time: int, image: str"
                               + "Do not add any comments or notes, ONLY THE EXTRACTED DATA, if there is nothing, leave it as None, or 0 for integers"
                               + "Leave it in PLAIN TEXT format, straight up, no code block formatting"

                }
            ]
        })
    )

    response_data = json.loads(response.text)
    message_content = response_data['choices'][0]['message']['content']

    content_dict = {}
    content_array = message_content.split("\n")

    for item in content_array:
        if ":" in item:
            key, value = item.split(': ', 1)
            value = value.strip()

            if key == "sorting_info":
                sorting_vals = ast.literal_eval(value)
                if not sorting_vals or len(sorting_vals) != 3:
                    content_dict[key] = (0, 'Uncategorized', college_name)
                content_dict[key] = sorting_vals
            elif 'None' in value or value == "":
                content_dict[key] = None
            elif key == "post_time":
                content_dict[key] = int(value.replace(',', ''))
            elif key == "image":
                if "http" in value:
                    content_dict[key] = value
                else:
                    content_dict[key] = url + "/" + value
            else:
                content_dict[key] = value

    return content_dict

def scrape(url: str, add_url: str, college_name: str) -> None:
    driver.get(url + add_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    events = soup.find_all(['div', 'li', 'article', 'a'], class_=['o-listing__list-item', 'm-listing-item--3cols', 'e-loop-item', 'archive-events', 'news-events-tile', 'tribe-events-calendar-month__day--current', 'events-link'])
    event_links = []


    for event in events:
        # For trinity
        if event['href']:
            if "http" in event['href']:
                event_links.append(event['href'])
            else:
                event_links.append(url + event['href'])

        # For every college except for trinity
        extension = event.find('a', href=True)
        if extension:

            if "http" in extension['href']:
                event_links.append(extension['href'])
            else:
                event_links.append(url + extension['href'])


    print(event_links)
    for link in event_links:
        driver.get(link)
        time.sleep(3)
        try:
            output_dict = extract_data(url, driver.page_source, college_name)
            print(output_dict)

            add_event(
                output_dict["name"],
                output_dict["desc"],
                output_dict["location"],
                output_dict["sorting_info"],
                output_dict["post_time"],
                output_dict["image"]
            )
        except KeyError:
            print("Event sucks or Deepseek messed up")

    return


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
    driver = webdriver.Chrome(options=chrome_options)

    scraped_events = []
    # scrape("https://www.uc.utoronto.ca", "/about-uc-connect-us-events", "University College")
    # scrape("https://wdw.utoronto.ca", "/events", "Woodsworth College")
    # scrape("https://innis.utoronto.ca", "/happening-at-innis", "Innis College")
    # scrape("https://www.newcollege.utoronto.ca", "/events", "New College")
    # scrape("https://www.vicu.utoronto.ca", "/whats-happening", "Victoria College")
    scrape("https://www.trinity.utoronto.ca", "/discover/calendar", "Trinity College")
    print(scraped_events)

    with open('static/u_of_t_events.json', 'w', encoding='utf-8') as file:
        json.dump(scraped_events, file, indent=4, ensure_ascii=False)

    driver.quit()