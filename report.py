import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# Set page config
st.set_page_config(page_title="Insident Spoorder", layout="wide")

# Load and preprocess learner data
@st.cache_data
def load_learner_data():
    df = pd.read_csv("learner_list.csv")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'Leerner se naam': 'Learner_Name',
        'klasgroep': 'Class',
        'Opvoeder betrokke': 'Teacher',
        'Wat het gebeur': 'Incident',
        'Kategorie': 'Category',
        'Kommentaar': 'Comment'
    })
    df['Learner_Name'] = df['Learner_Name'].fillna('Onbekend')
    df['Class'] = df['Class'].fillna('Onbekend')
    df['Teacher'] = df['Teacher'].fillna('Onbekend')
    df['Incident'] = df['Incident'].fillna('Onbekend')
    df['Category'] = df['Category'].astype(str).fillna('Onbekend')
    df['Comment'] = df['Comment'].fillna('Geen Kommentaar')
    # Add mock date for existing data
    np.random.seed(42)
    start_date = datetime(2024, 1, 1)
    date_range = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, size=len(df))]
    df['Date'] = pd.to_datetime(date_range)
    return df

# Load or initialize incident log
def load_incident_log():
    try:
        df = pd.read_csv("incident_log.csv")
        df['Category'] = df['Category'].astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date is datetime
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Learner_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log
def save_incident(learner_name, class_, teacher, incident, category, comment):
    incident_log = load_incident_log()
    new_incident = pd.DataFrame({
        'Learner_Name': [learner_name],
        'Class': [class_],
        'Teacher': [teacher],
        'Incident': [incident],
        'Category': [category],
        'Comment': [comment],
        'Date': [datetime.now()]
    })
    incident_log = pd.concat([incident_log, new_incident], ignore_index=True)
    incident_log.to_csv("incident_log.csv", index=False)
    return incident_log

# Clear a single incident
def clear_incident(index):
    incident_log = load_incident_log()
    if index in incident_log.index:
        incident_log = incident_log.drop(index)
        incident_log.to_csv("incident_log.csv", index=False)
        return incident_log
    return incident_log

# Generate Word document
def generate_word_report(df):
    doc = Document()
    doc.add_heading('Insident Verslag', 0)

    # Add table
    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Name': 'Leerling Naam',
            'Class': 'Klas',
            'Teacher': 'Onderwyser',
            'Incident': 'Insident',
            'Category': 'Kategorie',
            'Comment': 'Kommentaar',
            'Date': 'Datum'
        }.get(col, col)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            cells[i].text = str(row[col])

    # Add charts
    doc.add_heading('Insident Analise', level=1)

    # Bar chart: Incidents by Category
    fig, ax = plt.subplots(figsize=(5, 3))
    category_counts = df['Category'].value_counts()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Kategorie')
    ax.set_xlabel('Kategorie')
    ax.set_ylabel('Aantal')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100)
    plt.close()
    doc.add_picture(img_stream, width=Inches(4))

    # Bar chart: Incidents by Incident Type
    fig, ax = plt.subplots(figsize=(5, 3))
    incident_counts = df['Incident'].value_counts()
    sns.barplot(x=incident_counts.index, y=incident_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Tipe')
    ax.set_xlabel('Insident')
    ax.set_ylabel('Aantal')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100)
    plt.close()
    doc.add_picture(img_stream, width=Inches(4))

    # Bar chart: Incidents by Teacher
    fig, ax = plt.subplots(figsize=(5, 3))
    teacher_counts = df['Teacher'].value_counts()
    sns.barplot(x=teacher_counts.index, y=teacher_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Rapporterende Onderwyser')
    ax.set_xlabel('Onderwyser')
    ax.set_ylabel('Aantal')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100)
    plt.close()
    doc.add_picture(img_stream, width=Inches(4))

    # Bar chart: Incidents by Class
    fig, ax = plt.subplots(figsize=(5, 3))
    class_counts = df['Class'].value_counts()
    sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Klas')
    ax.set_xlabel('Klas')
    ax.set_ylabel('Aantal')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100)
    plt.close()
    doc.add_picture(img_stream, width=Inches(4))

    # Pie chart: Incident Distribution
    fig, ax = plt.subplots(figsize=(5, 3))
    category_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=sns.color_palette('muted'))
    ax.set_title('Insident Verspreiding volgens Kategorie')
    plt.tight_layout()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100)
    plt.close()
    doc.add_picture(img_stream, width=Inches(4))

    # Save document to stream
    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

# Load data
learner_df = load_learner_data()
incident_log = load_incident_log()

# Sidebar for incident input
st.sidebar.header("Rapporteer Nuwe Insident")
learner_name = st.sidebar.selectbox("Leerling Naam", options=['Kies'] + sorted(learner_df['Learner_Name'].unique()))
class_ = st.sidebar.selectbox("Klas", options=['Kies'] + sorted(learner_df['Class'].unique()))
teacher = st.sidebar.selectbox("Onderwyser", options=['Kies'] + sorted(learner_df['Teacher'].unique()))
incident = st.sidebar.selectbox("Insident", options=['Kies'] + sorted(learner_df['Incident'].unique()))
category = st.sidebar.selectbox("Kategorie", options=['Kies'] + sorted(learner_df['Category'].unique(), key=lambda x: str(x)))
comment = st.sidebar.text_area("Kommentaar", placeholder="Voer insident kommentaar in")

