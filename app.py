import os, re, time, sqlite3
import pandas as pd
import streamlit as st
from google import genai

st.set_page_config(page_title="AskBLR", page_icon="🍽️")
st.title("AskBLR: ask about Bengaluru restaurants")
st.caption("Type a question in plain English. The AI writes the SQL, runs it on 12,480 restaurants and explains the result.")


@st.cache_resource
def get_con():
    return sqlite3.connect("file:bengaluru_restaurants.db?mode=ro", uri=True, check_same_thread=False)


con = get_con()

api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass
api_key = api_key or os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("Paste your Gemini API key", type="password")
if not api_key:
    st.stop()

client = genai.Client(api_key=api_key)
CANDIDATES = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash",
              "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def get_schema():
    out = []
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cols = con.execute(f"PRAGMA table_info({t})").fetchall()
        out.append(f"{t}(" + ", ".join(f"{c[1]} {c[2]}" for c in cols) + ")")
    return "\n".join(out)


SCHEMA = get_schema() + """

Column notes:
- restaurants.location: the neighbourhood or area of the restaurant (for example Whitefield, BTM). When a question says "area" or "neighbourhood", use location.
- restaurants.listing_area: a broader Zomato listing region. Do NOT use it unless the question mentions "listing".
- restaurants.listing_type: the Zomato listing category (Buffet, Delivery, Dine-out). It is not the cuisine.
- restaurants.rate: rating out of 5, NULL if unrated.
- restaurants.cost_for_two: approximate cost for two people in rupees.
- restaurants.online_order and restaurants.book_table: 'Yes' or 'No'.
- restaurants.rest_type: type of place (Quick Bites, Casual Dining, Cafe).
- restaurant_cuisines: one row per restaurant per cuisine.
"""


def run_sql(query):
    q = query.strip().rstrip(";")
    if not re.match(r"^(select|with)\b", q, re.I):
        return "Error: only SELECT queries are allowed"
    if re.search(r"\b(insert|update|delete|drop|alter|create|attach|pragma|replace)\b", q, re.I):
        return "Error: this query contains a blocked keyword"
    try:
        return pd.read_sql(q, con)
    except Exception as e:
        return f"Error: {e}"


def ask_llm(prompt):
    order = ([st.session_state["model"]] if "model" in st.session_state else []) + CANDIDATES
    last = None
    for m in order:
        for _ in range(2):
            try:
                text = client.models.generate_content(model=m, contents=prompt).text
                st.session_state["model"] = m
                return text
            except Exception as e:
                last = e
                if "503" in str(e) or "429" in str(e):
                    time.sleep(4)
                    continue
                break
    raise RuntimeError(f"All models failed. Last error: {str(last)[:200]}")


def clean(sql):
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.M).strip()


def make_sql(question):
    prompt = f"""You write SQLite queries for a Bengaluru restaurants database.

Tables:
{SCHEMA}

Rules:
- Return ONLY one SQL query. No explanation, no markdown.
- Use only SELECT.
- restaurants has one row per restaurant. rate can be NULL (unrated).
- Cuisines are in restaurant_cuisines. Join on restaurant_id.
- When ranking by average rating, only include groups with at least 30 restaurants.
- Add LIMIT 20 unless the question asks otherwise.

Question: {question}"""
    return clean(ask_llm(prompt))


def explain(question, sql, result):
    prompt = f"""Question: {question}
SQL used: {sql}
Result:
{result.head(20).to_string(index=False)}

Answer the question in 1 to 3 plain sentences using only this result. Do not add facts."""
    return ask_llm(prompt).strip()


def ask(question, max_fixes=2):
    sql = make_sql(question)
    result = run_sql(sql)
    fixes = 0
    while not isinstance(result, pd.DataFrame) and fixes < max_fixes:
        fixes += 1
        fix = f"""This SQLite query failed.
Schema:
{SCHEMA}
Question: {question}
Query: {sql}
Error: {result}
Return ONLY the corrected SQL query."""
        sql = clean(ask_llm(fix))
        result = run_sql(sql)
    if not isinstance(result, pd.DataFrame):
        return sql, None, "Sorry, I could not answer that question."
    return sql, result, explain(question, sql, result)


st.write("Try one:")
examples = [
    "Which 5 areas have the most restaurants?",
    "Which cuisines have the highest average rating among cuisines with at least 100 restaurants?",
    "How many restaurants offer online ordering?",
]
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        st.session_state["q"] = ex

question = st.text_input("Your question", key="q")
if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Thinking..."):
        try:
            sql, result, answer = ask(question.strip())
        except Exception as e:
            st.error(str(e))
            st.stop()
    st.subheader("Answer")
    st.write(answer)
    if result is not None:
        st.dataframe(result, use_container_width=True)
    with st.expander("SQL the AI wrote"):
        st.code(sql, language="sql")
