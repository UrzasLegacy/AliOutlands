from pdfminer.high_level import extract_text
import fitz  # PyMuPDF
import re
import gspread

def Format_For_Spreadsheet():
    orgs = Miner()
    out_arr = []
    for org in orgs:
        for person in org['Personnel']:
            person_arr = [person['Name'],org['Name'],org['Website'],org['Address'],person['Email'],person['Phone']]
            out_arr.append(person_arr)

    gclient = gspread.service_account(filename='outlands-pricesheet-594e57a3357a.json')

    spreadsheet = gclient.open("Outlands Pricesheet")
    worksheet = spreadsheet.get_worksheet(0)
    worksheet.update(values=out_arr, range_name='A2')

def Miner():
    text = extract_text('DL.pdf', page_numbers=range(4, 20))
    chunks = chunker(text,extract_anchors())
    orgs = []
    for index,chunk in enumerate(chunks):
        orgs.append(Chunk_Analyzer(Chunk_Filter(chunk)))
        #print(f"{index}-\n{Chunk_Filter(chunk)}\n{index}-")
        #print(f"{index}-\n{Chunk_Analyzer(Chunk_Filter(chunk))}\n{index}-")
    return orgs

def Chunk_Filter(chunk):
    filtered_chunk_list = []
    sub_chunks = chunk.split('\n\n')
    for sub_chunk in sub_chunks:
        filtered_sub_chunk = []
        sub_lines = sub_chunk.split("\n")
        for sub_line in sub_lines:
            if not sub_line or len(sub_line) < 3 or "Membership Directory" in sub_line:
                continue
            filtered_sub_chunk.append(sub_line)
        if len(filtered_sub_chunk) > 2:
            filtered_chunk_list.append("\n".join(filtered_sub_chunk))
    return "\n\n".join(filtered_chunk_list)

def Chunk_Analyzer(filtered_chunk):
    organization = {
        'Name': '',
        'Address': '',
        'Website': '',
        'Personnel': []
    }
    if(len(filtered_chunk) == 0):
        return organization
    sub_chunks = filtered_chunk.split('\n\n')
    for chunk_index,sub_chunk in enumerate(sub_chunks):
        if chunk_index == 0:
            lines = sub_chunk.split('\n')
            if(len(lines) == 0):
                continue
            organization['Name'] = lines.pop(0).strip()
            try:
                website_check = lines.pop().strip()
            except Exception as e:
                print(f"ERROR: {filtered_chunk}")
            if "www" in website_check or ".com" in website_check or "http" in website_check:
                organization['Website'] = website_check
                organization['Address'] = ' '.join(lines).strip()
            else:
                organization['Address'] = f"{' '.join(lines)} {website_check}".strip()
            continue
        
        person = {
            'Name': '',
            'Phone': '',
            'Email': ''
        }
        lines = sub_chunk.split('\n')
        person['Name'] = lines.pop(0).strip()
        for line in lines:
            if "Email:" in line:
                person['Email'] = line.strip().replace('Email:','')
            elif "Phone:" in line:
                person['Phone'] = line.strip().replace('Phone:','')
        organization['Personnel'].append(person)
    return organization



def extract_text_with_bold_detection():
    def is_bold(fontname, flags):
        bold_markers = ['bold', 'bd', 'demi']
        if any(marker in fontname.lower() for marker in bold_markers):
            return True
        if flags & (1 << 0):  # Bit 0: bold
            return True
        return False
    doc = fitz.open('DL.pdf')
    formatted_text = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if 'lines' in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        if is_bold(span['font'], span['flags']):
                            formatted_text.append((span['text'], 'bold'))
                        else:
                            formatted_text.append((span['text'], 'regular'))
    return formatted_text

def extract_anchors():
    formatted_text = extract_text_with_bold_detection()
    entities = []
    for text, style in formatted_text:  # Just showing the first 10 for brevity
        if style == "bold" and len(text) > 2:
            entities.append(text.strip())
    return entities[9:]

def chunker(full_text,markers):
    escaped_markers = [re.escape(marker) for marker in markers]
    pattern = '|'.join(escaped_markers)
    matches = list(re.finditer(pattern, full_text))
    chunks = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        chunk = full_text[start:end]
        chunks.append(chunk)
    return chunks

def test():
    chunk = """US Playground Surfacing, LLC
PO Box 82828
29 Thompson Hill Rd
Collinsville, CT 06019-3532
www.USPlaygroundSurfacing.com

Michael McGuffie
Owner
Phone: 860-309-9901
Email: mmcguffie@usplaygroundsurfacing.com

Michael McGuffie
Owner
Phone: 860-309-9901
Email: mmcguffie@usplaygroundsurfacing.com

CSBGA 2023-2024 Membership Directory (as of November 5, 2023)

20








"""
    print(Chunk_Analyzer(Chunk_Filter(chunk)))


Format_For_Spreadsheet()