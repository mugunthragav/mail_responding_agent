

from typing import List, Dict
from .gmail_fetcher import fetcher
from .logger import get_logger

logger = get_logger(__name__)

def load_emails(use_live: bool = True) -> List[Dict]:

    try:
        if use_live:
            return fetcher.fetch_unread_emails(max_emails=10)
        # Fallback to sample
        with open("data/sample_emails.json", "r") as f:
            import json
            emails = json.load(f)
        logger.info(f"Loaded {len(emails)} sample emails (live mode off)")
        return emails
    except Exception as e:
        logger.error(f"Failed to load emails: {e}")
        return []