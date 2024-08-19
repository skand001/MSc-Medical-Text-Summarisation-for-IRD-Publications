import os
import re

def is_metadata_or_reference(line):
    """Check if the line is likely to be metadata, a reference, or a citation."""
    if re.search(r'\bDOI\b|\bPMID\b|\bwww\b|\bhttp\b|Quick Response Code|Correspondence', line, re.IGNORECASE):
        return True
    if re.match(r'^\s*©', line):
        return True
    if re.match(r'^\s*[0-9]+\s*\(.*\)', line):
        return True
    if re.match(r'^\s*\[.*\]', line):
        return True
    if re.match(r'^\s*\*', line):
        return True
    if re.match(r'^\s*Received:|Accepted:|Published:', line, re.IGNORECASE):
        return True
    return False

def extract_abstract(text):
    # Possible sections indicating the beginning of the abstract
    abstract_start_patterns = [
        r'\bAbstract\b',
        r'\bBackground\b',
        r'\bPurpose\b'
    ]
    
    # Possible sections indicating the end of the abstract
    abstract_end_patterns = [
        r'\bKeywords\b',
        r'\bIntroduction\b',
        r'\bMethods\b',
        r'\bMaterials\b',
        r'\bResults\b',
        r'\bConclusion\b',
        r'\bReferences\b',
        r'\bCitations\b'
    ]
    
    abstract_start = None
    abstract_end = len(text)
    
    # Search for the start of the abstract using standard patterns
    for pattern in abstract_start_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            abstract_start = match.end()
            break
    
    # If no start pattern is found, find the start of the first meaningful section after skipping metadata and author info
    if not abstract_start:
        lines = text.splitlines()
        found_authors_section = False
        
        for line in lines:
            # Skip lines that are metadata or references or part of author information
            if is_metadata_or_reference(line):
                found_authors_section = True  # Assume author section has passed after metadata lines
                continue

            # Consider a line with sufficient length and no citations/metadata as potential abstract start
            if found_authors_section and len(line.strip()) > 30 and not re.search(r'\[\d+\]', line) and not line.strip().isdigit():
                abstract_start = text.find(line)
                break
    
    # Search for the end of the abstract
    for pattern in abstract_end_patterns:
        match = re.search(pattern, text[abstract_start:], re.IGNORECASE)
        if match:
            abstract_end = abstract_start + match.start()
            break
    
    # Extract the abstract content
    abstract = text[abstract_start:abstract_end].strip()
    
    # Limit the abstract to 250 words
    words = abstract.split()
    if len(words) > 250:
        abstract = ' '.join(words[:250])
    
    return abstract

def process_files(directory):
    abstracts = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                text = file.read()
                abstract = extract_abstract(text)
                if abstract:
                    abstracts[filename] = abstract
    
    return abstracts

# Specify the directory where your text files are located
directory = 'path/to/your/text/files'

abstracts = process_files(directory)

# Save abstracts to a new file or print them
with open('extracted_abstracts.txt', 'w', encoding='utf-8') as output_file:
    for filename, abstract in abstracts.items():
        output_file.write(f"File: {filename}\nAbstract:\n{abstract}\n\n")
        
print("Abstracts extraction completed. Check 'extracted_abstracts.txt' for results.")
