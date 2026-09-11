import os

from dotenv import load_dotenv

from classifier import classify_email
from mailbox import fetch_unread_emails
from reply_generator import generate_reply
from state import load_processed, save_processed


def run_pipeline():
    load_dotenv()
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    processed = load_processed()
    emails = fetch_unread_emails("imap.gmail.com", gmail_user, gmail_password)

    skipped_count = 0
    classified_count = 0

    for email in emails:
        message_id = email["message_id"]
        if message_id in processed:
            skipped_count += 1
            continue

        result = classify_email(email["sender"], email["subject"], email["body_text"])

        record = {
            "sender": email["sender"],
            "subject": email["subject"],
            "category": result["category"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
        }

        if result["category"] == "sales_lead":
            record["reply"] = generate_reply(email["sender"], email["subject"], email["body_text"])
            record["status"] = "pending_review"
        else:
            record["status"] = "logged"

        processed[message_id] = record
        save_processed(processed)
        classified_count += 1

    print(
        f"Fetched {len(emails)} unread email(s): "
        f"{skipped_count} already processed (skipped), {classified_count} newly classified."
    )

    return processed


if __name__ == "__main__":
    run_pipeline()
