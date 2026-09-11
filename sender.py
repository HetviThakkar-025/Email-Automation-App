import smtplib
from email.message import EmailMessage


def send_reply(host, port, user, password, to_address, subject, body_text, in_reply_to_message_id):
    """Send a reply over SMTP+TLS, threaded to in_reply_to_message_id."""
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to_address
    msg["Subject"] = subject
    msg["In-Reply-To"] = in_reply_to_message_id
    msg["References"] = in_reply_to_message_id
    msg.set_content(body_text)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
