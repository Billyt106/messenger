from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import instaloader
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import spacy
import pyperclip

# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Initialize Instaloader and Sentiment Intensity Analyzer
L = instaloader.Instaloader()

def load_session(L, username, password):
    try:
        L.load_session_from_file(username)
    except FileNotFoundError:
        L.login(username, password)
        L.save_session_to_file(username)

def login_to_instagram(page, username, password):
    page.goto('https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Flogin%2F&source=logged_out_half_sheet')
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")


def random_delay(min_seconds, max_seconds):
    """Generates a random delay to mimic human behavior."""
    time.sleep(random.uniform(min_seconds, max_seconds))
    
def fetch_user_posts(username):
    """Fetches posts data for a given username."""
    profile = instaloader.Profile.from_username(L.context, username)
    posts_data = []

    for post in profile.get_posts():
        post_info = {
            'caption': post.caption if post.caption else "",
            'likes': post.likes,
            'comments': post.comments,
            'type': 'reel' if post.is_video else 'image',
            'url': post.url
        }
        posts_data.append(post_info)

    return posts_data
def extract_entities_and_keywords(caption):
    """Extracts entities and keywords from a caption."""
    doc = nlp(caption)
    entities = set(ent.label_ for ent in doc.ents)
    keywords = set(token.lemma_.lower() for token in doc if token.pos_ in {'NOUN', 'PROPN', 'ADJ'})
    return entities, keywords

def analyze_user_profile(posts_data):
    """Analyzes user's profile for specific themes and popular posts."""
    most_popular_post = max(posts_data, key=lambda x: x['likes'] + x['comments']) if posts_data else None
    all_entities = set()
    all_keywords = set()

    for post in posts_data:
        entities, keywords = extract_entities_and_keywords(post['caption'])
        all_entities.update(entities)
        all_keywords.update(keywords)

    return most_popular_post, all_keywords, all_entities
def type_message(page, message):
    for char in message:
        page.keyboard.type(char)
        time.sleep(0.05)  # Delay between typing each character

    time.sleep(1)  # Short pause after typing the complete message
    page.keyboard.press('Enter')
def extract_entities_and_keywords(caption):
    """Extracts entities and keywords from a caption."""
    doc = nlp(caption)
    entities = set(ent.label_ for ent in doc.ents)
    keywords = set(token.lemma_.lower() for token in doc if token.pos_ in {'NOUN', 'PROPN', 'ADJ'})
    return entities, keywords

def analyze_user_profile(posts_data):
    """Analyzes user's profile for specific themes and popular posts."""
    most_popular_post = max(posts_data, key=lambda x: x['likes'] + x['comments']) if posts_data else None
    all_entities = set()
    all_keywords = set()

    for post in posts_data:
        entities, keywords = extract_entities_and_keywords(post['caption'])
        all_entities.update(entities)
        all_keywords.update(keywords)

    return most_popular_post, all_keywords, all_entities

def generate_personalized_message(most_popular_post, all_keywords, all_entities):
    # Base message
    message = "Hey there! Just stumbled upon your profile and I must say, it's pretty awesome. "

    # Reference the most popular post in a conversational tone
    if most_popular_post and most_popular_post['caption']:
        # Remove newlines from the caption excerpt
        caption_excerpt = most_popular_post['caption'][:30].replace('\n', ' ')
        message += f"Your post '{caption_excerpt}' really caught my eye. Loved the vibe! "

    # Reference specific themes or entities
    if 'travel' in all_keywords or 'GPE' in all_entities:
        message += "The way you capture your travel adventures is just captivating. "
    if 'food' in all_keywords:
        message += "And your food posts? Simply delicious! "
    if 'music' in all_keywords:
        message += "Also, I can see we share a mutual love for music. "

    # Suggest sharing the new post
    message += f"We've also got something exciting that we think you'll love. Check it out below , it might just be your next favorite! If you enjoy it, feel free to share it on your story. We'd be thrilled, but no pressure at all. Only if it truly resonates with you. Cheers, 106 Records"

    return message



def send_direct_message(page, username, message,url):
    """Navigates to a user's Instagram profile and sends a direct message."""
    try:
        print(f"Attempting to send a message to {username}...")
        page.goto(f'https://www.instagram.com/{username}/')
        page.wait_for_load_state("networkidle")

        # Attempt to find and click the 'Message' button
        message_button_selector = "div[role='button']:has-text('Message')"
        if page.is_visible(message_button_selector):
            page.click(message_button_selector)
            random_delay(1, 3)

            # Attempt to find the message box using a detailed selector
            message_box_selector = "p[class='xat24cr xdj266r']"
            if page.wait_for_selector(message_box_selector, state="visible", timeout=5000):
                page.click(message_box_selector)
                random_delay(0.5, 1)  # Adding a brief delay before typing

                # Type the message and press Enter
                page.keyboard.type(message)
                time.sleep(3)
                page.keyboard.press('Enter')
                time.sleep(3)

                page.keyboard.type(url)
                time.sleep(3)
                page.keyboard.press('Enter')
                time.sleep(3)

                print(f"Message sent to {username}.")
            else:
                print(f"Message box not found for {username}.")
        else:
            print(f"Message button not found for {username}.")
    except Exception as e:
        print(f"Failed to send a message to {username}: {e}")
        
def main():
    insta_username = 'tauseeq.1'
    password = 'Miniclip!2345'

    start_time = time.time()

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        page = browser.new_page()
        login_to_instagram(page,insta_username,password)
        username = input('Enter username for testing : ')
        url = input('URL: ')
        print('Getting data...')
        posts_data = fetch_user_posts(username)
        print('Data Retreived...')
        print('')
        print('Getting best posts...')
        most_popular_post, all_keywords, all_entities = analyze_user_profile(posts_data)
        print('Data Retreived...')
        print('')
        print('Generatign personalised message')
        personalized_message = generate_personalized_message(most_popular_post, all_keywords, all_entities)
        print('Message generated...')
        print(personalized_message)
        print('')
        print('Sending message...')
        send_direct_message(page, username, personalized_message,url)
        print('Message sent!')
        browser.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program finished in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()