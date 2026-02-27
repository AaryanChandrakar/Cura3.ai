"""
Cura3.ai — Report Parser
Parses uploaded files (.txt, .pdf, .docx) and extracts text content.
"""
import io


async def parse_txt(file_bytes: bytes) -> str:
    """Parse a plain text file."""
    return file_bytes.decode("utf-8", errors="replace")


async def parse_pdf(file_bytes: bytes) -> str:
    """Parse a PDF file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


async def parse_docx(file_bytes: bytes) -> str:
    """Parse a DOCX file using python-docx."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")


async def parse_report_file(filename: str, file_bytes: bytes) -> str:
    """
    Parse a report file based on its extension.

    Args:
        filename: Original filename (used to detect format)
        file_bytes: Raw file content as bytes

    Returns:
        Extracted text content

    Raises:
        ValueError: If the file format is not supported
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "txt":
        return await parse_txt(file_bytes)
    elif ext == "pdf":
        return await parse_pdf(file_bytes)
    elif ext == "docx":
        return await parse_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file format: .{ext}. Supported: .txt, .pdf, .docx"
        )
