# Google Images Scraper

A Python script to download images from Google Images using Selenium.

## Prerequisites
- Python 3.x
- Chrome browser

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
Edit `main.py` to configure:
- `SEARCH_TERMS`: List of search queries
- `NUMBER_OF_IMAGES`: Images to download per query (default: 50)
- `SAVE_FOLDER`: Download directory (default: `downloaded_images`)

## Usage
```bash
python main.py
```

Images will be saved to `downloaded_images/<search_term>/`

Logs are written to `scraper.log` and console.

## Notes
- The script includes random delays to mimic human behavior
- Google may still detect/block automated scraping
- Image quality depends on what Google serves
