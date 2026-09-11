from imap_tools import AND, MailBox


def fetch_unread_emails(host, user, password):
    """Fetch unread inbox messages over IMAP SSL without marking them as seen."""
    emails = []
    with MailBox(host).login(user, password) as mailbox:
        for msg in mailbox.fetch(AND(seen=False), mark_seen=False):
            emails.append(
                {
                    # Message-ID header comes through .headers as {name: (values,)}
                    "message_id": msg.headers.get("message-id", [""])[0],
                    "sender": msg.from_,
                    "subject": msg.subject,
                    "body_text": msg.text or msg.html or "",
                }
            )
    return emails
