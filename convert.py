import sys
import os
import argparse
from bs4 import BeautifulSoup
import html2text
import yaml
from datetime import datetime

def convert_date_format(date_str: str) -> str:
    """
    Convert date from DD.MM.YYYY format to YYYY-MM-DD format.
    """
    try:
        # Convert the string to a datetime object using the DD.MM.YYYY format
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        # Convert back to string in the desired YYYY-MM-DD format
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        # Return the date as is if it doesn't match the expected format
        return date_str


def clean_and_extract_metadata(input_html: str) -> dict:
    # Parse the input HTML
    soup = BeautifulSoup(input_html, 'html.parser')
    
    # Initialize the metadata dictionary
    metadata = {
        'tags': [],
        'date': None,
        'author': None,
        'body': None,  # Added key to store the cleaned HTML body
        'title': None  # New key for the title
    }
    
    # Extract the title from <h1 class="article-title"> tag
    article_title_tag = soup.find('h1', class_='article-title')
    if article_title_tag:
        metadata['title'] = article_title_tag.get_text()
        article_title_tag.decompose()  # Remove the title tag from the HTML
    
    # Extract post tags under <a> tags with class "tag"
    for tag in soup.find_all('a', class_='tag'):
        metadata['tags'].append(tag.get_text())

    # Extract post author under <strong> tag inside <div class="meta">
    meta_div = soup.find('div', class_='meta')
    if meta_div:
        author = meta_div.find('strong')
        if author:
            metadata['author'] = author.get_text()

        # Extract post date from <time> tag inside <div class="meta">
        time_tag = meta_div.find('time')
        if time_tag:
            date_str = time_tag.get_text().strip()
            # Convert the date from DD.MM.YYYY to YYYY-MM-DD format
            metadata['date'] = convert_date_format(date_str)

    # Remove <div class="meta"> tag (since we've already extracted the info)
    if meta_div:
        meta_div.decompose()
    
    # Remove all <a> tags with class "tag"
    for tag in soup.find_all('a', class_='tag'):
        tag.decompose()
    
    # Remove all <aside> and <script> tags
    for tag in soup(['aside', 'script']):
        tag.decompose()

    # Remove any <div> tags with class "block-tag"
    for block_tag in soup.find_all('div', class_='block-tag'):
        block_tag.decompose()

    # Save the cleaned HTML under the 'body' key
    metadata['body'] = str(soup)
    
    return metadata


def convert_to_jekyll_post(metadata: dict) -> str:
    # Convert the cleaned HTML (body) to Markdown
    h = html2text.HTML2Text()
    h.body_width = 0  # Prevent wrapping of lines
    markdown_content = h.handle(metadata['body'])
    
    # Create the Jekyll front matter (YAML header)
    front_matter = {
        'layout': 'post',
        'title': metadata['title'],  # Use the title extracted from the HTML
        'author': metadata.get('author', 'Unknown'),
        'date': metadata.get('date', str(datetime.now().date())),
        'tags': metadata.get('tags', []),
    }
    
    # Convert the front matter dictionary to YAML
    yaml_front_matter = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
    
    # Format the final Jekyll post
    post = f"---\n{yaml_front_matter}---\n\n{markdown_content}"
    
    return post


def write_jekyll_post(markdown_content: str, target_directory: str) -> str:
    # Extract the front matter (YAML header) from the Markdown content
    if markdown_content.startswith('---'):
        # Split the content into front matter and body
        parts = markdown_content.split('---', 2)
        front_matter = parts[1].strip()  # Extract YAML front matter
        body_content = parts[2].strip()  # Extract the body (Markdown)
    else:
        raise ValueError("Markdown content must start with '---' for front matter.")
    
    # Parse the YAML front matter to a dictionary
    try:
        metadata = yaml.safe_load(front_matter)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing front matter: {e}")
    
    # Get the date and title from the front matter to create the filename
    date_str = metadata.get('date', str(datetime.now().date()))  # Default to today's date if not found
    title = metadata.get('title', 'untitled').replace(' ', '-').lower()  # Default title if not found
    
    # Ensure the date is in the correct format (YYYY-MM-DD)
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_filename = date_obj.strftime('%Y-%m-%d')  # Format the date for the filename
    except ValueError:
        raise ValueError("Date in front matter is not in the correct format (YYYY-MM-DD).")
    
    # Generate the filename (e.g., 2025-02-01-my-post-title.md)
    filename = f"{date_filename}-{title}.md"
    
    # Ensure the target directory exists
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    
    # Define the full path for the post file
    file_path = os.path.join(target_directory, filename)
    
    # Write the Markdown content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(front_matter)  # Write the front matter
        f.write('\n---\n\n')
        f.write(body_content)  # Write the body content
    
    return file_path


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert HTML to a Jekyll post.")
    parser.add_argument('target_directory', type=str, help="The directory where the Jekyll post will be saved.")
    
    # Parse the command-line arguments
    args = parser.parse_args()
    target_directory = args.target_directory
    
    # Read HTML input from standard input
    print("Please input the HTML string:")
    input_html = sys.stdin.read()  # Read the entire input as a string
    


import sys
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

