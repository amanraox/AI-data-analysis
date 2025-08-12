import pandas as pd
from weasyprint import HTML
import plotly.graph_objects as go

def generate_report_html(df_final, df_estimates, logs, chart_fig, filename):
    """Compiles all results into a single, interactive HTML string."""
    
    final_table_html = df_final.to_html(classes='styled-table', index=False)
    estimates_table_html = df_estimates.to_html(classes='styled-table', index=False)
    
    if chart_fig:
        chart_html = chart_fig.to_html(full_html=False, include_plotlyjs=True)
    else:
        chart_html = "<p>No chart to display.</p>"

    logs_html = "<pre>" + "\n".join(logs) + "</pre>"
    
    # The only change is adding the filename to the h1 tag below
    html_string = f"""
    <html>
    <head>
        <title>Survey Data Analysis Report for {filename}</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            h1, h2 {{ color: #333; }}
            .styled-table {{
                border-collapse: collapse; margin: 25px 0; font-size: 0.9em;
                min-width: 400px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
            .styled-table thead tr {{
                background-color: #009879; color: #ffffff; text-align: left;
            }}
            .styled-table th, .styled-table td {{ padding: 12px 15px; }}
            .styled-table tbody tr {{ border-bottom: 1px solid #dddddd; }}
            .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
            pre {{
                background-color: #eee; padding: 10px; border: 1px solid #ddd;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <h1>Survey Data Analysis Report for: {filename}</h1>
        <h2>Final Cleaned Data</h2>{final_table_html}
        <h2>Summary Estimates</h2>{estimates_table_html}
        <h2>Visualizations</h2>{chart_html}
        <h2>Processing Logs</h2>{logs_html}
    </body>
    </html>
    """
    return html_string

def create_pdf_report(html_string):
    """Converts an HTML string directly to PDF bytes."""
    return HTML(string=html_string).write_pdf()
