# Imager: A Selenium-Based Image Scraping Utility

**A Python automation Script designed to collect high-resolution visual data from dynamic web environments. **

![Banner](imager_banner.png)

![video](imager_video.gif)

## Description

**Imager** is a specialized utility developed to automate the manual bottleneck of gathering image datasets. Unlike traditional scraping methods that struggle with JavaScript-heavy sites, Imager leverages **Selenium WebDriver** to interact with the browser like a human would.

It handles complex tasks such as triggering infinite scrolls, interacting with lazy-loaded thumbnails to reach full-resolution source files, and managing large-scale downloads. This tool is ideal for developers needing to build local datasets for machine learning models or research purposes.

## Key Features

- **High Resolution Original Images**: Bypasses Google's thumbnails to fetch original high-quality files by visiting the source websites.
- **Dynamic Content Handling**: Configured to manage infinite scrolls and lazy-loaded elements.
- **Intelligent Loading**: Configurable timeouts (`WEBSITE_LOAD_TIMEOUT`) ensure the scraper skips down or slow websites instead of long waiting.
- **Stealth Integration**: Features User-Agent rotation and random human-like delays to minimize automated detection.

## Prerequisites

- Python 3.10+
- Google Chrome Browser
- `venv` ( Not Necessary but recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/santoshvandari/Imager.git
   cd Imager
   ```

2. Setup virtual environment:
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Copy the example environment file and customize your settings:

```bash
cp src/.env.example src/.env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SEARCH_TERMS` | Comma-separated list of queries | `cyberpunk city` |
| `NUMBER_OF_IMAGES` | Images to download per query | `5` |
| `SAVE_FOLDER` | Root folder for downloads | `downloaded_images` |
| `WEBSITE_LOAD_TIMEOUT`| Max seconds to wait for source sites | `10` |
| `LOG_FILE` | Path to log results | `scraper.log` |

## Usage

Run the utility via terminal:
```bash
python3 src/main.py
```

Images will be saved in `downloaded_images/{query_name}/`.

## Contributing
We welcome contributions! If you'd like to contribute to this Flutter Package Project, please check out our [Contribution Guidelines](CONTRIBUTING.md).

## Code of Conduct
Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before participating in this app.

## License
This project is licensed under the MIT [License](LICENSE).
