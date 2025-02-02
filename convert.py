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
        metadata['tags'].append(tag.get_text().strip())

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


import re

def insert_excerpt_separator(content):
    # Regular expression to find the front matter (usually enclosed with '---')
    front_matter_pattern = re.compile(r"^---\s*(.*?)\s*---", re.DOTALL)

    # Check if front matter exists
    match = front_matter_pattern.match(content)
    if not match:
        raise ValueError("Front matter not found.")

    # Extract the front matter and the rest of the content
    front_matter = match.group(1)
    body_content = content[match.end():].lstrip()  # Remove the front matter and whitespace after it

    # Add 'excerpt_separator: <!--more-->' to the front matter
    front_matter += "\nexcerpt_separator: <!--more-->"

    # Regular expression for detecting paragraphs
    # This matches blocks of text separated by at least one blank line,
    # and ensures it's not an image or an empty paragraph.
    paragraph_pattern = re.compile(r"^(?!\!\[)(?!\s*$).+?(\n\s*\n|$)", re.DOTALL | re.MULTILINE)

    # Regular expression for detecting images
    image_pattern = re.compile(r"!\[.*?\]\(.*?\)")  # Image is any markdown image syntax ![alt](url)

    # Find the first image (if any)
    first_image = image_pattern.search(body_content)

    # Find the first paragraph (if any)
    first_paragraph = paragraph_pattern.search(body_content)

    # Insert <!--more--> after the last of the first paragraph or image
    if first_image and (not first_paragraph or first_image.start() > first_paragraph.start()):
        insert_position = first_image.end()
    elif first_paragraph:
        insert_position = first_paragraph.end()
    else:
        insert_position = 0  # Fallback in case there's no paragraph or image

    # Insert the <!--more--> tag in the content after the selected element
    body_content = body_content[:insert_position] + "\n<!--more-->\n" + body_content[insert_position:]

    # Rebuild the final content with the modified front matter and body
    final_content = f"---\n{front_matter}\n---\n{body_content}"
    
    return final_content

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Fetch a URL and extract the <section> with class 'article' using Firefox.")
    parser.add_argument('url', nargs='+', type=str, help="The URL to fetch and extract the article section from.")
    parser.add_argument('-p', '--posts-directory', type=str, default="_posts",
                        required=True, help="where to put the resulting markdown")
    parser.add_argument('-a', '--assets-directory', type=str, default="assets",
                        required=True, help="where to put the assets")        
    
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

            from assets import download_images_in_markdown
            markdown_post = download_images_in_markdown(markdown_post, "/", args.assets_directory)

            markdown_post = insert_excerpt_separator(markdown_post)
            
            # Write the Markdown post to the specified target directory with the correct filename
            # print(markdown_post)
            post_file_path = write_jekyll_post(markdown_post, args.posts_directory)

            # Print the file path where the post is saved
            print(f"Jekyll post written to: {post_file_path}")

        else:
            print("Could not find the article section.")


if __name__ == "__main__":
    main()




    
