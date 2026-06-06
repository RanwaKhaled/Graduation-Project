import os
import tempfile
import urllib.request
import markdown
import convertapi

def text_to_pdf_bytes_english(markdown_text: str) -> bytes:
    """Generates a beautiful, highly-styled PDF from Markdown (No MathJax)."""
    
    # 1. Clean up LLM artifacts
    clean_text = markdown_text.replace("```markdown", "").replace("```", "").strip()

    # 2. Convert to HTML with formatting extensions
    html_body = markdown.markdown(
        clean_text,
        extensions=['tables', 'fenced_code', 'sane_lists', 'nl2br']
    )

    # 3. Inject a gorgeous, modern CSS stylesheet (GitHub style)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 23px;
                line-height: 1.6;
                color: #24292e;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3, h4, h5 {{
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }}
            h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h3 {{ font-size: 1.25em; }}
            p, blockquote, ul, ol, dl, table, pre, details {{
                margin-top: 0;
                margin-bottom: 16px;
            }}
            blockquote {{
                padding: 0 1em;
                color: #6a737d;
                border-left: 0.25em solid #dfe2e5;
            }}
            code {{
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: rgba(27,31,35,0.05);
                border-radius: 3px;
                font-family: Consolas, "Liberation Mono", Courier, monospace;
            }}
            pre {{
                word-wrap: normal;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #f6f8fa;
                border-radius: 6px;
            }}
            pre code {{
                display: inline;
                padding: 0;
                margin: 0;
                overflow: visible;
                line-height: inherit;
                word-wrap: normal;
                background-color: transparent;
                border: 0;
            }}
            table {{
                border-spacing: 0;
                border-collapse: collapse;
                width: 100%;
            }}
            table th, table td {{
                padding: 8px 13px;
                border: 1px solid #dfe2e5;
            }}
            table tr:nth-child(2n) {{
                background-color: #f6f8fa;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # 4. Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as temp_html:
        temp_html.write(html_content)
        temp_html_path = temp_html.name

    try:
        # 5. Call ConvertAPI using the correct INT data types to fix the 400 error!
        result = convertapi.convert(
            'pdf',
            {
                'File': temp_html_path,
                'MarginTop': 5,
                'MarginBottom': 5,
                'MarginLeft': 5,
                'MarginRight': 5,
                'PageSize': 'a4'
            },
            from_format='html'
        )

        # 6. Fetch and return
        with urllib.request.urlopen(result.file.url) as response:
            return response.read()

    finally:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)