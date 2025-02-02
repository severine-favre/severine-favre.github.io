import os
import re
import hashlib
import requests
from urllib.parse import urlparse, urljoin
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
    Links in the Markdown will be absolute URLs.

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
            image_url = urljoin(base_url, image_url)
        
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
            # Make the absolute URL to the image file in the download directory
            local_image_url = os.path.join(base_url, download_dir, os.path.basename(local_image_path)).replace(os.sep, '/')
            return f"![{alt_text}]({local_image_url})"
        else:
            # drop unresolved images
            return ""
    
    # Replace all image links in the Markdown content
    modified_markdown = re.sub(image_pattern, replace_image_link, markdown_content)
    
    return modified_markdown


def main():
    # Sample Markdown content (this would typically come from a file)
    markdown_content = """
    # Sample Markdown
    
    This is a sample markdown file with images.
    
    ![Image 1](https://example.com/images/image1.jpg)
    ![Image 2](./relative/path/to/image2.png)
    ![Image 3](https://example.com/images/image1.jpg)  # Same image name as image1.jpg
    """
    
    base_url = "https://example.com"  # Base URL to resolve relative image URLs
    download_dir = "downloaded_images"  # Local directory to store downloaded images
    
    # Download images and rewrite image links in the markdown content
    updated_markdown = download_images_in_markdown(markdown_content, base_url, download_dir)
    
    # Output the modified Markdown content
    print(updated_markdown)


if __name__ == "__main__":
    main()
