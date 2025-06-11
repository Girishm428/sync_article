# 🛠️ SyncApp: OpenZiti → Zendesk Importer

A Python-based automation tool to sync [OpenZiti](https://openziti.io/) documentation into Zendesk Help Center articles — complete with Mermaid diagram rendering, live logging, and a simple Web UI.

---

## 🚀 Features

- ✅ Import OpenZiti Markdown documentation from a source URL.
- ✅ Extract, render, and Zendesk using API (via article ID).
- ✅ Modify HTML output to suit Zendesk (e.g., convert `<h2>` tabs to `<h3>`, remove images inside admonitions).
- ✅ Live UI notifications 
- ✅ Web UI using [NiceGUI](https://nicegui.io) with:
  - Source URL, Article ID, and Title input
  - Settings modal (e.g., Zendesk email/token)
  - Sync status feedback
- ✅ CLI support (Windows & Ubuntu)
- 🧪 Logging & testing modules
- 🏗️ Configurable settings stored in `settings.json`

---

## 📁 Project Structure

├── syncapp/
│ ├── init.py
│ ├── backend/ # initate the core logic for sync process
│ ├── config/ # Load/save settings.json, and articles.db
│ ├── core/ # Fetchers, Cleaners, Handles Zendesk API interactions
│ ├── loggers/ # log_cli.py and setup_logger.py
│ ├── utils/ # Helper functions
│ ├── webui/ # NiceGUI app with appv4.py
│ | ├── appv5.py # Entrypoint for CLI or app launcher
├── README.md
├── requirements.txt
├── pyproject.toml


---

## 🖥️ Web UI Usage

### Launch

```bash
python syncapp/webui/appv5.py
```

### Features

#### Form to input:

    ✅ Source URL
    ✅ Zendesk Article ID
    ✅ Article Title
    ✅ Multi-article sync queue

#### Settings page:

    Zendesk subdomain

#### Email / API token

    Sync button triggers backend with real-time log feedback.

```

## 🛠️ Setup
1. Clone

```bash
git clone https://github.com/Girishm428/sync_article.git
cd sync_article
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure settings.json
Auto-generated on first run, or manually edit to include:

```bash
{
  "zendesk_subdomain": "yourdomain",
  "zendesk_email": "your@email.com",
  "zendesk_token": "your_token_here",
  "zendesk_local": "en-us"  
}
```

License
MIT License


---

Let me know if you'd like to auto-generate the `requirements.txt`, add screenshots, or create badges (e.g., GitHub Actions, PyPI).
