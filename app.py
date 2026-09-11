import os

import streamlit as st
from dotenv import load_dotenv

from pipeline import run_pipeline
from sender import send_reply
from state import load_processed, save_processed

load_dotenv()

st.set_page_config(page_title="Email Automation")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

CATEGORY_COLORS = {
    "sales_lead": "#2ecc71",
    "support": "#3498db",
    "spam": "#e74c3c",
    "other": "#95a5a6",
}


def badge(category):
    color = CATEGORY_COLORS.get(category, "#95a5a6")
    return (
        f'<span style="background-color:{color};color:white;padding:2px 10px;'
        f'border-radius:10px;font-size:0.85em;">{category}</span>'
    )


st.title("Email Automation Dashboard")

if st.button("Check for new emails"):
    with st.spinner("Checking mailbox..."):
        before_count = len(load_processed())
        try:
            processed_after = run_pipeline()
        except Exception as e:
            st.error(f"Pipeline run failed: {e}")
            processed_after = None

    if processed_after is not None:
        new_count = len(processed_after) - before_count
        st.success(f"Checked mailbox. {new_count} new email(s) processed, {len(processed_after)} total tracked.")

st.divider()

processed = load_processed()

if not processed:
    st.info("No processed emails yet. Click 'Check for new emails' to get started.")
else:
    leads = {mid: r for mid, r in processed.items() if r.get("status") in ("pending_review", "sent")}
    logged = {mid: r for mid, r in processed.items() if r.get("status") == "logged"}

    st.subheader(f"Sales Leads ({len(leads)})")

    if not leads:
        st.write("No sales leads yet.")

    for message_id, record in leads.items():
        with st.container(border=True):
            st.markdown(f"**{record['subject']}**")
            st.caption(f"From: {record['sender']}")
            st.markdown(badge(record["category"]), unsafe_allow_html=True)
            st.write(f"Confidence: {record['confidence']}")
            st.write(f"Reasoning: {record['reasoning']}")

            status = record.get("status")

            if status == "pending_review":
                edited_reply = st.text_area(
                    "Drafted reply", value=record.get("reply", ""), key=f"reply_{message_id}"
                )
                if st.button("Approve & Send", key=f"send_{message_id}"):
                    try:
                        send_reply(
                            host="smtp.gmail.com",
                            port=587,
                            user=GMAIL_USER,
                            password=GMAIL_APP_PASSWORD,
                            to_address=record["sender"],
                            subject=record["subject"],
                            body_text=edited_reply,
                            in_reply_to_message_id=message_id,
                        )
                        current = load_processed()
                        current[message_id]["reply"] = edited_reply
                        current[message_id]["status"] = "sent"
                        save_processed(current)
                        st.success("Sent!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to send: {e}")

            elif status == "sent":
                st.success("✓ Sent")

    if logged:
        with st.expander(f"Other emails ({len(logged)}) — logged, no action needed"):
            for message_id, record in logged.items():
                st.markdown(f"**{record['subject']}** — {record['sender']}")
                st.markdown(badge(record["category"]), unsafe_allow_html=True)
                st.caption(record["reasoning"])
                st.write("")
