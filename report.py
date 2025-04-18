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

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# Set page config
st.set_page_config(page_title="Insident Verslag", layout="wide")

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* General layout */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #e9ecef;
            padding: 20px;
            border-right: 1px solid #dee2e6;
        }
        .main .block-container {
            padding: 30px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        /* Headers */
        h1 {
            color: #343a40;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        h2 {
            color: #495057;
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        h3 {
            color: #495057;
            font-size: 1.4rem;
            font-weight: 500;
        }

        /* Buttons */
        .stButton>button {
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-size: 1rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .stButton>button:hover {
            background-color: #218838;
            color: white;
        }
        .stButton>button:disabled {
            background-color: #6c757d;
            color: #d3d3d3;
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            overflow: hidden;
        }
        .stDataFrame table {
            width: 100%;
            border-collapse: collapse;
        }
        .stDataFrame th {
            background-color: #e9ecef;
            color: #343a40;
            font-weight: 600;
            padding: 10px;
            text-align: left;
        }
        .stDataFrame td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stDataFrame tr:hover {
            background-color: #e9ecef;
        }

        /* Sidebar inputs */
        .stSelectbox, .stTextArea {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 5px;
        }
        .stSelectbox:hover, .stTextArea:hover {
            border-color: #28a745;
        }

        /* Text and labels */
        .stMarkdown, .stText {
            color: #495057;
            font-size: 1rem;
        }
        .stAlert {
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# Load and preprocess learner data
@st.cache_data
def load_learner_data():
    df = pd.read_csv("learner_list.csv")
    df.columns = df.columns.str.strip()
    # Combine surname and name into Learner_Full_Name, handling missing values
    df['Learner_Full_Name'] = df['Leerder van'].fillna('') + ' ' + df['Leerner se naam'].fillna('')
    df['Learner_Full_Name'] = df['Learner_Full_Name'].str.strip()  # Remove extra spaces
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
    # Convert Category to integer, handle non-numeric as 'Onbekend'
    df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(0).astype(int).astype(str)
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
        # Check if old column 'Learner_Name' exists and rename to 'Learner_Full_Name'
        if 'Learner_Name' in df.columns and 'Learner_Full_Name' not in df.columns:
            df = df.rename(columns={'Learner_Name': 'Learner_Full_Name'})
        # Convert Category to integer, handle non-numeric as 0
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(0).astype(int).astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Convert to South African time and remove timezone for storage
        sa_tz = pytz.timezone('Africa/Johannesburg')
        df['Date'] = df['Date'].dt.tz_localize('UTC').dt.tz_convert(sa_tz).dt.tz_localize(None)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log
def save_incident(learner_full_name, class_, teacher, incident, category, comment):
    incident_log = load_incident_log()
    sa_tz = pytz.timezone('Africa/Johannesburg')
    # Ensure category is an integer string (e.g., '1' instead of '1.0')
    try:
        category = str(int(float(category)))
    except ValueError:
        category = '0'
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

    # Add table
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

# Generate learner-specific Word report
def generate_learner_report(df, learner_full_name, period, start_date, end_date):
    doc = Document()
    doc.add_heading(f'Insident Verslag vir {learner_full_name}', 0)
    doc.add_paragraph(f'Tydperk: {period}')
    doc.add_paragraph(f'Datum Reeks: {start_date.strftime("%Y-%m-%d")} tot {end_date.strftime("%Y-%m-%d")}')

    # Add table
    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Full_Name': 'Leerling Naam',
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

    # Add chart: Incidents by Category
    if not df.empty:
        doc.add_heading('Insident Analise', level=1)
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

    # Save document to stream
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
        learner_full_name = st.selectbox("Leerling Naam", options=['Kies'] + sorted(learner_df['Learner_Full_Name'].unique()))
        class_ = st.selectbox("Klas", options=['Kies'] + sorted(learner_df['Class'].unique()))
        teacher = st.selectbox("Onderwyser", options=['Kies'] + sorted(learner_df['Teacher'].unique()))
        incident = st.selectbox("Insident", options=['Kies'] + sorted(learner_df['Incident'].unique()))
        category = st.selectbox("Kategorie", options=['Kies'] + sorted(learner_df['Category'].unique(), key=lambda x: str(x)))
        comment = st.text_area("Kommentaar", placeholder="Voer insident kommentaar in")
        if st.button("Stoor Insident"):
            if learner_full_name != 'Kies' and class_ != 'Kies' and teacher != 'Kies' and incident != 'Kies' and category != 'Kies' and comment:
                incident_log = save_incident(learner_full_name, class_, teacher, incident, category, comment)
                st.success("Insident suksesvol gestoor!")
            else:
                st.error("Vul asseblief alle velde in en voer kommentaar in.")

    st.header("Genereer Leerder Verslag")
    with st.container():
        learner_report_name = st.selectbox("Kies Leerling vir Verslag", options=['Kies'] + sorted(incident_log['Learner_Full_Name'].unique()))
        report_period = st.selectbox("Kies Tydperk", options=['Daagliks', 'Weekliks', 'Maandelik', 'Kwartaalliks'])

        # Calculate date range based on period
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
        else:  # Kwartaalliks
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            end_date = (start_date + timedelta(days=92)).replace(day=1) - timedelta(seconds=1)

        # Remove timezone info for comparison
        start_date = start_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)

        # Display date range
        st.write(f"Verslag Datum Reeks: {start_date.strftime('%Y-%m-%d')} tot {end_date.strftime('%Y-%m-%d')}")

        if st.button("Genereer Leerling Verslag"):
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
                        label="Laai Leerling Verslag af",
                        data=report_stream,
                        file_name=f"insident_verslag_{learner_report_name}_{report_period.lower()}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error(f"Geen insidente gevind vir {learner_report_name} in die geselekteerde tydperk.")
            else:
                st.error("Kies asseblief 'n leerling.")

# Main content
with st.container():
    st.title("HOËRSKOOL SAUL DAMON")
    st.subheader("INSIDENT VERSLAG")

    # Incident Log with Pagination and Scrollbar
    st.subheader("Insident Log")
    if not incident_log.empty:
        # Pagination settings
        rows_per_page = 10
        total_rows = len(incident_log)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page  # Ceiling division

        # Store current page in session state
        if 'incident_log_page' not in st.session_state:
            st.session_state.incident_log_page = 1

        # Page navigation
        col1, col2, col3 = st.columns([2, 3, 2])
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

        # Calculate start and end indices for the current page
        start_idx = (st.session_state.incident_log_page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)

        # Create a display DataFrame with one-based index
        display_df = incident_log.iloc[start_idx:end_idx].copy()
        display_df.index = range(start_idx + 1, min(end_idx + 1, total_rows + 1))

        # Display paginated data with scrollbar and column config
        st.dataframe(
            display_df,
            height=300,
            use_container_width=True,
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerling Naam", width="medium"),
                "Class": st.column_config.TextColumn("Klas", width="small"),
                "Teacher": st.column_config.TextColumn("Onderwyser", width="medium"),
                "Incident": st.column_config.TextColumn("Insident", width="medium"),
                "Category": st.column_config.TextColumn("Kategorie", width="small"),
                "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
                "Date": st.column_config.DatetimeColumn("Datum", width="medium", format="YYYY-MM-DD HH:mm:ss")
            }
        )
        st.write(f"Wys {start_idx + 1} tot {end_idx} van {total_rows} insidente")

        # Download full report
        st.download_button(
            label="Laai Verslag af as Word",
            data=generate_word_report(incident_log),
            file_name="insident_verslag.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Delete incident with one-based index
        st.write("Verwyder 'n Insident")
        one_based_indices = list(range(1, total_rows + 1))
        selected_display_index = st.selectbox("Kies Insident om te Verwyder (deur Indeks)", options=one_based_indices)
        if st.button("Verwyder Insident"):
            # Convert one-based display index to zero-based DataFrame index
            zero_based_index = selected_display_index - 1
            incident_log = clear_incident(zero_based_index)
            st.success(f"Insident {selected_display_index} suksesvol verwyder!")
            # Adjust page if necessary after deletion
            total_rows = len(incident_log)
            total_pages = (total_rows + rows_per_page - 1) // rows_per_page
            if st.session_state.incident_log_page > total_pages and total_pages > 0:
                st.session_state.incident_log_page = total_pages
            elif total_pages == 0:
                st.session_state.incident_log_page = 1
            st.rerun()
    else:
        st.write("Geen insidente in die log nie.")

    # Daily incident charts
    st.subheader("Vandag se Insidente")
    today = datetime.now(sa_tz).date()
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

    # Tabs for filtered data and summaries
    tab1, tab2, tab3, tab4 = st.tabs(["Gefiltreerde Data", "Weeklikse Opsomming", "Maandelikse Opsomming", "Kwartaallikse Opsomming"])

    with tab1:
        st.subheader("Gefiltreerde Data")
        filter_learner = st.selectbox("Filter Leerling Naam", options=['Alle'] + sorted(incident_log['Learner_Full_Name'].unique()))
        filter_class = st.selectbox("Filter Klas", options=['Alle'] + sorted(incident_log['Class'].unique()))
        filter_teacher = st.selectbox("Filter Onderwyser", options=['Alle'] + sorted(incident_log['Teacher'].unique()))
        filter_incident = st.selectbox("Filter Insident", options=['Alle'] + sorted(incident_log['Incident'].unique()))
        filter_category = st.selectbox("Filter Kategorie", options=['Alle'] + sorted(incident_log['Category'].unique(), key=lambda x: str(x)))
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
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerling Naam", width="medium"),
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
            # Group by week starting Monday, format date as YYYY-MM-DD
            weekly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='W-MON'), 'Category']).size().unstack(fill_value=0)
            weekly_summary.index = weekly_summary.index.strftime('%Y-%m-%d')
            st.dataframe(weekly_summary, use_container_width=True)
            # Create bar chart with formatted dates
            fig, ax = plt.subplots(figsize=(8, 4))
            weekly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Weeklikse Insidente volgens Kategorie')
            ax.set_xlabel('Week Begin (Maandag)')
            ax.set_ylabel('Aantal')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab3:
        st.subheader("Maandelikse Opsomming")
        if not incident_log.empty:
            # Group by month, format date as YYYY-MM-DD
            monthly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
            monthly_summary.index = monthly_summary.index.strftime('%Y-%m')
            st.dataframe(monthly_summary, use_container_width=True)
            # Create bar chart with formatted dates
            fig, ax = plt.subplots(figsize=(8, 4))
            monthly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Maandelikse Insidente volgens Kategorie')
            ax.set_xlabel('Maand')
            ax.set_ylabel('Aantal')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")

    with tab4:
        st.subheader("Kwartaallikse Opsomming")
        if not incident_log.empty:
            # Group by quarter, format date as YYYY-Q#
            quarterly_summary = incident_log.groupby([pd.Grouper(key='Date', freq='Q'), 'Category']).size().unstack(fill_value=0)
            quarterly_summary.index = quarterly_summary.index.map(
                lambda x: f"{x.year}-Q{(x.month-1)//3 + 1}"
            )
            st.dataframe(quarterly_summary, use_container_width=True)
            # Create bar chart with formatted dates
            fig, ax = plt.subplots(figsize=(8, 4))
            quarterly_summary.plot(kind='bar', ax=ax, color=sns.color_palette('muted'))
            ax.set_title('Kwartaallikse Insidente volgens Kategorie')
            ax.set_xlabel('Kwartaal')
            ax.set_ylabel('Aantal')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.write("Geen insidente om te wys nie.")