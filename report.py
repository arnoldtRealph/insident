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

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8

# Set page config
st.set_page_config(page_title="Insident Verslag", layout="wide")

# Custom CSS for professional styling, dark mode, and mobile optimization
st.markdown("""
    <style>
        /* General layout */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Arial', sans-serif;
        }
        [data-baseweb="baseweb"] {
            background-color: #f8f9fa !important;
        }

        /* Dark mode adjustments */
        [data-theme="dark"] .stApp, [data-theme="dark"] [data-baseweb="baseweb"] {
            background-color: #212529 !important;
        }
        [data-theme="dark"] .main .block-container {
            background-color: #343a40 !important;
            color: #f8f9fa !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        [data-theme="dark"] .sidebar .sidebar-content {
            background-color: #2c3034 !important;
            color: #f8f9fa !important;
            border-right: 1px solid #495057;
        }
        [data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText, [data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 {
            color: #f8f9fa !important;
        }

        /* Main content */
        .main .block-container {
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }

        /* Headers */
        h1 {
            color: #343a40;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-align: center;
        }
        h2 {
            color: #495057;
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        h3 {
            color: #495057;
            font-size: 1.2rem;
            font-weight: 500;
        }

        /* Input labels */
        .input-label {
            color: #495057;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 5px;
        }
        [data-theme="dark"] .input-label {
            color: #f8f9fa !important;
        }

        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #e9ecef;
            padding: 15px;
            border-right: 1px solid #dee2e6;
            width: 250px;
        }

        /* Buttons */
        .stButton>button {
            background-color: #28a745;
            color: #ffffff !important;
            border: none;
            border-radius: 4px;
            padding: 12px 18px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: background-color 0.2s;
            width: 100%;
            margin: 5px 0;
        }
        .stButton>button:hover {
            background-color: #218838;
            color: #ffffff !important;
        }
        .stButton>button:active {
            background-color: #1e7e34;
            color: #ffffff !important;
        }
        .stButton>button:disabled {
            background-color: #6c757d;
            color: #d3d3d3 !important;
        }

        /* Download button */
        .stDownloadButton>button {
            background-color: #007bff;
            color: #ffffff !important;
            border: none;
            border-radius: 4px;
            padding: 12px 18px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: background-color 0.2s;
            width: 100%;
            margin: 5px 0;
        }
        .stDownloadButton>button:hover {
            background-color: #0056b3;
            color: #ffffff !important;
        }
        .stDownloadButton>button:active {
            background-color: #004085;
            color: #ffffff !important;
        }
        .stDownloadButton>button:disabled {
            background-color: #6c757d;
            color: #d3d3d3 !important;
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            overflow-x: auto;
        }
        .stDataFrame table {
            width: 100%;
            border-collapse: collapse;
        }
        .stDataFrame th {
            background-color: #e9ecef;
            color: #343a40;
            font-weight: 600;
            padding: 8px;
            text-align: left;
            font-size: 0.85rem;
        }
        [data-theme="dark"] .stDataFrame th {
            background-color: #495057;
            color: #f8f9fa;
        }
        .stDataFrame td {
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
            color: #343a40;
            font-size: 0.85rem;
        }
        [data-theme="dark"] .stDataFrame td {
            color: #f8f9fa;
            border-bottom: 1px solid #495057;
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

        /* Sidebar inputs */
        .stSelectbox, .stTextArea {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px;
            font-size: 0.9rem;
        }
        [data-theme="dark"] .stSelectbox, [data-theme="dark"] .stTextArea {
            background-color: #343a40;
            border: 1px solid #6c757d;
            color: #f8f9fa;
        }
        .stSelectbox:hover, .stTextArea:hover {
            border-color: #28a745;
        }
        [data-theme="dark"] .stSelectbox:hover, [data-theme="dark"] .stTextArea:hover {
            border-color: #28a745;
        }

        /* Text and labels */
        .stMarkdown, .stText {
            color: #495057;
            font-size: 0.9rem;
        }
        [data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText {
            color: #f8f9fa;
        }
        .stAlert {
            border-radius: 4px;
            font-size: 0.9rem;
        }

        /* Mobile optimization */
        @media (max-width: 600px) {
            .main .block-container {
                padding: 10px;
                margin-bottom: 10px;
            }
            h1 {
                font-size: 1.8rem;
            }
            h2 {
                font-size: 1.3rem;
            }
            h3 {
                font-size: 1.1rem;
            }
            .input-label {
                font-size: 0.85rem;
            }
            .sidebar .sidebar-content {
                width: 100%;
                padding: 10px;
            }
            .stButton>button, .stDownloadButton>button {
                padding: 10px 15px;
                font-size: 0.85rem;
            }
            .stSelectbox, .stTextArea {
                font-size: 0.85rem;
                padding: 6px;
            }
            .stDataFrame th, .stDataFrame td {
                font-size: 0.8rem;
                padding: 6px;
            }
            .stPlotlyChart, .stPyplot {
                width: 100% !important;
                height: auto !important;
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
    df['Date'] = pd.to_datetime(date_range)
    return df

# Load or initialize incident log
def load_incident_log():
    try:
        df = pd.read_csv("incident_log.csv")
        if 'Learner_Name' in df.columns and 'Learner_Full_Name' not in df.columns:
            df = df.rename(columns={'Learner_Name': 'Learner_Full_Name'})
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        sa_tz = pytz.timezone('Africa/Johannesburg')
        df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert(sa_tz).dt.tz_localize(None)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log
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
        'Date': [datetime.now(sa_tz).replace(tzinfo=None)]
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
                cells[i].text = row[col].strftime("%Y-%m-%d %H:%M:%S")
            else:
                cells[i].text = str(row[col])

    doc.add_heading('Insident Analise', level=1)

    # Bar chart: Incidents by Category
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts = df['Category'].value_counts().sort_index()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Kategorie', pad=10, fontsize=10, weight='bold')
    ax.set_xlabel('Kategorie', fontsize=9)
    ax.set_ylabel('Aantal', fontsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=0, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Incident Type
    fig, ax = plt.subplots(figsize=(4, 2.5))
    incident_counts = df['Incident'].value_counts()
    sns.barplot(x=incident_counts.index, y=incident_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Tipe', pad=10, fontsize=10, weight='bold')
    ax.set_xlabel('Insident', fontsize=9)
    ax.set_ylabel('Aantal', fontsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Teacher
    fig, ax = plt.subplots(figsize=(4, 2.5))
    teacher_counts = df['Teacher'].value_counts()
    sns.barplot(x=teacher_counts.index, y=teacher_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Rapporterende Onderwyser', pad=10, fontsize=10, weight='bold')
    ax.set_xlabel('Onderwyser', fontsize=9)
    ax.set_ylabel('Aantal', fontsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Class
    fig, ax = plt.subplots(figsize=(4, 2.5))
    class_counts = df['Class'].value_counts()
    sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette='muted')
    ax.set_title('Insidente volgens Klas', pad=10, fontsize=10, weight='bold')
    ax.set_xlabel('Klas', fontsize=9)
    ax.set_ylabel('Aantal', fontsize=9)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Pie chart: Incident Distribution
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=sns.color_palette('muted'), textprops={'fontsize': 8})
    ax.set_title('Insident Verspreiding volgens Kategorie', pad=10, fontsize=10, weight='bold')
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

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
                cells[i].text = row[col].strftime("%Y-%m-%d %H:%M:%S")
            else:
                cells[i].text = str(row[col])

    if not df.empty:
        doc.add_heading('Insident Analise', level=1)
        fig, ax = plt.subplots(figsize=(4, 2.5))
        category_counts = df['Category'].value_counts().sort_index()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='muted')
        ax.set_title('Insidente volgens Kategorie', pad=10, fontsize=10, weight='bold')
        ax.set_xlabel('Kategorie', fontsize=9)
        ax.set_ylabel('Aantal', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
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

# Sidebar for incident input
with st.sidebar:
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
        learner_report_name = st.selectbox("", options=['Kies'] + sorted(incident_log['Learner_Full_Name'].unique()), key="learner_report_name")
        
        st.markdown('<div class="input-label">Kies Tydperk</div>', unsafe_allow_html=True)
        report_period = st.selectbox("", options=['Daagliks', 'Weekliks', 'Maandelik', 'Kwartaalliks'], key="report_period")

        sa_tz = pytz.timezone('Africa/Johannesburg')
        today = datetime.now(sa_tz).replace(hour=0, minute=0, second=0, microsecond=0)

        if report_period == 'Daagliks':
            start_date = today
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif report_period == 'Weekliks':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7) - timedelta(seconds=1)
        elif report_period == 'Maandelik':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        else:
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            end_date = (start_date + timedelta(days=92)).replace(day=1) - timedelta(seconds=1)

        start_date = start_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)

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

# Main content
with st.container():
    st.title("HOËRSKOOL SAUL DAMON")
    st.subheader("INSIDENT VERSLAG")

    st.subheader("Insident Log")
    if not incident_log.empty:
        rows_per_page = 10
        total_rows = len(incident_log)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        if 'incident_log_page' not in st.session_state:
            st.session_state.incident_log_page = 1

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Vorige", disabled=(st.session_state.incident_log_page == 1)):
                st.session_state.incident_log_page -= 1
        with col2:
            page_options = list(range(1, total_pages + 1))
            st.session_state.incident_log_page = st.selectbox(
                "Bladsy",
                options=page_options,
                index=st.session_state.incident_log_page - 1,
                key="incident_log_page_select"
            )
        with col3:
            if st.button("Volgende", disabled=(st.session_state.incident_log_page == total_pages)):
                st.session_state.incident_log_page += 1

        start_idx = (st.session_state.incident_log_page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)

        display_df = incident_log.iloc[start_idx:end_idx].copy()
        display_df.index = range(start_idx + 1, min(end_idx + 1, total_rows + 1))

        st.dataframe(
            display_df,
            height=300,
            use_container_width=True,
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerder Naam", width="medium"),
                "Class": st.column_config.TextColumn("Klas", width="small"),
                "Teacher": st.column_config.TextColumn("Onderwyser", width="medium"),
                "Incident": st.column_config.TextColumn("Insident", width="medium"),
                "Category": st.column_config.TextColumn("Kategorie", width="small"),
                "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
                "Date": st.column_config.DatetimeColumn("Datum", width="medium", format="YYYY-MM-DD HH:mm:ss")
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
    today = datetime.now(sa_tz).date()
    today_incidents = incident_log[incident_log['Date'].dt.date == today]
    if not today_incidents.empty:
        st.write(f"Totale Insidente Vandag: {len(today_incidents)}")

        st.write("Insidente volgens Kategorie")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        category_counts = today_incidents['Category'].value_counts().sort_index()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='muted')
        ax.set_title('Insidente volgens Kategorie (Vandag)', pad=10, fontsize=10, weight='bold')
        ax.set_xlabel('Kategorie', fontsize=9)
        ax.set_ylabel('Aantal', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Tipe")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        incident_counts = today_incidents['Incident'].value_counts()
        sns.barplot(x=incident_counts.index, y=incident_counts.values, ax=ax, palette='muted')
        ax.set_title('Insidente volgens Tipe (Vandag)', pad=10, fontsize=10, weight='bold')
        ax.set_xlabel('Insident', fontsize=9)
        ax.set_ylabel('Aantal', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=60, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Rapporterende Onderwyser")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        teacher_counts = today_incidents['Teacher'].value_counts()
        sns.barplot(x=teacher_counts.index, y=teacher_counts.values, ax=ax, palette='muted')
        ax.set_title('Insidente volgens Rapporterende Onderwyser (Vandag)', pad=10, fontsize=10, weight='bold')
        ax.set_xlabel('Onderwyser', fontsize=9)
        ax.set_ylabel('Aantal', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=60, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

        st.write("Insidente volgens Klas")
        fig, ax = plt.subplots(figsize=(4, 2.5))
        class_counts = today_incidents['Class'].value_counts()
        sns.barplot(x=class_counts.index, y=class_counts.values, ax=ax, palette='muted')
        ax.set_title('Insidente volgens Klas (Vandag)', pad=10, fontsize=10, weight='bold')
        ax.set_xlabel('Klas', fontsize=9)
        ax.set_ylabel('Aantal', fontsize=9)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=60, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()
    else:
        st.write("Geen insidente vandag gerapporteer nie.")

    tab1, tab2, tab3, tab4 = st.tabs(["Gefiltreerde Data", "Weeklikse Opsomming", "Maandelikse Opsomming", "Kwartaallikse Opsomming"])

    with tab1:
        st.subheader("Gefiltreerde Data")
        st.markdown('<div class="input-label">Filter Leerder Naam</div>', unsafe_allow_html=True)
        filter_learner = st.selectbox("", options=['Alle'] + sorted(incident_log['Learner_Full_Name'].unique()), key="filter_learner")
        
        st.markdown('<div class="input-label">Filter Klas</div>', unsafe_allow_html=True)
        filter_class = st.selectbox("", options=['Alle'] + sorted(incident_log['Class'].unique()), key="filter_class")
        
        st.markdown('<div class="input-label">Filter Onderwyser</div>', unsafe_allow_html=True)
        filter_teacher = st.selectbox("", options=['Alle'] + sorted(incident_log['Teacher'].unique()), key="filter_teacher")
        
        st.markdown('<div class="input-label">Filter Insident</div>', unsafe_allow_html=True)
        filter_incident = st.selectbox("", options=['Alle'] + sorted(incident_log['Incident'].unique()), key="filter_incident")
        
        st.markdown('<div class="input-label">Filter Kategorie</div>', unsafe_allow_html=True)
        filter_category = st.selectbox("", options=['Alle'] + sorted(incident_log['Category'].unique(), key=lambda x: int(x)), key="filter_category")
        
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
                "Date": st.column_config.DatetimeColumn("Datum", width="medium", format="YYYY-MM-DD HH:mm:ss")
            }
        )
        st.write(f"Totale Insidente: {len(filtered_df)}")

    with tab2:
        st.subheader("Weeklikse Opsomming")
        if not incident_log.empty:
            weekly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='W-MON'), 'Category']).size().unstack(fill_value=0)
            weekly_summary.index = weekly_summary.index.strftime('%Y-%m-%d')
            st.dataframe(weekly_summary, use_container_width=True, height=300)
            fig, ax = plt.subplots(figsize=(4, 2.5))
            weekly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Weeklikse Insidente volgens Kategorie', pad=10, fontsize=10, weight='bold')
            ax.set_xlabel('Week Begin (Maandag)', fontsize=9)
            ax.set_ylabel('Aantal', fontsize=9)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab3:
        st.subheader("Maandelikse Opsomming")
        if not incident_log.empty:
            monthly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
            monthly_summary.index = monthly_summary.index.strftime('%Y-%m')
            st.dataframe(monthly_summary, use_container_width=True, height=300)
            fig, ax = plt.subplots(figsize=(4, 2.5))
            monthly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Maandelikse Insidente volgens Kategorie', pad=10, fontsize=10, weight='bold')
            ax.set_xlabel('Maand', fontsize=9)
            ax.set_ylabel('Aantal', fontsize=9)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab4:
        st.subheader("Kwartaallikse Opsomming")
        if not incident_log.empty:
            quarterly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='Q'), 'Category']).size().unstack(fill_value=0)
            quarterly_summary.index = quarterly_summary.index.map(
                lambda x: f"{x.year}-Q{(x.month-1)//3 + 1}"
            )
            st.dataframe(quarterly_summary, use_container_width=True, height=300)
            fig, ax = plt.subplots(figsize=(4, 2.5))
            quarterly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Kwartaallikse Insidente volgens Kategorie', pad=10, fontsize=10, weight='bold')
            ax.set_xlabel('Kwartaal', fontsize=9)
            ax.set_ylabel('Aantal', fontsize=9)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            plt.tight_layout(pad=1.0)
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")