def get_html_from_existing_firefox(url):
    """
    Connect to an existing Firefox session and fetch the HTML for the given URL.
    """
    # Set up the Firefox options to connect to the existing session
    options = Options()
    options.set_capability('moz:firefoxOptions', {
        'args': ['--remote-debugging-port=9222']
    })
    
    # Connect to the existing Firefox session
    driver = webdriver.Firefox(options=options)  # Ensure geckodriver is in PATH or specify the full path
    
    # Navigate to the URL
    driver.get(url)

    # Wait for the page to load (adjust time as needed)
    time.sleep(3)  # You may want to adjust this depending on your network speed

    # Get the page source (HTML)
    page_html = driver.page_source

    # Close the session
    driver.quit()

    return page_html


def extract_article_section(html):
    """
    Extract the <section> tag with class 'article' from the provided HTML string.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    article_section = soup.find('section', class_='article')

    if article_section:
        return str(article_section)
    else:
        return None

import os
import re
import hashlib
import requests
from urllib.parse import urlparse
from pathlib import Path

def get_md5_checksum(content):
    """
    Computes the MD5 checksum of the given content.
    
    :param content: The content (bytes) of the file.
    :return: The MD5 checksum as a hexadecimal string.
    """
    return hashlib.md5(content).hexdigest()

def download_images_in_markdown(markdown_content, base_url, download_dir):
    """
    Downloads images from the markdown content and rewrites image links to point to the local directory.
    The downloaded image filenames will be based on their MD5 checksum.

    :param markdown_content: The Markdown content as a string.
    :param base_url: The base URL from where the images will be downloaded (for relative URLs).
    :param download_dir: The relative directory where images should be saved.
    :return: The modified Markdown content with updated image links.
    """
    
    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Regular expression to find image links (Markdown syntax: ![alt text](image_url))
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def download_image(image_url):
        """
        Downloads the image from the provided URL, calculates its MD5 checksum,
        and saves it in the specified directory with the checksum as the filename.
        The function avoids downloading the same image multiple times.

        :param image_url: The URL of the image.
        :return: The local file path where the image was saved, or None if there was an error.
        """
        # If the URL is relative, convert it to an absolute URL using the base URL
        if not image_url.startswith('http'):
            image_url = os.path.join(base_url, image_url)
        
        # Download the image content
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            image_content = response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e}")
            return None
        
        # Calculate the MD5 checksum of the image content
        image_checksum = get_md5_checksum(image_content)
        
        # Extract the file extension from the original URL (default to .jpg if no extension)
        image_ext = os.path.splitext(urlparse(image_url).path)[-1] or '.jpg'
        
        # Create the local file path using the MD5 checksum as the filename
        image_filename = f"{image_checksum}{image_ext}"
        image_path = os.path.join(download_dir, image_filename)

        # Avoid overwriting existing files by checking if the file already exists
        if os.path.exists(image_path):
            print(f"Image already downloaded: {image_url} -> {image_path}")
            return image_path
        
        # Save the image to the local path
        with open(image_path, 'wb') as file:
            file.write(image_content)
        print(f"Downloaded image: {image_url} -> {image_path}")
        
        return image_path
    
    # Function to update the image URL in the Markdown content
    def replace_image_link(match):
        alt_text = match.group(1)
        image_url = match.group(2)
        
        # Download the image and get the local file path
        local_image_path = download_image(image_url)
        
        # If the image was downloaded successfully, replace the URL in the Markdown content
        if local_image_path:
            # Make the relative path to the image file in the download directory
            local_image_url = os.path.join(download_dir, os.path.basename(local_image_path)).replace(os.sep, '/')
            return f"![{alt_text}]({local_image_url})"
        return match.group(0)
    
    # Replace all image links in the Markdown content
    modified_markdown = re.sub(image_pattern, replace_image_link, markdown_content)
    
    return modified_markdown





def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Fetch a URL and extract the <section> with class 'article' using Firefox.")
    parser.add_argument('url', nargs='+', type=str, help="The URL to fetch and extract the article section from.")
    parser.add_argument('-p', '--posts-directory', type=str, required=True, help="where to put the resulting markdown")
    parser.add_argument('-a', '--assets-directory', type=str, required=True, help="where to put the assets")        
    
    # Parse the command-line arguments
    args = parser.parse_args()

    for url in args.url:
        # Fetch HTML from existing Firefox session
        html_content = get_html_from_existing_firefox(url)

        # Extract the article section from the HTML
        article_html = extract_article_section(html_content)

        # Output the extracted article section
        if article_html:
            print("Extracted Article Section:")
            # print(article_html)

            input_html = article_html

            # Clean the HTML and extract metadata
            metadata = clean_and_extract_metadata(input_html)

            # Convert the cleaned HTML and metadata to a Jekyll post (Markdown)
            markdown_post = convert_to_jekyll_post(metadata)

            markdown_post = download_images_in_markdown(markdown_post, "http://localhost", args.assets_directory)
            
            # Write the Markdown post to the specified target directory with the correct filename
            post_file_path = write_jekyll_post(markdown_post, args.posts_directory)

            # Print the file path where the post is saved
            print(f"Jekyll post written to: {post_file_path}")

        else:
            print("Could not find the article section.")


if __name__ == "__main__":
    main()
