

import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from .logger import get_logger

load_dotenv()

logger = get_logger(__name__)

class GmailFetcher:
    def __init__(self, cache_file: str = "data/live_emails.json"):
        self.email = os.getenv("GMAIL_EMAIL")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")
        self.cache_file = cache_file
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        if not self.email or not self.app_password:
            raise ValueError("GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in .env")

    def _connect(self) -> imaplib.IMAP4_SSL:
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.app_password)
            logger.info("Connected to Gmail IMAP")
            return mail
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            raise

    def _decode_header(self, header: bytes) -> str:
        decoded = decode_header(header)[0]
        if isinstance(decoded[0], bytes):
            return decoded[0].decode(decoded[1] or "utf-8")
        return str(header)

    def fetch_unread_emails(self, max_emails: int = 10, mark_as_read: bool = False) -> List[Dict]:

        mail = None
        try:
            mail = self._connect()
            mail.select("INBOX")
            
            # Search unread
            status, messages = mail.uid("search", None, "UNSEEN")
            if status != "OK":
                logger.error("Failed to search unread emails")
                return []
            
            email_uids = messages[0].split()[-max_emails:]  # Latest N
            if not email_uids:
                logger.info("No unread emails found")
                return []
            
            emails = []
            for uid in email_uids:
                status, msg_data = mail.uid("fetch", uid, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = self._decode_header(msg["subject"] or b"")
                from_ = self._decode_header(msg["from"] or b"")
                
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                
                email_dict = {"id": uid.decode("utf-8"), "subject": subject, "body": body, "from": from_}
                emails.append(email_dict)
                
                
                if mark_as_read:
                    mail.uid("store", uid, "+FLAGS", "\\Seen")
            
            
            self._save_cache(emails)
            logger.info(f"Fetched {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            # Fallback to cache
            return self._load_cache()
        finally:
            if mail:
                mail.close()
                mail.logout()

    def _save_cache(self, emails: List[Dict]):
        import json
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(emails, f, indent=2)

    def _load_cache(self) -> List[Dict]:
        import json
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

fetcher = GmailFetcher()