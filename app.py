import streamlit as st
import pandas as pd
import plotly.express as px

from processing import impute_missing_values, handle_outliers, apply_rules, calculate_estimates
from reporting import generate_report_html, create_pdf_report

st.set_page_config(layout="wide")
st.title("🤖 AI Enhanced Application for Survey Data")

# Initialize session state keys
if "df_final" not in st.session_state:
    st.session_state.df_final = None
    st.session_state.df_estimates = None
    st.session_state.logs = None
    st.session_state.fig = None

# File Uploader
uploaded_file = st.file_uploader("Upload your raw survey file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.subheader("Raw Data Preview")
    st.dataframe(df_raw)

    # Configuration Sidebar
    st.sidebar.header("⚙️ Configuration")
    all_columns = df_raw.columns.tolist()
    numeric_columns = df_raw.select_dtypes(include='number').columns.tolist()
    
    imputation_cols = st.sidebar.multiselect("Select columns for imputation:", options=numeric_columns, default=numeric_columns)
    imputation_method = st.sidebar.selectbox("Imputation Method:", ["Median", "Mean", "KNN"])
    outlier_cols = st.sidebar.multiselect("Select columns for outlier handling:", options=numeric_columns, default=numeric_columns)
    weight_column = st.sidebar.selectbox(
        "Select the design weight column:", 
        options=numeric_columns, 
        index=numeric_columns.index('Design_Weight') if 'Design_Weight' in numeric_columns else 0
    )

    # Processing
    if st.sidebar.button("🚀 Run Analysis"):
        with st.spinner("Processing data..."):
            logs = []
            
            df_imputed, log = impute_missing_values(df_raw, columns=imputation_cols, method=imputation_method)
            logs.append(log)
            df_outliers_handled, log = handle_outliers(df_imputed, columns=outlier_cols)
            logs.append(log)
            df_validated, log = apply_rules(df_outliers_handled)
            logs.append(log)
            df_estimates, log = calculate_estimates(df_validated, weight_column=weight_column)
            logs.append(log)
            
            st.session_state.df_final = df_validated
            st.session_state.df_estimates = df_estimates
            st.session_state.logs = logs
            
            if st.session_state.df_estimates is not None and not st.session_state.df_estimates.empty:
                st.session_state.fig = px.bar(
                    st.session_state.df_estimates, x='Variable', y=['Unweighted Mean', 'Weighted Mean'],
                    barmode='group', title="Weighted vs. Unweighted Mean Estimates"
                )
            else:
                st.session_state.fig = None

# Display Results
if st.session_state.df_final is not None:
    st.header("📊 Results")

    st.subheader("Final Cleaned Data")
    st.dataframe(st.session_state.df_final)
    
    st.subheader("Full Descriptive Statistics (Cleaned Data)")
    st.dataframe(st.session_state.df_final.describe())

    st.subheader("Summary Estimates")
    st.dataframe(st.session_state.df_estimates)
        
    st.subheader("Visualizations")
    if st.session_state.fig:
        st.plotly_chart(st.session_state.fig, use_container_width=True)

    st.subheader("Data Distributions")
    column_to_plot = st.selectbox(
        "Select a numeric column to see its distribution:",
        st.session_state.df_final.select_dtypes(include='number').columns
    )
    if column_to_plot:
        fig_hist = px.histogram(
            st.session_state.df_final,
            x=column_to_plot,
            title=f'Distribution of {column_to_plot}'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    st.subheader("Processing Logs")
    st.text_area("Logs", "\n".join(st.session_state.logs), height=250)
    
    # Report Download Section
    st.subheader("⬇️ Download Report")
    
    # Pass the filename to the reporting function
    html_report = generate_report_html(
        st.session_state.df_final, 
        st.session_state.df_estimates, 
        st.session_state.logs,
        st.session_state.fig,
        uploaded_file.name  # <-- This is the new argument
    )

    dl_col1, dl_col2 = st.columns(2)
    
    with dl_col1:
        st.download_button(
            label="Download as HTML",
            data=html_report,
            file_name=f"report_{uploaded_file.name}.html",
            mime="text/html"
        )
        
    with dl_col2:
        pdf_report = create_pdf_report(html_report)
        st.download_button(
            label="Download as PDF",
            data=pdf_report,
            file_name=f"report_{uploaded_file.name}.pdf",
            mime="application/pdf"
        )
