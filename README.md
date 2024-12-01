
# HubSpot to WordPress Blog Migration

This repository contains a Python script for migrating blog posts from HubSpot (exported as a CSV file) to a WordPress site using the WordPress REST API.

## Features
- Automatically uploads featured images to WordPress.
- Maps `Tags` from the CSV to both WordPress tags and categories.
- Creates new tags and categories if they don’t exist, or reuses existing ones.
- Assigns publish dates, metadata, and SEO titles to posts.
- Handles duplicate terms gracefully using the `term_exists` API response.

## Prerequisites
1. **WordPress REST API Authentication Plugin**:
   - Install and activate the [WordPress REST API Authentication plugin](https://wordpress.org/plugins/wp-rest-api-authentication/).
   - Generate an API key using Basic Authentication.

2. **Python Environment**:
   - Install Python 3.8+.
   - Install dependencies:
     ```bash
     pip install pandas requests python-dotenv
     ```

3. **CSV File**:
   - Export blog posts from HubSpot as a CSV file.

4. **Environment Variables**:
   - Create a `.env` file in the project directory with the following content:
     ```plaintext
     WP_BASE_URL=https://your-wordpress-site.com/wp-json/wp/v2
     WP_API_KEY=your-generated-api-key
     DEFAULT_AUTHOR_ID=2
     ```

## How to Generate WP_API_KEY
The `WP_API_KEY` is required for authenticating requests to the WordPress REST API. This key is a Base64-encoded string that combines your WordPress username and password.

### Steps to Generate WP_API_KEY
1. Replace `your_username` and `your_password` with your WordPress login credentials.
2. Run the following command in your terminal:
   ```bash
   echo -n "your_username:your_password" | base64
   ```
   For example:
   ```bash
   echo -n "admin:mySecurePassword123" | base64
   ```

3. The output will look like this:
   ```plaintext
   YWRtaW46bXlTZWN1cmVQYXNzd29yZDEyMw==
   ```

4. Copy the generated key and paste it into your `.env` file as the value for `WP_API_KEY`:
   ```plaintext
   WP_API_KEY=YWRtaW46bXlTZWN1cmVQYXNzd29yZDEyMw==
   ```

### Important Notes
- Use a strong and unique password for your WordPress account.
- Never share the Base64-encoded key publicly.
- Restrict the user's permissions if using an account dedicated to API access (e.g., Editor role).

## Usage
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Place the exported CSV file (`blog_posts.csv`) in the project directory.

3. Update the `.env` file with your WordPress API credentials.

4. Run the script:
   ```bash
   python blog_posts.py
   ```

5. Check the WordPress admin panel to verify the imported posts.

## CSV Format
The script expects the following fields in the CSV:
- `Blog name`
- `Post title`
- `Post SEO title`
- `Post language`
- `Post URL`
- `Author`
- `Tags`
- `Meta description`
- `Publish date`
- `Last modified date`
- `Post body`
- `Featured image URL`
- `Head HTML`
- `Status`
- `Archived`

## Error Handling
- **Term Already Exists**: Automatically reuses existing tag or category IDs.
- **Missing Fields**: Logs warnings for missing or invalid data.
- **API Authentication**: Uses the WordPress REST API Authentication plugin for secure access.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Feel free to fork this repository and submit pull requests for improvements or bug fixes.

## Author
**Quauhtli Martínez**
- Email: quauhtlimtz@gmail.com
