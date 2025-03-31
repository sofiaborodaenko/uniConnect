import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from typing import Optional
import json
import ast
import event


def add_event(name: str, desc: str, location: Optional[str], sorting_info: tuple[int, str, str], posted_time: int, image: Optional[str]) -> None:
    scraped_events.append({
        "name": name,
        "desc": desc,
        "location": location,
        "sorting_info": sorting_info,
        "posted_time": posted_time,
        "image": image
    })


def call_llm_models(url: str, source: str, college_name: str) -> str:
    """
    Calls multiple LLMs in order: Gemini -> DeepSeek -> Qwen -> Dolphin
    Returns the first successful response.
    """
    prompts = f'''
You are given the full HTML source of a web page from the {college_name} college event page.

Extract a **single event** from this page (if available), and output the following fields in exactly this format:

name: str  
desc: str  
location: str or None  
sorting_info: tuple[int, str, str]  # (UNIX timestamp, category, "{college_name}")  
post_time: int  
image: str or None

Important Rules:
- The `sorting_info[1]` is the event category (e.g. 'Free Food', 'Social', 'Sports', 'Academic', 'Career', 'Financial Help', 'Mental Health', 'Health', 'Outdoor Adventure', 'Uncategorized'). If you can't find an exact match, analyze the event content and **choose the closest category**. If it is truly unclear or ambiguous, label it as 'Uncategorized'.
- The `sorting_info[2]` must always be "{college_name}"
- If any field is missing, use `None`, and `0` for integers
- `image` should be a full image URL (absolute path)
- Do NOT include any extra notes, formatting, explanations, or markdown — just the raw fields.
- Only extract **one** event, and output in plain text (no JSON, no code block)

HTML Source:
{source}
'''
    try:
        print("Trying Deepseek ...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer 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"},
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [{"role": "user", "content": prompts}]
            })
        )
        return json.loads(response.text)["choices"][0]["message"]["content"]
    except:
        print("DeepSeek failed, trying Gemini...")

    try:
        print("Trying Gemini Flash...")
        response = requests.post(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyBGKtjloXqO3-9a8Barol8ORxkqO8h0jNY",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "contents": [{"parts": [{"text": prompts}]}]
            })
        )
        return json.loads(response.text)["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Gemini failed, trying Qwen...")

    try:
        print("Trying Qwen...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer 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"},
            data=json.dumps({
                "model": "qwen/qwen-qwq-32b:free",
                "messages": [{"role": "user", "content": prompts}]
            })
        )
        return json.loads(response.text)["choices"][0]["message"]["content"]
    except:
        print("Qwen failed, trying Dolphin...")

    try:
        print("Trying Dolphin...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": "Bearer dolphin-3.0-mistral-24b"},
            data=json.dumps({
                "model": "dolphin/dolphin-3.0-mistral-24b:free",
                "messages": [{"role": "user", "content": prompts}]
            })
        )
        return json.loads(response.text)["choices"][0]["message"]["content"]
    except:
        print("All LLMs failed.")
        return ""


def extract_data(url: str, source: str, college_name: str) -> dict:
    """
    Takes the link of the event, and return a dictionary with extracted information
    """
    message_content = call_llm_models(url, source, college_name)
    content_dict = {}
    content_array = message_content.split("\n")

    for item in content_array:
        if ":" in item:
            key, value = item.split(': ', 1)
            value = value.strip()
            if key == "sorting_info":
                try:
                    sorting_vals = ast.literal_eval(value)
                    content_dict[key] = sorting_vals if len(sorting_vals) == 3 else (0, 'Uncategorized', college_name)
                except:
                    content_dict[key] = (0, 'Uncategorized', college_name)
            elif 'None' in value or value == "":
                content_dict[key] = None
            elif key == "post_time":
                content_dict[key] = int(value.replace(',', ''))
            elif key == "image":
                content_dict[key] = value if "http" in value else url + "/" + value
            else:
                content_dict[key] = value

    return content_dict


def scrape(url: str, add_url: str, college_name: str) -> None:
    """
    Get main domain of an event page, extract the links of each event and retrieve their information
    """
    driver.get(url + add_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    events = soup.find_all(['div', 'li', 'article', 'a'], class_=[
        'o-listing__list-item', 'm-listing-item--3cols', 'e-loop-item',
        'archive-events', 'news-events-tile',
        'tribe-events-calendar-month__day--current', 'events-link'
    ])
    event_links = []

    for item in events:
        if 'href' in item.attrs:
            event_links.append(item['href'] if "http" in item['href'] else url + item['href'])
        else:
            a_tag = item.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                event_links.append(href if "http" in href else url + href)

    for link in event_links:
        driver.get(link)
        time.sleep(3)
        try:
            output_dict = extract_data(url, driver.page_source, college_name)
            event.add_event_dict(
                scraped_events,
                output_dict.get("name"),
                output_dict.get("desc"),
                output_dict.get("location"),
                output_dict.get("sorting_info"),
                output_dict.get("post_time"),
                output_dict.get("image")
            )
        except:
            print("Failed to extract event from:", link)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    scraped_events = []
    scrape("https://www.uc.utoronto.ca", "/about-uc-connect-us-events", "University College")
    scrape("https://wdw.utoronto.ca", "/events", "Woodsworth College")
    scrape("https://innis.utoronto.ca", "/happening-at-innis", "Innis College")
    scrape("https://www.newcollege.utoronto.ca", "/events", "New College")
    scrape("https://www.vicu.utoronto.ca", "/whats-happening", "Victoria College")
    scrape("https://www.trinity.utoronto.ca", "/discover/calendar", "Trinity College")

    with open('static/u_of_t_events.json', 'w', encoding='utf-8') as file:
        json.dump(scraped_events, file, indent=4, ensure_ascii=False)

    with open('static/u_of_t_events_original.json', 'w', encoding='utf-8') as file:
        json.dump(scraped_events, file, indent=4, ensure_ascii=False)

    driver.quit()
