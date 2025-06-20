import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

st.set_page_config(page_title="Life in Weeks", layout="wide")
st.title("🧬 Life in Weeks")

if "events" not in st.session_state:
    st.session_state.events = []

if "event_types" not in st.session_state:
    st.session_state.event_types = ["Birthday", "Personal", "International"]

if "type_colors" not in st.session_state:
    st.session_state.type_colors = {
        "Birthday": "#4da6ff",
        "Personal": "#90ee90",
        "International": "#ffa500"
    }

# Sidebar Info
st.sidebar.header("🧑 Your Info")
dob = st.sidebar.date_input("Date of Birth (YYYY-MM-DD)", value=date(2007, 8, 1))
lifespan = st.sidebar.slider("Target Lifespan (Years)", 50, 100, 90)
buffer_years = st.sidebar.slider("Future Preview (Years)", 0, 10, 2)

today = date.today()
current_age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
weeks_lived = (today - dob).days // 7
total_weeks = lifespan * 52
weeks_left = total_weeks - weeks_lived
percent_lived = (weeks_lived / total_weeks) * 100

# Add Event
st.sidebar.header("⭐ Add Event")
with st.sidebar.expander("➕ Add Event"):
    event_date = st.date_input("Date (YYYY-MM-DD)", key="event_date_input")
    event_title = st.text_input("Title")
    event_type = st.selectbox("Type", st.session_state.event_types)
    if st.button("Save Event"):
        week_number = (event_date - dob).days // 7
        st.session_state.events.append({
            "date": event_date,
            "title": event_title,
            "type": event_type,
            "week": week_number
        })
        st.success("Event added!")

# Event List/Edit/Delete
st.sidebar.header("🔍 Manage Events")
search_query = st.sidebar.text_input("Search event")
matching_events = [e for e in st.session_state.events if search_query.lower() in e["title"].lower()]

for idx, ev in enumerate(matching_events):
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        edited_title = st.text_input("✏️", ev["title"], key=f"title_{idx}")
    with col2:
        new_age = st.number_input("Age", 0, lifespan, value=(ev["week"] // 52), key=f"age_{idx}")
    with col3:
        if st.button("❌", key=f"del_ev_{idx}"):
            st.session_state.events.remove(ev)
            st.rerun()
    if edited_title != ev["title"] or new_age != ev["week"] // 52:
        ev["title"] = edited_title
        ev["week"] = new_age * 52

# Life Summary
st.subheader("📊 Life Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Weeks Lived", f"{weeks_lived}")
col2.metric("Weeks Left", f"{weeks_left}")
col3.metric("Life Completed", f"{percent_lived:.2f}%")

# Calendar Grid with click
st.subheader("🗓️ Life Calendar")
display_years = current_age_years + buffer_years
cols = 52

selected_week = st.session_state.get("selected_week", None)
selected_title = ""

grid = []
for year in range(display_years):
    row = []
    for week_in_year in range(52):
        week = year * 52 + week_in_year
        color = "#d3d3d3"
        label = ""
        if week < weeks_lived:
            color = "#ff4d4d"
        for e in st.session_state.events:
            if week == e["week"]:
                color = st.session_state.type_colors.get(e["type"], "#dda0dd")
                label = e["title"]
                break
        row.append((week, color, label))
    grid.append((year, row))

for year, weeks in grid:
    with st.container():
        st.markdown(f"**Year {year}**")
        cols = st.columns(52)
        for idx, (week, color, label) in enumerate(weeks):
            with cols[idx]:
                if st.button(" ", key=f"week_{week}", help=label):
                    st.session_state.selected_week = week
                    st.session_state.selected_title = label
                st.markdown(f"""
                    <div style='width:12px;height:12px;border-radius:2px;background:{color}'></div>
                """, unsafe_allow_html=True)

# Display clicked week info
if st.session_state.get("selected_week") is not None:
    title = st.session_state.get("selected_title", "")
    if title:
        st.info(f"📅 **Week {st.session_state.selected_week}**: {title}")

# Event Legend
if st.session_state.events:
    st.markdown("### 🔵 Event Legend")
    for ev in st.session_state.events:
        col = st.session_state.type_colors.get(ev['type'], '#000000')
        st.markdown(f"<span style='color:{col}'>⬤</span> **{ev['title']}** ({ev['type']}) on `{ev['date']}` (Week {ev['week']})", unsafe_allow_html=True)

# Motivation
st.subheader("💡 Motivational Quote")
quotes = [
    "⏳ *“It’s not that we have a short time to live, but that we waste a lot of it.”* — Seneca",
    "🎯 *“Live as if you were to die tomorrow. Learn as if you were to live forever.”* — Gandhi",
    "🔥 *“You have 4,680 weeks. What will you do with them?”*",
    "🚀 *“You only live once, but if you do it right, once is enough.”* — Mae West",
    "📘 *“Don’t count the days, make the days count.”* — Muhammad Ali"
]
st.markdown(np.random.choice(quotes))

# Moved: Manage Event Types (now at the bottom)
st.sidebar.header("🗂️ Manage Event Types")
with st.sidebar.expander("➕ Add/Delete Types"):
    new_type = st.text_input("New Type")
    if st.button("Add Type"):
        if new_type and new_type not in st.session_state.event_types:
            st.session_state.event_types.append(new_type)
            st.session_state.type_colors[new_type] = "#dda0dd"
            st.success(f"Type '{new_type}' added.")
    st.markdown("#### Existing Types:")
    for i, t in enumerate(st.session_state.event_types):
        col1, col2 = st.columns([5, 1])
        col1.write(f"- {t}")
        if col2.button("❌", key=f"del_type_{i}"):
            st.session_state.event_types.remove(t)
            st.session_state.type_colors.pop(t, None)
            st.rerun()

# Color Picker
st.sidebar.header("🎨 Customize Colors")
with st.sidebar.expander("🎨 Color for Each Type"):
    for event_type in st.session_state.event_types:
        current_color = st.session_state.type_colors.get(event_type, "#cccccc")
        chosen_color = st.color_picker(f"{event_type}", value=current_color, key=f"color_{event_type}")
        st.session_state.type_colors[event_type] = chosen_color
