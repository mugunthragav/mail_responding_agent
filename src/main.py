

import argparse
import json
from typing import Dict, Any
from agents.classifier import ClassifierAgent
from agents.drafter import DrafterAgent
from agents.refiner import RefinerAgent
from utils.email_reader import load_sample_emails
from utils.logger import get_logger

logger = get_logger(__name__)

def process_email(email: Dict[str, Any], feedback: str = None):
    email_id = email["id"]
    body = email["body"]
    
    logger.info(f"Processing email: {email_id} | Subject: {email['subject']}")

    
    category = classifier.classify(body)
    logger.info(f"Classification: {category}")

    
    draft = drafter.draft(body, email_id)
    logger.info("Draft generated")

    
    if feedback:
        refined = refiner.refine(body, draft, feedback, email_id)
        logger.info("Draft refined with feedback")
        return {
            "id": email_id,
            "category": category,
            "original_draft": draft,
            "refined_reply": refined,
            "feedback_used": feedback
        }
    else:
        return {
            "id": email_id,
            "category": category,
            "reply": draft
        }

def main():
    parser = argparse.ArgumentParser(description="AI Email Responder Agent (CLI Mode)")
    parser.add_argument("--email-id", type=str, help="Process specific email by ID")
    parser.add_argument("--feedback", type=str, help="Provide feedback to refine draft")
    parser.add_argument("--all", action="store_true", help="Process all sample emails")
    
    args = parser.parse_args()

    global classifier, drafter, refiner
    classifier = ClassifierAgent()
    drafter = DrafterAgent()
    refiner = RefinerAgent()

    emails = load_sample_emails()
    if not emails:
        logger.error("No emails loaded. Check /data/sample_emails.json")
        return

    target_emails = []
    if args.email_id:
        target = next((e for e in emails if e["id"] == args.email_id), None)
        if target:
            target_emails = [target]
        else:
            logger.error(f"Email ID {args.email_id} not found")
            return
    elif args.all:
        target_emails = emails
    else:
        # Default: process first email
        target_emails = [emails[0]]

    results = []
    for email in target_emails:
        result = process_email(email, feedback=args.feedback)
        results.append(result)
        print(json.dumps(result, indent=2))

    logger.info(f"Processed {len(results)} email(s)")

if __name__ == "__main__":
    main()