# Save button
if st.sidebar.button("Stoor Insident"):
    if learner_name != 'Kies' and class_ != 'Kies' and teacher != 'Kies' and incident != 'Kies' and category != 'Kies' and comment:
        incident_log = save_incident(learner_name, class_, teacher, incident, category, comment)
        st.sidebar.success("Insident suksesvol gestoor!")
    else:
        st.sidebar.error("Vul asseblief alle velde in en voer kommentaar in.")

# Main content
st.title("HOËRSKOOL SAUL DAMON")
st.subheader("INSIDENT VERSLAG")

# Incident Log
st.subheader("Insident Log")
st.dataframe(incident_log)
if not incident_log.empty:
    st.download_button(
        label="Laai Verslag af as Word",
        data=generate_word_report(incident_log),
        file_name="insident_verslag.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    st.write("Verwyder 'n Insident")
    incident_index = st.selectbox("Kies Insident om te Verwyder (deur Indeks)", options=incident_log.index)
    if st.button("Verwyder Insident"):
        incident_log = clear_incident(incident_index)
        st.success(f"Insident {incident_index} suksesvol verwyder!")
        st.rerun()

# Daily incident charts
st.subheader("Vandag se Insidente")
today = datetime.now().date()
today_incidents = incident_log[incident_log['Date'].dt.date == today]
if not today_incidents.empty:
    st.write(f"Totale Insidente Vandag: {len(today_incidents)}")

    # Bar chart: Incidents by Category
    st.write("Insidente volgens Kategorie")
    fig, ax = plt.subplots(figsize=(6, 3))
    today_incidents['Category'].value_counts().plot(kind='bar', ax=ax, color=sns.color_palette('muted')[0])
    ax.set_title("Insidente volgens Kategorie (Vandag)")
    ax.set_xlabel("Kategorie")
    ax.set_ylabel("Aantal")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()

    # Bar chart: Incidents by Incident Type
    st.write("Insidente volgens Tipe")
    fig, ax = plt.subplots(figsize=(6, 3))
    today_incidents['Incident'].value_counts().plot(kind='bar', ax=ax, color=sns.color_palette('muted')[1])
    ax.set_title("Insidente volgens Tipe (Vandag)")
    ax.set_xlabel("Insident")
    ax.set_ylabel("Aantal")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()

    # Bar chart: Incidents by Teacher
    st.write("Insidente volgens Rapporterende Onderwyser")
    fig, ax = plt.subplots(figsize=(6, 3))
    today_incidents['Teacher'].value_counts().plot(kind='bar', ax=ax, color=sns.color_palette('muted')[2])
    ax.set_title("Insidente volgens Rapporterende Onderwyser (Vandag)")
    ax.set_xlabel("Onderwyser")
    ax.set_ylabel("Aantal")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()

    # Bar chart: Incidents by Class
    st.write("Insidente volgens Klas")
    fig, ax = plt.subplots(figsize=(6, 3))
    today_incidents['Class'].value_counts().plot(kind='bar', ax=ax, color=sns.color_palette('muted')[3])
    ax.set_title("Insidente volgens Klas (Vandag)")
    ax.set_xlabel("Klas")
    ax.set_ylabel("Aantal")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()
else:
    st.write("Geen insidente vandag gerapporteer nie.")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Gefiltreerde Data", "Weeklikse Opsomming", "Maandelikse Opsomming", "Kwartaallikse Opsomming"])

with tab1:
    st.subheader("Gefiltreerde Data")
    filter_learner = st.selectbox("Filter Leerling Naam", options=['Alle'] + sorted(incident_log['Learner_Name'].unique()))
    filter_class = st.selectbox("Filter Klas", options=['Alle'] + sorted(incident_log['Class'].unique()))
    filter_teacher = st.selectbox("Filter Onderwyser", options=['Alle'] + sorted(incident_log['Teacher'].unique()))
    filter_incident = st.selectbox("Filter Insident", options=['Alle'] + sorted(incident_log['Incident'].unique()))
    filter_category = st.selectbox("Filter Kategorie", options=['Alle'] + sorted(incident_log['Category'].unique(), key=lambda x: str(x)))
    filtered_df = incident_log.copy()
    if filter_learner != 'Alle':
        filtered_df = filtered_df[filtered_df['Learner_Name'] == filter_learner]
    if filter_class != 'Alle':
        filtered_df = filtered_df[filtered_df['Class'] == filter_class]
    if filter_teacher != 'Alle':
        filtered_df = filtered_df[filtered_df['Teacher'] == filter_teacher]
    if filter_incident != 'Alle':
        filtered_df = filtered_df[filtered_df['Incident'] == filter_incident]
    if filter_category != 'Alle':
        filtered_df = filtered_df[filtered_df['Category'] == filter_category]
    st.dataframe(filtered_df)
    st.write(f"Totale Insidente: {len(filtered_df)}")

with tab2:
    st.subheader("Weeklikse Opsomming")
    if not incident_log.empty:
        weekly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='W'), 'Category']).size().unstack(fill_value=0)
        st.dataframe(weekly_summary)
        st.bar_chart(weekly_summary)
    else:
        st.write("Geen insidente om te wys nie.")

with tab3:
    st.subheader("Maandelikse Opsomming")
    if not incident_log.empty:
        monthly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
        st.dataframe(monthly_summary)
        st.bar_chart(monthly_summary)
    else:
        st.write("Geen insidente om te wys nie.")

with tab4:
    st.subheader("Kwartaallikse Opsomming")
    if not incident_log.empty:
        quarterly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='Q'), 'Category']).size().unstack(fill_value=0)
        st.dataframe(quarterly_summary)
        st.bar_chart(quarterly_summary)
    else:
        st.write("Geen insidente om te wys nie.")