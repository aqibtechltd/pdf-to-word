import streamlit as st
import os
import time
import uuid
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from utils import convert_pdf_to_docx, cleanup_temp_files

# Page configuration
st.set_page_config(
    page_title="Free PDF to Word Converter | PDFRocket.site",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Session state initialization
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("<div class='header'><h1>PDF Rocket 🚀</h1><h2>Free PDF to Word Converter</h2></div>", 
                unsafe_allow_html=True)
    st.markdown("<p class='subheading'>Convert your PDFs to editable Word documents in seconds</p>", 
                unsafe_allow_html=True)

# Main content container
main_container = st.container()

with main_container:
    # Conversion quality selector
    quality_options = {
        "Basic": "Fast conversion with basic formatting",
        "Formatted": "Slower but preserves more complex formatting"
    }
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<p class='option-label'>Conversion Quality:</p>", unsafe_allow_html=True)
    with col2:
        quality = st.selectbox("", options=list(quality_options.keys()), 
                              index=1, label_visibility="collapsed")
    
    st.markdown(f"<p class='quality-description'>{quality_options[quality]}</p>", 
                unsafe_allow_html=True)
    
    # File uploader
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.markdown("<p class='upload-title'>Upload PDF Files</p>", unsafe_allow_html=True)
    st.markdown("<p class='upload-subtitle'>Drag and drop files here (10MB max per file)</p>", 
                unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload PDF files", 
                                     type=['pdf'], 
                                     accept_multiple_files=True,
                                     label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # Conversion process
    if uploaded_files:
        st.markdown("<div class='conversion-section'>", unsafe_allow_html=True)
        st.markdown("<h3>Converting Files</h3>", unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        converted_files = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Check file size
            file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
            if file_size > 10:
                st.error(f"⚠️ {uploaded_file.name} exceeds the 10MB limit and will be skipped.")
                continue
                
            # Create temp directory if it doesn't exist
            if not os.path.exists("temp"):
                os.makedirs("temp")
                
            # Generate unique filenames
            temp_id = uuid.uuid4().hex
            pdf_path = os.path.join("temp", f"{temp_id}.pdf")
            docx_path = os.path.join("temp", f"{temp_id}.docx")
            
            # Save uploaded PDF
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Status message
            status_msg = st.empty()
            status_msg.info(f"Converting {uploaded_file.name}... Please wait.")
            
            try:
                # Convert PDF to DOCX
                convert_pdf_to_docx(pdf_path, docx_path, quality.lower())
                
                # Generate download link
                with open(docx_path, "rb") as file:
                    docx_data = file.read()
                    b64_docx = base64.b64encode(docx_data).decode()
                    download_filename = uploaded_file.name.replace(".pdf", ".docx")
                    
                    converted_files.append({
                        "original_name": uploaded_file.name,
                        "converted_name": download_filename,
                        "path": docx_path,
                        "data": b64_docx
                    })
                
                status_msg.success(f"✅ Successfully converted {uploaded_file.name}")
                
                # Update session history (keep last 5)
                if len(st.session_state.conversion_history) >= 5:
                    st.session_state.conversion_history.pop(0)
                    
                st.session_state.conversion_history.append({
                    "original_name": uploaded_file.name,
                    "converted_name": download_filename,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "data": b64_docx
                })
                
            except Exception as e:
                status_msg.error(f"❌ Error converting {uploaded_file.name}: {str(e)}")
            
            # Update progress bar
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Download section
        if converted_files:
            st.markdown("<h3>Download Converted Files</h3>", unsafe_allow_html=True)
            
            for file in converted_files:
                href = f'<a class="download-btn" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{file["data"]}" download="{file["converted_name"]}">Download {file["converted_name"]}</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            # Email option
            st.markdown("<h3>Email Converted Files</h3>", unsafe_allow_html=True)
            recipient_email = st.text_input("Enter email address:", key="email_input")
            
            if st.button("Send via Email"):
                if recipient_email and "@" in recipient_email and "." in recipient_email:
                    try:
                        # Email sending would be implemented here in production
                        # This is a placeholder as email sending requires SMTP credentials
                        st.session_state.email_sent = True
                        st.success(f"✉️ Files would be sent to {recipient_email} in production.")
                        st.info("Note: Actual email functionality requires SMTP server setup.")
                    except Exception as e:
                        st.error(f"Failed to send email: {str(e)}")
                else:
                    st.error("Please enter a valid email address")
            
            # Batch download (all files in a single click)
            if len(converted_files) > 1:
                st.markdown("<h3>Batch Download</h3>", unsafe_allow_html=True)
                st.markdown("Download all files with a single click:")
                
                # In a production app, you would create a zip file here
                # This is a simplified example
                st.info("Note: In production, this would create a zip file with all conversions.")
                st.button("Download All (Zip)")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Conversion history section
if st.session_state.conversion_history:
    st.markdown("<div class='history-section'>", unsafe_allow_html=True)
    st.markdown("<h3>Recent Conversions</h3>", unsafe_allow_html=True)
    
    for item in reversed(st.session_state.conversion_history):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"📄 {item['original_name']}")
        with col2:
            st.write(f"🕒 {item['timestamp']}")
        with col3:
            href = f'<a class="history-download-btn" href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{item["data"]}" download="{item["converted_name"]}">Download</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Guide section
with st.expander("How to Use PDF Rocket"):
    st.markdown("""
    ### Simple Steps to Convert PDF to Word:
    
    1. **Select Quality**: Choose between basic (faster) or formatted (better quality) conversion.
    2. **Upload Files**: Drag and drop your PDF files (up to 10MB each).
    3. **Convert**: We'll automatically process your files.
    4. **Download**: Click the download button to get your editable Word document.
    
    ### Tips for Best Results:
    
    - For complex layouts, use the "Formatted" quality option.
    - Make sure your PDF isn't password-protected.
    - For large files, consider splitting them into smaller PDFs first.
    - Text-based PDFs convert better than scanned documents.
    """)

# Footer
st.markdown("<footer>App Built By Aqib Chaudhary</footer>", unsafe_allow_html=True)

# Cleanup temporary files on session end
cleanup_temp_files()
