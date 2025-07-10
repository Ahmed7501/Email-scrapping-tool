import streamlit as st
import tempfile
import os
from pathlib import Path
from main import EmailScraper

st.set_page_config(page_title="Email Scraper Tool", layout="centered")
st.title("📧 Email Scraper Tool")
st.markdown("""
A powerful tool to extract emails from websites and social media. Upload a file with URLs and configure your scraping options below.
""")

# --- Sidebar options ---
st.sidebar.header("Scraping Options")
use_selenium = st.sidebar.checkbox("Use Selenium (for dynamic sites)", value=False)
use_proxies = st.sidebar.checkbox("Use Proxy Rotation", value=False)
use_social = st.sidebar.checkbox("Scrape Social Media", value=True)
max_internal = st.sidebar.slider("Max Internal Pages", 1, 10, 3)
output_format = st.sidebar.selectbox("Output Format", ["csv", "excel", "both"], index=1)

# --- File uploader ---
st.subheader("1. Upload a file with URLs")
file = st.file_uploader(
    "Upload .csv, .xlsx, .xls, .txt, or .docx file",
    type=["csv", "xlsx", "xls", "txt", "docx"]
)

if file:
    st.success(f"Uploaded: {file.name}")
    # Save to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
else:
    tmp_path = None

# --- Scrape button ---
if st.button("Start Scraping", disabled=not file):
    if not tmp_path:
        st.error("Please upload a file to begin.")
    else:
        st.info("Scraping in progress... This may take a few minutes.")
        progress = st.progress(0)
        status_placeholder = st.empty()
        results = None
        try:
            with EmailScraper(
                use_selenium=use_selenium,
                use_proxies=use_proxies,
                use_social_scraping=use_social,
                max_internal_pages=max_internal,
                output_format=output_format
            ) as scraper:
                # Run scraping
                results = scraper.scrape_from_file(tmp_path)
                progress.progress(100)
                status_placeholder.success("Scraping complete!")
        except Exception as e:
            st.error(f"Error: {e}")
            status_placeholder.error("Scraping failed.")
            results = None
        
        # --- Show summary ---
        if results:
            st.subheader("2. Results Summary")
            st.write(f"**Total URLs processed:** {results['total_urls_processed']}")
            st.write(f"**Successful scrapes:** {results['successful_scrapes']}")
            st.write(f"**Failed scrapes:** {results['failed_scrapes']}")
            st.write(f"**Unique emails found:** {results['unique_emails_found']}")
            st.write(f"**Success rate:** {results['success_rate']:.2f}%")
            
            # --- Download buttons ---
            st.subheader("3. Download Results")
            output_files = results.get('output_files', {})
            for label, path in output_files.items():
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        file_bytes = f.read()
                        ext = Path(path).suffix
                        if ext == ".csv":
                            mime = "text/csv"
                        elif ext in [".xlsx", ".xls"]:
                            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        elif ext == ".txt":
                            mime = "text/plain"
                        else:
                            mime = "application/octet-stream"
                        st.download_button(
                            label=f"Download {label.upper()} ({Path(path).name})",
                            data=file_bytes,
                            file_name=Path(path).name,
                            mime=mime
                        )
            st.success("All done! You can now download your results.")

st.markdown("---")
st.caption("Developed with ❤️ using Streamlit and Python. | [GitHub](#)") 