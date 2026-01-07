#!/usr/bin/env python3
"""
Process NCDR CathPCI documentation into searchable JSON format
"""
import pandas as pd
import pdfplumber
import json
import re
from datetime import datetime

def extract_faqs(excel_path):
    """Extract Additional Coding Directives (FAQs) from Excel"""
    df = pd.read_excel(excel_path, sheet_name='Sheet 1')
    
    entries = []
    for _, row in df.iterrows():
        entry = {
            'id': f"FAQ-{row['ID']}",
            'source': 'Additional Coding Directives (FAQs)',
            'published_date': pd.to_datetime(row['POSTED_DATE']).strftime('%Y-%m-%d') if pd.notna(row['POSTED_DATE']) else 'Unknown',
            'sequence': str(row['SEQNUM']) if pd.notna(row['SEQNUM']) else '',
            'category': row['CATEGORY_NAME'] if pd.notna(row['CATEGORY_NAME']) else '',
            'element_name': row['ELEMENT_NAME'] if pd.notna(row['ELEMENT_NAME']) else '',
            'definition': row['Definition'] if pd.notna(row['Definition']) else '',
            'question': row['QUESTION'] if pd.notna(row['QUESTION']) else '',
            'answer': row['ANSWER'] if pd.notna(row['ANSWER']) else '',
            'keywords': []
        }
        
        # Generate keywords from all text fields
        text_content = f"{entry['sequence']} {entry['element_name']} {entry['question']} {entry['answer']} {entry['definition']}"
        keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower()))
        entry['keywords'] = sorted(list(keywords))[:20]  # Limit to 20 keywords
        
        entries.append(entry)
    
    return entries

def extract_questions_from_peers(excel_path):
    """Extract Questions from your Peers"""
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    
    entries = []
    for idx, row in df.iterrows():
        # Parse date
        date_str = str(row['Date']) if pd.notna(row['Date']) else 'Unknown'
        try:
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) == 3:
                    month, day, year = parts
                    date_obj = datetime(int(year), int(month), int(day))
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = 'Unknown'
            else:
                formatted_date = 'Unknown'
        except:
            formatted_date = 'Unknown'
        
        # Handle sequence number - may be numeric or text
        seq_val = ''
        if pd.notna(row['SEQ #']):
            try:
                seq_val = str(int(float(row['SEQ #'])))
            except (ValueError, TypeError):
                seq_val = str(row['SEQ #'])
        
        entry = {
            'id': f"PEER-{idx+1}",
            'source': 'Questions from your Peers',
            'published_date': formatted_date,
            'sequence': seq_val,
            'data_field': row['Data Field'] if pd.notna(row['Data Field']) else '',
            'question': row['Questions from your Peers'] if pd.notna(row['Questions from your Peers']) else '',
            'answer': row['Answer'] if pd.notna(row['Answer']) else '',
            'rationale': row['Rationale'] if pd.notna(row['Rationale']) else '',
            'keywords': []
        }
        
        # Generate keywords
        text_content = f"{entry['sequence']} {entry['data_field']} {entry['question']} {entry['answer']} {entry['rationale']}"
        keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower()))
        entry['keywords'] = sorted(list(keywords))[:20]
        
        entries.append(entry)
    
    return entries

def extract_supplement(pdf_path):
    """Extract Supplemental Dictionary entries from PDF"""
    entries = []
    
    with pdfplumber.open(pdf_path) as pdf:
        current_section = None
        current_seq = None
        current_content = []
        
        for page_num, page in enumerate(pdf.pages, 1):
            if page_num <= 2:  # Skip title/TOC pages
                continue
                
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                # Look for sequence numbers
                seq_match = re.search(r'Seq#(\d+)', line)
                if seq_match:
                    # Save previous entry if exists
                    if current_seq and current_content:
                        entry = {
                            'id': f"SUPP-{current_seq}",
                            'source': 'Supplemental Dictionary',
                            'published_date': '2025-01-03',
                            'sequence': current_seq,
                            'section': current_section or '',
                            'content': ' '.join(current_content),
                            'keywords': []
                        }
                        text_content = f"{entry['sequence']} {entry['content']}"
                        keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower()))
                        entry['keywords'] = sorted(list(keywords))[:20]
                        entries.append(entry)
                    
                    # Start new entry
                    current_seq = seq_match.group(1)
                    current_content = [line]
                elif current_seq:
                    # Add to current entry
                    current_content.append(line)
                elif line.startswith('Section '):
                    current_section = line
        
        # Don't forget the last entry
        if current_seq and current_content:
            entry = {
                'id': f"SUPP-{current_seq}",
                'source': 'Supplemental Dictionary',
                'published_date': '2025-01-03',
                'sequence': current_seq,
                'section': current_section or '',
                'content': ' '.join(current_content),
                'keywords': []
            }
            text_content = f"{entry['sequence']} {entry['content']}"
            keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower()))
            entry['keywords'] = sorted(list(keywords))[:20]
            entries.append(entry)
    
    return entries

