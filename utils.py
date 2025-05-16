import os
import glob
import tempfile
from pdf2docx import Converter
import time

def convert_pdf_to_docx(pdf_path, docx_path, quality='formatted'):
    """
    Convert PDF to DOCX using pdf2docx library
    
    Args:
        pdf_path (str): Path to the PDF file
        docx_path (str): Output path for the DOCX file
        quality (str): 'basic' or 'formatted'
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a converter object
        cv = Converter(pdf_path)
        
        # Set conversion parameters based on quality
        if quality == 'basic':
            # Basic conversion parameters (faster)
            cv.convert(docx_path, start=0, end=None, zoom_factor=1.0, debug=False)
        else:
            # Formatted conversion parameters (better quality)
            cv.convert(docx_path, start=0, end=None, zoom_factor=1.5, debug=False)
        
        # Close the converter
        cv.close()
        return True
    except Exception as e:
        # Log error
        print(f"Conversion error: {str(e)}")
        raise e

def cleanup_temp_files():
    """
    Remove temporary files created during conversion
    """
    try:
        # Clean up temp directory if it exists
        if os.path.exists("temp"):
            files = glob.glob("temp/*")
            for f in files:
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                except Exception as e:
                    print(f"Error deleting {f}: {e}")
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
