from docx import Document
import asyncio


async def extract(path:str) -> str:
    try:
        doc = Document(path)
        text_pr = []
        for pr in doc.paragraphs:
            if pr.text.strip():
                text_pr.append(pr.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_pr.append(cell.text)  
        return "\n\n".join(text_pr)                      
    except Exception as e:
        raise Exception(f"Error : {e}")

    