def extract_data_dictionary_sample(pdf_path):
    """Extract entries from Data Dictionary with structured fields"""
    entries = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            current_entry = None
            current_field = None

            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')

                for line in lines:
                    line = line.strip()

                    # Look for sequence numbers (start of new entry)
                    seq_match = re.match(r'Seq(?:uence)?[:#\s]*(\d+)', line, re.IGNORECASE)
                    if seq_match:
                        # Save previous entry if exists
                        if current_entry and current_entry.get('sequence'):
                            entries.append(current_entry)

                        # Start new entry
                        seq_num = seq_match.group(1)
                        current_entry = {
                            'id': f"DD-{seq_num}",
                            'source': 'Data Dictionary',
                            'published_date': '2024-11-15',
                            'sequence': seq_num,
                            'element_reference': '',
                            'name': '',
                            'coding_instructions': '',
                            'target_value': '',
                            'supporting_definition': '',
                            'keywords': []
                        }
                        current_field = None
                        continue

                    if not current_entry:
                        continue

                    # Identify field labels
                    if re.match(r'Element\s+Reference', line, re.IGNORECASE):
                        current_field = 'element_reference'
                        # Try to extract value from same line
                        value = re.sub(r'Element\s+Reference[:\s]*', '', line, flags=re.IGNORECASE).strip()
                        if value:
                            current_entry[current_field] = value
                        continue
                    elif re.match(r'^Name[:\s]*', line, re.IGNORECASE) and not re.search(r'element', line, re.IGNORECASE):
                        current_field = 'name'
                        value = re.sub(r'^Name[:\s]*', '', line, flags=re.IGNORECASE).strip()
                        if value:
                            current_entry[current_field] = value
                        continue
                    elif re.match(r'Coding\s+Instructions?', line, re.IGNORECASE):
                        current_field = 'coding_instructions'
                        value = re.sub(r'Coding\s+Instructions?[:\s]*', '', line, flags=re.IGNORECASE).strip()
                        if value:
                            current_entry[current_field] = value
                        continue
                    elif re.match(r'Target\s+Value', line, re.IGNORECASE):
                        current_field = 'target_value'
                        value = re.sub(r'Target\s+Value[:\s]*', '', line, flags=re.IGNORECASE).strip()
                        if value:
                            current_entry[current_field] = value
                        continue
                    elif re.match(r'Supporting\s+Definition', line, re.IGNORECASE):
                        current_field = 'supporting_definition'
                        value = re.sub(r'Supporting\s+Definition[:\s]*', '', line, flags=re.IGNORECASE).strip()
                        if value:
                            current_entry[current_field] = value
                        continue

                    # Add content to current field
                    if current_field and line:
                        if current_entry[current_field]:
                            current_entry[current_field] += ' ' + line
                        else:
                            current_entry[current_field] = line

            # Don't forget the last entry
            if current_entry and current_entry.get('sequence'):
                entries.append(current_entry)

            # Generate keywords for all entries
            for entry in entries:
                text_content = ' '.join([
                    entry.get('sequence', ''),
                    entry.get('element_reference', ''),
                    entry.get('name', ''),
                    entry.get('coding_instructions', ''),
                    entry.get('target_value', ''),
                    entry.get('supporting_definition', '')
                ])
                keywords = set(re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower()))
                entry['keywords'] = sorted(list(keywords))[:20]

    except Exception as e:
        print(f"Error processing Data Dictionary: {e}")
        # Add placeholder entry
        entries.append({
            'id': 'DD-PLACEHOLDER',
            'source': 'Data Dictionary',
            'published_date': '2024-11-15',
            'sequence': '',
            'element_reference': '',
            'name': 'Data Dictionary',
            'coding_instructions': 'Data Dictionary processing in progress. Full content will be available soon.',
            'target_value': '',
            'supporting_definition': '',
            'keywords': ['data', 'dictionary', 'placeholder']
        })

    return entries

def main():
    print("Processing NCDR CathPCI documentation...")
    
    all_entries = []
    
    # Process Additional Coding Directives
    print("- Processing Additional Coding Directives (FAQs)...")
    faqs = extract_faqs('/mnt/user-data/uploads/CathPCI-v5_0__6_.xlsx')
    all_entries.extend(faqs)
    print(f"  Found {len(faqs)} FAQ entries")
    
    # Process Questions from Peers
    print("- Processing Questions from your Peers...")
    peers = extract_questions_from_peers('/mnt/user-data/uploads/Questions_from_your_Peers_2025.xlsx')
    all_entries.extend(peers)
    print(f"  Found {len(peers)} peer question entries")
    
    # Process Supplemental Dictionary
    print("- Processing Supplemental Dictionary...")
    supplement = extract_supplement('/mnt/user-data/uploads/v5_datadictionarysupplement_pendingupdates_01032025.pdf')
    all_entries.extend(supplement)
    print(f"  Found {len(supplement)} supplemental entries")
    
    # Process Data Dictionary (sample)
    print("- Processing Data Dictionary (sample)...")
    dd_entries = extract_data_dictionary_sample('/mnt/user-data/uploads/CathPCI_Data_Dictionary_-_Full_Specs.pdf')
    all_entries.extend(dd_entries)
    print(f"  Found {len(dd_entries)} data dictionary entries")
    
    # Save to JSON
    output_path = '/home/claude/ncdr_guidelines_data.json'
    with open(output_path, 'w') as f:
        json.dump(all_entries, f, indent=2)
    
    print(f"\n✓ Complete! Processed {len(all_entries)} total entries")
    print(f"✓ Saved to {output_path}")
    
    # Print summary by source
    print("\nSummary by source:")
    sources = {}
    for entry in all_entries:
        source = entry['source']
        sources[source] = sources.get(source, 0) + 1
    for source, count in sorted(sources.items()):
        print(f"  - {source}: {count} entries")

if __name__ == '__main__':
    main()
