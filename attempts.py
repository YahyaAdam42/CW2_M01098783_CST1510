import sqlite3

import pandas as pd
import streamlit as st
from openai import OpenAI

from log_hash import save_user, check_user

DB_PATH = "DATA/intelligence_platform.db"


# ---------- Database Helpers ----------

def get_db_connection():
    """Open a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def load_cyber_incidents():
    """Return all rows from the cyber_incidents table as a DataFrame."""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
        conn.close()
        return df
    except (sqlite3.Error, FileNotFoundError):
        return None


def insert_incident(title: str, severity: str, status: str):
    """Insert a new incident into the cyber_incidents table."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cyber_incidents (title, severity, status)
        VALUES (?, ?, ?)
        """,
        (title, severity, status),
    )
    conn.commit()
    conn.close()


# ---------- Session State ----------

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "messages" not in st.session_state:
        # Domain-specific system prompt for cybersecurity Tier 3
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are a cybersecurity expert assistant.\n"
                    "- Analyze security incidents and threats.\n"
                    "- Provide technical guidance using standard terminology (e.g. MITRE ATT&CK, CVE).\n"
                    "- Explain attack vectors and mitigations clearly.\n"
                    "- Prioritize actionable recommendations.\n"
                    "Tone: Professional and concise.\n"
                    "Format answers as clear steps or bullet points where helpful."
                ),
            }
        ]


def get_openai_client():
    """Create an OpenAI client using Streamlit secrets. Returns None if not configured."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# ---------- Main App ----------

def main():
    st.set_page_config(page_title="Cybersecurity Intelligence Platform", layout="wide")
    init_session_state()

    st.title("🛡️ Cybersecurity Intelligence Platform (Tier 3)")

    col_login, col_register = st.columns(2)

    # --- Registration ---
    with col_register:
        st.subheader("Register")
        reg_username = st.text_input("New username", key="reg_username")
        reg_password = st.text_input("New password", type="password", key="reg_password")
        if st.button("Create account"):
            if not reg_username or not reg_password:
                st.warning("Please enter both a username and a password.")
            else:
                save_user(reg_username, reg_password)
                st.success("Account created. You can now log in.")

    # --- Login ---
    with col_login:
        st.subheader("Log in")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in"):
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")

    st.markdown("---")

    # --- Protected Dashboard ---
    if not st.session_state.logged_in:
        st.info("Log in to view the Cybersecurity dashboard and AI assistant.")
        return

    st.subheader(f"Cybersecurity Dashboard – {st.session_state.username}")

    incidents = load_cyber_incidents()
    if incidents is None:
        st.error(
            "No cyber_incidents table found.\n\n"
            "Make sure you have run `python test.py` to create the database "
            "and load the CSV data into DATA/intelligence_platform.db."
        )
        return

    # Show all incidents
    st.markdown("### All Cyber Incidents")
    st.dataframe(incidents, use_container_width=True)

    # Simple aggregation by severity
    st.markdown("### Incidents by Severity")
    if "severity" in incidents.columns:
        severity_counts = incidents["severity"].value_counts().reset_index()
        severity_counts.columns = ["severity", "count"]
        st.bar_chart(severity_counts.set_index("severity")["count"])
    else:
        st.info("No 'severity' column found in cyber_incidents table.")

    # Simple CREATE operation (add new incident)
    st.markdown("### Add New Incident")
    with st.form("new_incident_form"):
        new_title = st.text_input("Incident title")
        new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        new_status = st.selectbox("Status", ["open", "in progress", "resolved"])
        submitted = st.form_submit_button("Add incident")

        if submitted:
            if not new_title:
                st.warning("Title is required.")
            else:
                insert_incident(new_title, new_severity, new_status)
                st.success("Incident added.")

                # Reload incidents after insert
                incidents = load_cyber_incidents()
                st.dataframe(incidents, use_container_width=True)

    st.markdown("---")

    # --- Tier 3: Cybersecurity AI Assistant ---
    st.subheader("🤖 Cybersecurity AI Assistant")

    client = get_openai_client()
    if client is None:
        st.error(
            "OpenAI API key not configured.\n\n"
            "Add your key to `.streamlit/secrets.toml` as:\n"
            'OPENAI_API_KEY = "sk-your-real-key-here"'
        )
    else:
        # Sidebar controls for chat
        with st.sidebar:
            st.title("💬 Chat Controls")
            # Count non-system messages
            message_count = len(
                [m for m in st.session_state.messages if m["role"] != "system"]
            )
            st.metric("Messages", message_count)
            if st.button("🗑️ Clear Chat", use_container_width=True):
                # Reset to initial system prompt
                st.session_state.messages = [
                    st.session_state.messages[0]
                ]
                st.rerun()

        # Display chat history (excluding system)
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        user_input = st.chat_input("Ask the cybersecurity assistant...")
        if user_input:
            # Show user message
            with st.chat_message("user"):
                st.markdown(user_input)

            # Add user message to history
            st.session_state.messages.append(
                {"role": "user", "content": user_input}
            )

            # Call OpenAI ChatGPT API
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages,
                )
                ai_message = response.choices[0].message.content

                # Display AI response
                with st.chat_message("assistant"):
                    st.markdown(ai_message)

                # Save AI response to history
                st.session_state.messages.append(
                    {"role": "assistant", "content": ai_message}
                )

            except Exception as e:
                # Show the REAL error from OpenAI / network
                error_text = f"There was an error contacting the AI service:\n\n`{e}`"
                with st.chat_message("assistant"):
                    st.error(error_text)


    st.markdown("---")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")


if __name__ == "__main__":
    main()
