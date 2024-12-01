import os
import requests
import pandas as pd
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# WordPress API credentials and configuration
WP_BASE_URL = os.getenv("WP_BASE_URL")
WP_API_KEY = os.getenv("WP_API_KEY")
DEFAULT_AUTHOR_ID = int(os.getenv("DEFAULT_AUTHOR_ID"))

# Headers for authentication
HEADERS = {
    "Authorization": f"Basic {WP_API_KEY}",
}

# Mapping for Status column normalization
STATUS_MAPPING = {
    "PUBLISHED": "publish",
    "DRAFT": "draft",
    "PENDING": "pending",
    "PRIVATE": "private",
    "FUTURE": "future"
}

# Function to upload an image to WordPress media library
def upload_image(image_url):
    if not image_url or pd.isna(image_url):
        print("No image URL provided.")
        return None

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            print(f"Failed to fetch image from {image_url}. Status code: {response.status_code}")
            return None

        filename = os.path.basename(urlparse(image_url).path)
        media_url = f"{WP_BASE_URL}/media"
        files = {
            "file": (filename, response.content)
        }
        media_response = requests.post(media_url, headers=HEADERS, files=files)
        if media_response.status_code == 201:
            print(f"Image uploaded successfully: {filename}")
            return media_response.json()["id"]
        else:
            print(f"Failed to upload image: {media_response.status_code} - {media_response.json()}")
            return None
    except Exception as e:
        print(f"Error during image upload: {e}")
        return None

# Function to fetch or create a term (categories or tags)
def get_or_create_term(term_name, taxonomy):
    try:
        term_url = f"{WP_BASE_URL}/{taxonomy}"
        # Fetch existing terms
        response = requests.get(term_url, headers=HEADERS)
        if response.status_code == 200:
            terms = response.json()
            # Check if term already exists
            for term in terms:
                if term["name"].lower() == term_name.lower():
                    return term["id"]

        # Create term if it doesn't exist
        term_data = {"name": term_name}
        create_response = requests.post(term_url, headers=HEADERS, json=term_data)
        if create_response.status_code == 201:
            print(f"Created {taxonomy[:-1]}: {term_name}")
            return create_response.json()["id"]
        elif create_response.status_code == 400:
            error_data = create_response.json()
            if error_data["code"] == "term_exists":
                existing_id = error_data["data"]["term_id"]
                print(f"{taxonomy[:-1].capitalize()} '{term_name}' already exists with ID {existing_id}. Using existing ID.")
                return existing_id
            else:
                print(f"Failed to create {taxonomy[:-1]} '{term_name}': {create_response.status_code} - {error_data}")
                return None
        else:
            print(f"Failed to create {taxonomy[:-1]} '{term_name}': {create_response.status_code} - {create_response.json()}")
            return None
    except Exception as e:
        print(f"Error while fetching/creating {taxonomy[:-1]}: {e}")
        return None

# Function to create a blog post
def create_blog_post(post_data):
    try:
        post_url = f"{WP_BASE_URL}/posts"
        response = requests.post(post_url, headers=HEADERS, json=post_data)
        if response.status_code == 201:
            print(f"Post '{post_data['title']}' created successfully!")
        else:
            print(f"Failed to create post: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error during post creation: {e}")

# Function to process the CSV and create posts
def process_csv(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        for index, row in df.iterrows():
            print(f"Processing row {index + 1}: {row['Post title']}")

            # Upload featured image and get its ID
            image_id = upload_image(row["Featured image URL"])
            
            # Normalize status
            post_status = STATUS_MAPPING.get(row["Status"].upper(), "draft")
            
            # Fetch or create terms for both categories and tags
            term_ids = []
            if pd.notna(row["Tags"]):
                tag_names = [tag.strip() for tag in row["Tags"].split(",")]
                for tag_name in tag_names:
                    tag_id = get_or_create_term(tag_name, "tags")
                    if tag_id:
                        term_ids.append(tag_id)
                    # Add the same term to categories
                    category_id = get_or_create_term(tag_name, "categories")
                    if category_id and category_id not in term_ids:
                        term_ids.append(category_id)

            # Prepare the blog post data
            post_data = {
                "title": row["Post title"],
                "content": row["Post body"],
                "excerpt": row["Meta description"] if pd.notna(row["Meta description"]) else "",
                "slug": row["Post URL"],
                "status": post_status,
                "author": DEFAULT_AUTHOR_ID,  # Use the constant from .env
                "date": row["Publish date"],  # Use the Publish date field
                "categories": term_ids,  # Assign the same terms to categories
                "tags": term_ids,  # Assign the same terms to tags
                "meta": {
                    "seo_title": row["Post SEO title"],
                    "language": row["Post language"],
                    "archived": str(row["Archived"]).lower() == "true"
                },
                "featured_media": image_id if image_id else None
            }
            
            # Create the post in WordPress
            create_blog_post(post_data)

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found. Please ensure the file is in the correct directory.")
    except Exception as e:
        print(f"Error while processing CSV: {e}")

if __name__ == "__main__":
    # Path to the CSV file
    CSV_FILE_PATH = "blog_posts.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    CSV_FILE_PATH = os.path.join(script_dir, CSV_FILE_PATH)

    # Process the CSV and upload posts
    process_csv(CSV_FILE_PATH)