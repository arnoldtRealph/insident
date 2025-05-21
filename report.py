import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pytz
from matplotlib.ticker import MaxNLocator
import uuid
from github import Github
import base64
import os

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Set page config
st.set_page_config(page_title="Insident Verslag", layout="wide")

# Custom CSS for enhanced professional styling and mobile responsiveness
st.markdown("""
    <style>
        /* General layout */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #212529;
            text-align: center;
        }
        [data-baseweb="baseweb"] {
            background-color: #f8f9fa !important;
        }

        /* Dark mode adjustments */
        [data-theme="dark"] .stApp, [data-theme="dark"] [data-baseweb="baseweb"] {
            background-color: #212529 !important;
            color: #e9ecef !important;
        }
        [data-theme="dark"] .main .block-container {
            background-color: #343a40 !important;
            color: #e9ecef !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        [data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText, 
        [data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 {
            color: #e9ecef !important;
        }

        /* Main content */
        .main .block-container {
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
            transition: box-shadow 0.3s ease;
        }
        .main .block-container:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }

        /* Headers */
        h1 {
            color: #003087;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
            letter-spacing: 0.02em;
        }
        h2 {
            color: #003087;
            font-size: 1.8rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 0.5rem;
            text-align: center;
        }
        h3 {
            color: #003087;
            font-size: 1.4rem;
            font-weight: 500;
            margin-bottom: 1rem;
            text-align: center;
        }

        /* Input labels */
        .input-label {
            color: #003087;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            display: block;
            text-align: center;
        }
        [data-theme="dark"] .input-label {
            color: #e9ecef !important;
        }

        /* Buttons */
        .stButton>button, .stDownloadButton>button {
            background-color: #003087;
            color: #ffffff !important;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            max-width: 200px;
            width: 100%;
            margin: 0.5rem auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            display: block;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #00205b;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .stButton>button:active, .stDownloadButton>button:active {
            background-color: #001a4d;
        }
        .stButton>button:disabled, .stDownloadButton>button:disabled {
            background-color: #6c757d;
            color: #ced4da !important;
            box-shadow: none;
        }

        /* Download button specific */
        .stDownloadButton>button {
            background-color: #007bff;
        }
        .stDownloadButton>button:hover {
            background-color: #0056b3;
        }
        .stDownloadButton>button:active {
            background-color: #004085;
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow-x: auto;
            background-color: #ffffff;
            max-width: 100%;
            margin: 0 auto;
        }
        .stDataFrame table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        .stDataFrame th {
            background-color: #e9ecef;
            color: #003087;
            font-weight: 600;
            padding: 0.75rem;
            text-align: left;
            font-size: 0.95rem;
            border-bottom: 2px solid #dee2e6;
        }
        [data-theme="dark"] .stDataFrame th {
            background-color: #495057;
            color: #e9ecef;
            border-bottom: 2px solid #6c757d;
        }
        .stDataFrame td {
            padding: 0.75rem;
            border-bottom: 1px solid #dee2e6;
            color: #212529;
            font-size: 0.9rem;
        }
        [data-theme="dark"] .stDataFrame td {
            color: #e9ecef;
            border-bottom: 1px solid #6c757d;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        [data-theme="dark"] .stDataFrame tr:nth-child(even) {
            background-color: #343a40;
        }
        .stDataFrame tr:hover {
            background-color: #e9ecef;
        }
        [data-theme="dark"] .stDataFrame tr:hover {
            background-color: #495057;
        }

        /* Selectbox (dropdowns) */
        .stSelectbox {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 0.5rem;
            font-size: 0.95rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 400px;
            width: 100%;
            margin: 0.5rem auto;
            display: block;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        [data-theme="dark"] .stSelectbox {
            background-color: #495057;
            border: 1px solid #6c757d;
            color: #e9ecef;
        }
        .stSelectbox:hover {
            border-color: #003087;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        [data-theme="dark"] .stSelectbox:hover {
            border-color: #e9ecef;
        }
        .stSelectbox > div > div {
            min-height: 40px;
        }

        /* Text area */
        .stTextArea {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 0.5rem;
            font-size: 0.95rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 400px;
            width: 100%;
            margin: 0.5rem auto;
            display: block;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        [data-theme="dark"] .stTextArea {
            background-color: #495057;
            border: 1px solid #6c757d;
            color: #e9ecef;
        }
        .stTextArea:hover {
            border-color: #003087;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        [data-theme="dark"] .stTextArea:hover {
            border-color: #e9ecef;
        }

        /* Text and labels */
        .stMarkdown, .stText {
            color: #212529;
            font-size: 0.95rem;
            text-align: center;
        }
        [data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText {
            color: #e9ecef;
        }
        .stAlert {
            border-radius: 8px;
            font-size: 0.95rem;
            padding: 0.75rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }

        /* Tabs */
        .stTabs {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e9ecef;
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            font-size: 0.95rem;
            color: #003087;
            margin-right: 0.5rem;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #dee2e6;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #003087;
            color: #ffffff;
            font-weight: 600;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"] {
            background-color: #343a40;
            color: #e9ecef;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"]:hover {
            background-color: #495057;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #007bff;
            color: #ffffff;
        }

        /* Charts */
        .stPyplot {
            border-radius: 8px;
            padding: 0.75rem;
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        [data-theme="dark"] .stPyplot {
            background-color: #343a40;
        }

        /* Separator */
        .custom-divider {
            border-top: 3px solid #dee2e6;
            margin: 2rem auto;
            max-width: 800px;
            border-radius: 2px;
        }
        [data-theme="dark"] .custom-divider {
            border-top: 3px solid #6c757d;
        }

        /* Pagination form */
        .pagination-form {
            display: flex;
            justify-content: center;
            align-items: center;
            max-width: 600px;
            margin: 1.5rem auto;
        }
        .pagination-form .stForm {
            display: flex;
            justify-content: center;
            width: 100%;
            gap: 0.5rem;
        }

        /* Notification container */
        .notification-container {
            position: fixed;
            top: 1rem;
            right: 1rem;
            width: 280px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border-radius: 10px;
            }
            h1 {
                font-size: 2rem;
            }
            h2 {
                font-size: 1.6rem;
                margin: 1.25rem 0 0.75rem;
            }
            h3 {
                font-size: 1.3rem;
                margin-bottom: 0.75rem;
            }
            .input-label {
                font-size: 1rem;
            }
            .stButton>button, .stDownloadButton>button {
                padding: 0.6rem 1.2rem;
                font-size: 0.9rem;
                max-width: 180px;
                border-radius: 6px;
            }
            .stSelectbox {
                font-size: 0.9rem;
                padding: 0.4rem;
                max-width: 90%;
                border-radius: 6px;
                min-height: 38px;
            }
            .stTextArea {
                font-size: 0.9rem;
                padding: 0.4rem;
                max-width: 90%;
                border-radius: 6px;
                min-height: 100px;
            }
            .stDataFrame {
                max-width: 100%;
                font-size: 0.85rem;
            }
            .stDataFrame th, .stDataFrame td {
                padding: 0.6rem;
            }
            .stPyplot {
                max-width: 100%;
            }
            .stAlert {
                max-width: 95%;
                font-size: 0.85rem;
                padding: 0.6rem;
            }
            .stTabs {
                flex-wrap: wrap;
                justify-content: flex-start;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 0.6rem 1.2rem;
                font-size: 0.9rem;
                margin-bottom: 0.4rem;
                border-radius: 6px;
                flex: 1 1 auto;
                text-align: center;
            }
            .custom-divider {
                border-top: 2px solid #dee2e6;
                margin: 1.5rem auto;
                max-width: 95%;
            }
            [data-theme="dark"] .custom-divider {
                border-top: 2px solid #6c757d;
            }
            .pagination-form {
                max-width: 95%;
                flex-direction: column;
                gap: 0.4rem;
            }
            .pagination-form .stForm {
                flex-direction: column;
                align-items: center;
            }
            .pagination-form .stSelectbox {
                max-width: 180px;
            }
            .notification-container {
                width: 90%;
                right: 0.5rem;
            }
        }

        @media (max-width: 480px) {
            .main .block-container {
                padding: 1rem;
                margin-bottom: 1rem;
            }
            h1 {
                font-size: 1.8rem;
            }
            h2 {
                font-size: 1.4rem;
            }
            h3 {
                font-size: 1.2rem;
            }
            .input-label {
                font-size: 0.9rem;
            }
            .stButton>button, .stDownloadButton>button {
                padding: 0.5rem 1rem;
                font-size: 0.85rem;
                max-width: 160px;
            }
            .stSelectbox {
                font-size: 0.85rem;
                padding: 0.3rem;
                max-width: 100%;
                min-height: 36px;
            }
            .stTextArea {
                font-size: 0.85rem;
                padding: 0.3rem;
                max-width: 100%;
                min-height: 80px;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 0.5rem 1rem;
                font-size: 0.85rem;
            }
            .notification-container {
                width: 95%;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Load and preprocess learner data
@st.cache_data
def load_learner_data():
    df = pd.read_csv("learner_list.csv")
    df.columns = df.columns.str.strip()
    df['Learner_Full_Name'] = df['Leerder van'].fillna('') + ' ' + df['Leerner se naam'].fillna('')
    df['Learner_Full_Name'] = df['Learner_Full_Name'].str.strip()
    df = df.rename(columns={
        'klasgroep': 'Class',
        'Opvoeder betrokke': 'Teacher',
        'Wat het gebeur': 'Incident',
        'Kategorie': 'Category',
        'Kommentaar': 'Comment'
    })
    df['Learner_Full_Name'] = df['Learner_Full_Name'].replace('', 'Onbekend')
    df['Class'] = df['Class'].fillna('Onbekend')
    df['Teacher'] = df['Teacher'].fillna('Onbekend')
    df['Incident'] = df['Incident'].fillna('Onbekend')
    df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
    df['Comment'] = df['Comment'].fillna('Geen Kommentaar')
    np.random.seed(42)
    start_date = datetime(2024, 1, 1)
    date_range = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, size=len(df))]
    df['Date'] = pd.to_datetime(date_range).date
    return df

# Load or initialize incident log
def load_incident_log():
    try:
        if os.path.exists("incident_log.csv") and os.path.getsize("incident_log.csv") > 0:
            df = pd.read_csv("incident_log.csv")
            if 'Learner_Name' in df.columns and 'Learner_Full_Name' not in df.columns:
                df = df.rename(columns={'Learner_Name': 'Learner_Full_Name'})
            df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
            df['Class'] = df['Class'].fillna('Onbekend').astype(str)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            return df
        else:
            st.write("incident_log.csv is empty or does not exist.")
            return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        st.write(f"Error loading incident_log.csv: {e}")
        return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log and push to GitHub
def save_incident(learner_full_name, class_, teacher, incident, category, comment):
    incident_log = load_incident_log()
    sa_tz = pytz.timezone('Africa/Johannesburg')
    try:
        category = str(int(float(category)))
    except ValueError:
        category = '1'
    new_incident = pd.DataFrame({
        'Learner_Full_Name': [learner_full_name],
        'Class': [class_],
        'Teacher': [teacher],
        'Incident': [incident],
        'Category': [category],
        'Comment': [comment],
        'Date': [datetime.now(sa_tz).date()]
    })
    incident_log = pd.concat([incident_log, new_incident], ignore_index=True)
    incident_log.to_csv("incident_log.csv", index=False)

    # Push to GitHub
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("arnoldtRealph/insident")
        with open("incident_log.csv", "rb") as file:
            content = file.read()
        repo_path = "incident_log.csv"
        try:
            contents = repo.get_contents(repo_path, ref="master")
            repo.update_file(
                path=repo_path,
                message="Updated incident_log.csv with new incident",
                content=content,
                sha=contents.sha,
                branch="master"
            )
        except:
            repo.create_file(
                path=repo_path,
                message="Created incident_log.csv with new incident",
                content=content,
                branch="master"
            )
    except Exception as e:
        st.error(f"Kon nie na GitHub stoot nie: {e}")

    return incident_log

# Clear a single incident and push to GitHub
def clear_incident(index):
    incident_log = load_incident_log()
    if index in incident_log.index:
        incident_log = incident_log.drop(index)
        incident_log.to_csv("incident_log.csv", index=False)

        # Push to GitHub
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("arnoldtRealph/insident")
            with open("incident_log.csv", "rb") as file:
                content = file.read()
            repo_path = "incident_log.csv"
            try:
                contents = repo.get_contents(repo_path, ref="master")
                repo.update_file(
                    path=repo_path,
                    message="Updated incident_log.csv after clearing incident",
                    content=content,
                    sha=contents.sha,
                    branch="master"
                )
            except:
                repo.create_file(
                    path=repo_path,
                    message="Created incident_log.csv after clearing incident",
                    content=content,
                    branch="master"
                )
        except Exception as e:
            st.error(f"Kon nie na GitHub stoot nie: {e}")

        return incident_log
    return incident_log

# Generate Word document
def generate_word_report(df):
    doc = Document()
    doc.add_heading('Insident Verslag', 0)

    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Full_Name': 'Leerder Naam',
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
            if col == 'Date':
                cells[i].text = row[col].strftime("%Y-%m-%d")
            else:
                cells[i].text = str(row[col])

    doc.add_heading('Insident Analise', level=1)
    
    # Bar chart: Incidents by Category
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts = df['Category'].value_counts().sort_index()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Kategorie', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=0, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Incident Type
    fig, ax = plt.subplots(figsize=(4, 2.5))
    incident_counts = df['Incident'].value_counts()
    sns.barplot(x=incident_counts.index, y=incident_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Tipe', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Insident', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Teacher
    fig, ax = plt.subplots(figsize=(4, 2.5))
    teacher_counts = df['Teacher'].value_counts()
    sns.barplot(x=teacher_counts.index, y=teacher_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Rapporterende Onderwyser', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Onderwyser', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Class
    fig, ax = plt.subplots(figsize=(4, 2.5))
    class_counts = df['Class'].value_counts()
    sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Klas', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Klas', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=9)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Pie chart: Incident Distribution
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=sns.color_palette('Blues'), textprops={'fontsize': 9})
    ax.set_title('Insident Verspreiding volgens Kategorie', pad=10, fontsize=12, weight='bold')
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Add High-Risk Learners section
    doc.add_heading('Leerders met Herhalende Insidente', level=1)
    incident_counts = df['Learner_Full_Name'].value_counts()
    high_risk_learners = incident_counts[incident_counts > 2].index
    high_risk_df = df[df['Learner_Full_Name'].isin(high_risk_learners)]

    if not high_risk_df.empty:
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Table Grid'
        headers = ['Leerder Naam', 'Klas', 'Insident', 'Kategorie', 'Datum']
        for i, header in enumerate(headers):
            table.cell(0, i).text = header

        for _, row in high_risk_df.iterrows():
            cells = table.add_row().cells
            cells[0].text = str(row['Learner_Full_Name'])
            cells[1].text = str(row['Class'])
            cells[2].text = str(row['Incident'])
            cells[3].text = str(row['Category'])
            cells[4].text = row['Date'].strftime("%Y-%m-%d")
    else:
        doc.add_paragraph("Geen leerders met herhalende insidente is tans gemerk nie.")

    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

# Generate learner-specific Word report
def generate_learner_report(df, learner_full_name, period, start_date, end_date):
    doc = Document()
    doc.add_heading(f'Insident Verslag vir {learner_full_name}', 0)
    doc.add_paragraph(f'Tydperk: {period}')
    doc.add_paragraph(f'Datum Reeks: {start_date.strftime("%Y-%m-%d")} tot {end_date.strftime("%Y-%m-%d")}')

    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Full_Name': 'Leerder Naam',
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
            if col == 'Date':
                cells[i].text = row[col].strftime("%Y-%m-%d")
            else:
                cells[i].text = str(row[col])

    if not df.empty:
        doc.add_heading('Insident Analise', level=1)
        fig, ax = plt.subplots(figsize=(4, 2.5))
        category_counts = df['Category'].value_counts().sort_index()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
        ax.set_xlabel('Kategorie', fontsize=10)
        ax.set_ylabel('Aantal', fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=0, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        plt.tight_layout(pad=1.0)
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        doc.add_picture(img_stream, width=Inches(3.5))

    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

# Load data
learner_df = load_learner_data()
incident_log = load_incident_log()

# Main content
with st.container():
    st.title("HOËRSKOOL SAUL DAMON")
    st.subheader("INSIDENT VERSLAG")

# Add CSS for top-right notifications
st.markdown("""
    <style>
        .notification-container {
            position: fixed;
            top: 1rem;
            right: 1rem;
            width: 280px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        [data-theme="dark"] .notification-container {
            background-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for sanction notifications
if 'sanction_popups' not in st.session_state:
    st.session_state.sanction_popups = {}

# Compute sanctions based on incident counts
if not incident_log.empty:
    tally_df = incident_log.pivot_table(
        index='Learner_Full_Name',
        columns='Category',
        values='Incident',
        aggfunc='count',
        fill_value=0
    )
    for cat in ['1', '2', '3', '4']:
        if cat not in tally_df.columns:
            tally_df[cat] = 0
    tally_df = tally_df[['1', '2', '3', '4']].reset_index()

    sanctions = []
    for _, row in tally_df.iterrows():
        learner = row['Learner_Full_Name']
        if row['1'] > 10:
            sanctions.append({
                'Learner': learner,
                'Category': '1',
                'Count': int(row['1']),
                'Sanction': 'Ouers moet afspraak maak met Mnr. Zealand; leerder mag nie skool bywoon voor ouers nie by die skool was nie.'
            })
        if row['2'] > 5:
            sanctions.append({
                'Learner': learner,
                'Category': '2',
                'Count': int(row['2']),
                'Sanction': 'Ouers moet afspraak maak met Mnr. Zealand; leerder mag nie skool bywoon voor ouers nie by die skool was nie.'
            })
        if row['3'] > 2:
            sanctions.append({
                'Learner': learner,
                'Category': '3',
                'Count': int(row['3']),
                'Sanction': 'Ouers moet afspraak maak met Mnr. Zealand; leerder mag nie skool bywoon voor ouers nie by die skool was nie.'
            })
        if row['4'] >= 1:
            sanctions.append({
                'Learner': learner,
                'Category': '4',
                'Count': int(row['4']),
                'Sanction': 'Leerder moet geskors word.'
            })

    sanctions_df = pd.DataFrame(sanctions)

    for _, row in sanctions_df.iterrows():
        key = f"{row['Learner']}_{row['Category']}"
        if key not in st.session_state.sanction_popups:
            st.session_state.sanction_popups[key] = True

    with st.container():
        st.markdown('<div class="notification-container">', unsafe_allow_html=True)
        any_notifications = False
        for _, row in sanctions_df.iterrows():
            key = f"{row['Learner']}_{row['Category']}"
            if st.session_state.sanction_popups.get(key, False):
                any_notifications = True
                st.markdown(
                    f"""
                    <div style='background-color: #ffe6e6; padding: 15px; border-radius: 8px; border: 2px solid #cc0000;'>
                        <h4 style='color: #cc0000; margin: 0;'>SANKSIEMELDING</h4>
                        <p style='color: #333; margin: 5px 0; font-size: 0.9rem;'>
                            Leerder <strong>{row['Learner']}</strong> het {row['Count']} Kategorie {row['Category']} insidente. 
                            Sanksie: {row['Sanction']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Opgelos", key=f"sanction_resolve_{key}"):
                    st.session_state.sanction_popups[key] = False
                    st.rerun()
        if not any_notifications:
            st.markdown(
                """
                <div style='background-color: #e6f3e6; padding: 15px; border-radius: 8px; border: 2px solid #28b463;'>
                    <p style='color: #333; margin: 0; font-size: 0.9rem;'>Geen aktiewe sanksiemeldings nie.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.header("Rapporteer Nuwe Insident")
    with st.container():
        st.markdown('<div class="input-label">Leerder Naam</div>', unsafe_allow_html=True)
        learner_full_name = st.selectbox("", options=['Kies'] + sorted(learner_df['Learner_Full_Name'].unique()), key="learner_full_name")
        
        st.markdown('<div class="input-label">Klas</div>', unsafe_allow_html=True)
        class_ = st.selectbox("", options=['Kies'] + sorted(learner_df['Class'].unique()), key="class")
        
        st.markdown('<div class="input-label">Onderwyser</div>', unsafe_allow_html=True)
        teacher = st.selectbox("", options=['Kies'] + sorted(learner_df['Teacher'].unique()), key="teacher")
        
        st.markdown('<div class="input-label">Insident</div>', unsafe_allow_html=True)
        incident = st.selectbox("", options=['Kies'] + sorted(learner_df['Incident'].unique()), key="incident")
        
        st.markdown('<div class="input-label">Kategorie</div>', unsafe_allow_html=True)
        category = st.selectbox("", options=['Kies'] + sorted(learner_df['Category'].unique(), key=lambda x: int(x)), key="category")
        
        st.markdown('<div class="input-label">Kommentaar</div>', unsafe_allow_html=True)
        comment = st.text_area("", placeholder="Tik hier...", key="comment")
        
        if st.button("Stoor Insident"):
            if learner_full_name != 'Kies' and class_ != 'Kies' and teacher != 'Kies' and incident != 'Kies' and category != 'Kies' and comment:
                incident_log = save_incident(learner_full_name, class_, teacher, incident, category, comment)
                st.success("Insident suksesvol gestoor!")
            else:
                st.error("Vul asseblief alle velde in en voer kommentaar in.")

    st.header("Genereer Leerder Verslag")
    with st.container():
        st.markdown('<div class="input-label">Kies Leerder vir Verslag</div>', unsafe_allow_html=True)
        learner_report_name = st.selectbox("", options=['Kies'] + sorted(incident_log['Learner_Full_Name'].unique()) if not incident_log.empty else ['Kies'], key="learner_report_name")
        
        st.markdown('<div class="input-label">Kies Tydperk</div>', unsafe_allow_html=True)
        report_period = st.selectbox("", options=['Daagliks', 'Weekliks', 'Maandelik', 'Kwartaalliks'], key="report_period")

        sa_tz = pytz.timezone('Africa/Johannesburg')
        today = datetime.now(sa_tz).date()

        if report_period == 'Daagliks':
            start_date = today
            end_date = today
        elif report_period == 'Weekliks':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif report_period == 'Maandelik':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        else:  # Kwartaalliks
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            end_date = (start_date + timedelta(days=92)).replace(day=1) - timedelta(days=1)

        st.write(f"Verslag Datum Reeks: {start_date.strftime('%Y-%m-%d')} tot {end_date.strftime('%Y-%m-%d')}")

        if st.button("Genereer Leerder Verslag"):
            if learner_report_name != 'Kies':
                learner_incidents = incident_log[
                    (incident_log['Learner_Full_Name'] == learner_report_name) &
                    (incident_log['Date'] >= start_date) &
                    (incident_log['Date'] <= end_date)
                ]
                if not learner_incidents.empty:
                    report_stream = generate_learner_report(learner_incidents, learner_report_name, report_period, start_date, end_date)
                    st.success(f"Verslag vir {learner_report_name} suksesvol gegenereer!")
                    st.download_button(
                        label="Laai Leerder Verslag af",
                        data=report_stream,
                        file_name=f"insident_verslag_{learner_report_name}_{report_period.lower()}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error(f"Geen insidente gevind vir {learner_report_name} in die geselekteerde tydperk.")
            else:
                st.error("Kies asseblief 'n leerder.")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.subheader("Insident Log")
    if not incident_log.empty:
        rows_per_page = 20
        total_rows = len(incident_log)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        if 'incident_log_page' not in st.session_state:
            st.session_state.incident_log_page = 1

        with st.form(key="pagination_form", clear_on_submit=False):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                submit_prev = st.form_submit_button("Vorige", disabled=(st.session_state.incident_log_page <= 1))
            with col2:
                page_options = list(range(1, total_pages + 1))
                selected_page = st.selectbox("Bladsy", options=page_options, index=st.session_state.incident_log_page - 1, key="incident_log_page_select")
            with col3:
                submit_next = st.form_submit_button("Volgende", disabled=(st.session_state.incident_log_page >= total_pages))

            if submit_prev:
                st.session_state.incident_log_page = max(1, st.session_state.incident_log_page - 1)
                st.rerun()
            if submit_next:
                st.session_state.incident_log_page = min(total_pages, st.session_state.incident_log_page + 1)
                st.rerun()
            if selected_page != st.session_state.incident_log_page:
                st.session_state.incident_log_page = selected_page
                st.rerun()

        start_idx = (st.session_state.incident_log_page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)

        display_df = incident_log.iloc[start_idx:end_idx].copy()
        display_df.index = range(start_idx + 1, min(end_idx + 1, total_rows + 1))

        st.dataframe(
            display_df,
            height=600,
            use_container_width=True,
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerder Naam", width="medium"),
                "Class": st.column_config.TextColumn("Klas", width="small"),
                "Teacher": st.column_config.TextColumn("Onderwyser", width="medium"),
                "Incident": st.column_config.TextColumn("Insident", width="medium"),
                "Category": st.column_config.TextColumn("Kategorie", width="small"),
                "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
                "Date": st.column_config.DateColumn("Datum", width="medium", format="YYYY-MM-DD")
            }
        )
        st.write(f"Wys {start_idx + 1} tot {end_idx} van {total_rows} insidente")

        st.download_button(
            label="Laai Verslag af as Word",
            data=generate_word_report(incident_log),
            file_name="insident_verslag.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.write("Verwyder 'n Insident")
        one_based_indices = list(range(1, total_rows + 1))
        st.markdown('<div class="input-label">Kies Insident om te Verwyder (deur Indeks)</div>', unsafe_allow_html=True)
        selected_display_index = st.selectbox("", options=one_based_indices, key="delete_index")
        if st.button("Verwyder Insident"):
            zero_based_index = selected_display_index - 1
            incident_log = clear_incident(zero_based_index)
            st.success(f"Insident {selected_display_index} suksesvol verwyder!")
            total_rows = len(incident_log)
            total_pages = (total_rows + rows_per_page - 1) // rows_per_page
            if st.session_state.incident_log_page > total_pages and total_pages > 0:
                st.session_state.incident_log_page = total_pages
            elif total_pages == 0:
                st.session_state.incident_log_page = 1
            st.rerun()
    else:
        st.write("Geen insidente in die log nie.")

    st.subheader("Vandag se Insidente")
    today = datetime.now(pytz.timezone('Africa/Johannesburg')).date()
    today_incidents = incident_log[incident_log['Date'] == today]
    if not today_incidents.empty:
        st.write(f"Totale Insidente Vandag: {len(today_incidents)}")

        st.write("Insidente volgens Kategorie")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        category_counts = today_incidents['Category'].value_counts().sort_index()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Kategorie (Vandag)', pad=10, fontsize=12, weight='bold')
        ax.set_xlabel('Kategorie', fontsize=10)
        ax.set_ylabel('Aantal', fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=0, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Tipe")
        fig, ax = plt.subplots(figsize=(10, 5))
        incident_counts = today_incidents['Incident'].value_counts()
        sns.barplot(x=incident_counts.index, y=incident_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Tipe (Vandag)', pad=8, fontsize=10, weight='bold')
        ax.set_xlabel('Insident', fontsize=8)
        ax.set_ylabel('Aantal', fontsize=8)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=45, labelsize=6)
        ax.tick_params(axis='y', labelsize=7)
        plt.tight_layout(pad=1.5)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Rapporterende Onderwyser")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        teacher_counts = today_incidents['Teacher'].value_counts()
        sns.barplot(x=teacher_counts.index, y=teacher_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Rapporterende Onderwyser (Vandag)', pad=10, fontsize=12, weight='bold')
        ax.set_xlabel('Onderwyser', fontsize=10)
        ax.set_ylabel('Aantal', fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=60, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Klas")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        class_counts = today_incidents['Class'].value_counts()
        sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Klas (Vandag)', pad=10, fontsize=12, weight='bold')
        ax.set_xlabel('Klas', fontsize=10)
        ax.set_ylabel('Aantal', fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=60, labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()
    else:
        st.write("Geen insidente vandag gerapporteer nie.")

    tab1, tab2, tab3, tab4 = st.tabs(["Gefiltreerde Data", "Weeklikse Opsomming", "Maandelikse Opsomming", "Kwartaallikse Opsomming"])

    with tab1:
        st.subheader("Gefiltreerde Data")
        st.markdown('<div class="input-label">Filter Leerder Naam</div>', unsafe_allow_html=True)
        learner_options = ['Alle'] + sorted(incident_log['Learner_Full_Name'].unique()) if not incident_log.empty else ['Alle']
        filter_learner = st.selectbox("", options=learner_options, key="filter_learner")
        
        st.markdown('<div class="input-label">Filter Klas</div>', unsafe_allow_html=True)
        if not incident_log.empty:
            class_options = incident_log['Class'].fillna('Onbekend').astype(str).unique()
            class_options = [x for x in class_options if x]
            class_options = sorted(class_options)
        else:
            class_options = []
        filter_class = st.selectbox("", options=['Alle'] + class_options, key="filter_class")
        
        st.markdown('<div class="input-label">Filter Onderwyser</div>', unsafe_allow_html=True)
        teacher_options = ['Alle'] + sorted(incident_log['Teacher'].unique()) if not incident_log.empty else ['Alle']
        filter_teacher = st.selectbox("", options=teacher_options, key="filter_teacher")
        
        st.markdown('<div class="input-label">Filter Insident</div>', unsafe_allow_html=True)
        incident_options = ['Alle'] + sorted(incident_log['Incident'].unique()) if not incident_log.empty else ['Alle']
        filter_incident = st.selectbox("", options=incident_options, key="filter_incident")
        
        st.markdown('<div class="input-label">Filter Kategorie</div>', unsafe_allow_html=True)
        category_options = ['Alle'] + sorted(incident_log['Category'].unique(), key=lambda x: int(x)) if not incident_log.empty else ['Alle']
        filter_category = st.selectbox("", options=category_options, key="filter_category")
        
        filtered_df = incident_log.copy()
        if filter_learner != 'Alle':
            filtered_df = filtered_df[filtered_df['Learner_Full_Name'] == filter_learner]
        if filter_class != 'Alle':
            filtered_df = filtered_df[filtered_df['Class'] == filter_class]
        if filter_teacher != 'Alle':
            filtered_df = filtered_df[filtered_df['Teacher'] == filter_teacher]
        if filter_incident != 'Alle':
            filtered_df = filtered_df[filtered_df['Incident'] == filter_incident]
        if filter_category != 'Alle':
            filtered_df = filtered_df[filtered_df['Category'] == filter_category]
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=300,
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerder Naam", width="medium"),
                "Class": st.column_config.TextColumn("Klas", width="small"),
                "Teacher": st.column_config.TextColumn("Onderwyser", width="medium"),
                "Incident": st.column_config.TextColumn("Insident", width="medium"),
                "Category": st.column_config.TextColumn("Kategorie", width="small"),
                "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
                "Date": st.column_config.DateColumn("Datum", width="medium", format="YYYY-MM-DD")
            }
        )
        st.write(f"Totale Insidente: {len(filtered_df)}")

    with tab2:
        st.subheader("Weeklikse Opsomming")
        if not incident_log.empty:
            incident_log_dt = incident_log.copy()
            incident_log_dt['Date'] = pd.to_datetime(incident_log_dt['Date'])
            weekly_summary = incident_log_dt.groupby([pd.Grouper(key='Date', freq='W-MON'), 'Category']).size().unstack(fill_value=0)
            weekly_summary.index = weekly_summary.index.strftime('%Y-%m-%d')
            weekly_summary['Totaal'] = weekly_summary.sum(axis=1)
            weekly_summary = weekly_summary.reset_index().rename(columns={'Date': 'Week Begin (Maandag)'})
            st.dataframe(
                weekly_summary,
                use_container_width=True,
                height=300,
                column_config={
                    'Week Begin (Maandag)': st.column_config.TextColumn("Week Begin (Maandag)", width="medium"),
                    'Totaal': st.column_config.NumberColumn("Totaal Insidente", width="small")
                }
            )
            st.write("Totale Insidente per Week:")
            for idx, row in weekly_summary.iterrows():
                st.write(f"Week van {row['Week Begin (Maandag)']}: {int(row['Totaal'])} insidente")
            
            fig, ax = plt.subplots(figsize=(8, 4))
            weekly_summary.set_index('Week Begin (Maandag)')[weekly_summary.columns[1:-1]].plot(
                kind='bar', 
                stacked=True, 
                ax=ax, 
                color=sns.color_palette('tab10', n_colors=len(weekly_summary.columns[1:-1]))
            )
            ax.set_title('Weeklikse Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
            ax.set_xlabel('Week Begin (Maandag)', fontsize=10)
            ax.set_ylabel('Aantal Insidente', fontsize=10)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.legend(title='Kategorie', fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab3:
        st.subheader("Maandelikse Opsomming")
        if not incident_log.empty:
            incident_log_dt = incident_log.copy()
            incident_log_dt['Date'] = pd.to_datetime(incident_log_dt['Date'])
            monthly_summary = incident_log_dt.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
            monthly_summary.index = monthly_summary.index.strftime('%Y-%m')
            st.dataframe(monthly_summary, use_container_width=True, height=300)
            fig, ax = plt.subplots(figsize=(8, 4))
            monthly_summary.plot(
                kind='bar', 
                stacked=True, 
                ax=ax, 
                color=sns.color_palette('tab10', n_colors=len(monthly_summary.columns))
            )
            ax.set_title('Maandelikse Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
            ax.set_xlabel('Maand', fontsize=10)
            ax.set_ylabel('Aantal Insidente', fontsize=10)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.legend(title='Kategorie', fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab4:
        st.subheader("Kwartaallikse Opsomming")
        if not incident_log.empty:
            incident_log_dt = incident_log.copy()
            incident_log_dt['Date'] = pd.to_datetime(incident_log_dt['Date'])
            quarterly_summary = incident_log_dt.groupby([pd.Grouper(key='Date', freq='Q'), 'Category']).size().unstack(fill_value=0)
            quarterly_summary.index = quarterly_summary.index.map(
                lambda x: f"{x.year}-Q{(x.month-1)//3 + 1}"
            )
            st.dataframe(quarterly_summary, use_container_width=True, height=300)
            fig, ax = plt.subplots(figsize=(8, 4))
            quarterly_summary.plot(
                kind='bar', 
                stacked=True, 
                ax=ax, 
                color=sns.color_palette('tab10', n_colors=len(quarterly_summary.columns))
            )
            ax.set_title('Kwartaallikse Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
            ax.set_xlabel('Kwartaal', fontsize=10)
            ax.set_ylabel('Aantal Insidente', fontsize=10)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.legend(title='Kategorie', fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    st.subheader("Leerders met Herhalende Insidente")
    incident_counts = incident_log['Learner_Full_Name'].value_counts()
    high_risk_learners = incident_counts[incident_counts > 2].index
    high_risk_df = incident_log[incident_log['Learner_Full_Name'].isin(high_risk_learners)]

    if not high_risk_df.empty:
        st.markdown("Hieronder is leerders met meer as twee insidente, aangedui as areas van kommer.")
        styled_html = """
        <style>
            .red-table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                background-color: #ffcccc;
                color: #000;
                font-size: 15px;
            }
            .red-table th {
                background-color: #cc0000;
                color: white;
                padding: 10px;
            }
            .red-table td {
                padding: 10px;
                border: 1px solid #990000;
            }
            .red-table tr:hover {
                background-color: #ff9999;
            }
        </style>
        """
        table_html = "<table class='red-table'><thead><tr>"
        for col in ['Leerder Naam', 'Klas', 'Insident', 'Kategorie', 'Datum']:
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"
        for _, row in high_risk_df.iterrows():
            table_html += "<tr>"
            table_html += f"<td>{row['Learner_Full_Name']}</td>"
            table_html += f"<td>{row['Class']}</td>"
            table_html += f"<td>{row['Incident']}</td>"
            table_html += f"<td>{row['Category']}</td>"
            table_html += f"<td>{row['Date']}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        st.markdown(styled_html + table_html, unsafe_allow_html=True)
    else:
        st.info("Geen leerders met herhalende insidente is tans gemerk nie.")
