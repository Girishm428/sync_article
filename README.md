# Sync Article

A Python tool to fetch OpenZiti documentation, clean and convert its HTML content, and update Zendesk Help Center articles programmatically.

## Features

- Fetch dynamic content with Selenium
- Clean and transform HTML for Zendesk compatibility
- Convert tabs UI into static sections
- Update Zendesk article translations via API
- Configurable via environment variables
- Easy to extend and maintain

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/openziti-importer.git
cd sync_article

Install dependencies using Poetry:
poetry install


2. Rename .env.example:

```bash
Rename .env.example file to .env in the project root with the required variables:

ZENDESK_DOMAIN=yourdomain.zendesk.com
ZENDESK_ARTICLE_ID=123456789
ZENDESK_EMAIL=you@example.com
ZENDESK_API_TOKEN=your_api_token
OPENZITI_SOURCE_URL=https://docs.openziti.io/...
ZENDESK_LOCAL=en-us
ZENDESK_DST_TITLE=Your Article Title

Usage
Run the main script via Poetry:


poetry run python -m cli.main
Development
Run tests:

poetry run pytest
Format code with Black:

poetry run black .

License
MIT License © Girish Reddy

pgsql
