import re

def parse_analysis(analysis_text):
    analysis = {
        "strengths": [],
        "risks": [],
        "alternatives": [],
        "best_practices": [],
        "assessment": ""
    }
    
    lines = analysis_text.split('\n')
    current_section = None
    current_alternative = None
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Detect sections
        if 'STRENGTHS' in line.upper():
            current_section = 'strengths'
            continue
        elif 'RISKS' in line.upper():
            current_section = 'risks'
            continue
        elif 'ALTERNATIVES' in line.upper():
            current_section = 'alternatives'
            continue
        elif 'BEST PRACTICES' in line.upper():
            current_section = 'best_practices'
            continue
        elif 'OVERALL ASSESSMENT' in line.upper():
            current_section = 'assessment'
            continue
        
        # Parse content based on section
        if current_section == 'strengths' and line.startswith('-'):
            analysis['strengths'].append(line[1:].strip())
        elif current_section == 'risks' and line.startswith('-'):
            analysis['risks'].append(line[1:].strip())
        elif current_section == 'alternatives':
            # Match numbered list items (e.g., "1. Option", "1. **Option**")
            alt_match = re.match(r'^\d+\.\s*(?:\*\*)?(.*?)(?:\*\*)?$', line)
            if alt_match:
                if current_alternative:
                    analysis['alternatives'].append(current_alternative)
                current_alternative = {"option": alt_match.group(1).strip(), "pros": "", "cons": ""}
            elif current_alternative:
                # Match Pros/Cons with flexible formatting (e.g., "- Pros:", "- **Pros**:", "Pros:")
                # Case insensitive, handles optional bullets and bolding
                pros_match = re.search(r'(?:-\s*)?(?:\*\*)?pros(?:\*\*)?:\s*(.*)', line, re.IGNORECASE)
                cons_match = re.search(r'(?:-\s*)?(?:\*\*)?cons(?:\*\*)?:\s*(.*)', line, re.IGNORECASE)
                
                if pros_match:
                    current_alternative['pros'] = pros_match.group(1).strip()
                elif cons_match:
                    current_alternative['cons'] = cons_match.group(1).strip()
        elif current_section == 'best_practices' and line.startswith('-'):
            analysis['best_practices'].append(line[1:].strip())
        elif current_section == 'assessment':
            analysis['assessment'] += line + " "
    
    # Add last alternative if exists
    if current_alternative:
        analysis['alternatives'].append(current_alternative)
    
    return analysis

# Test cases
test_cases = [
    """
    **ALTERNATIVES**
    1. **Option A**
       - Pros: Good stuff
       - Cons: Bad stuff
    """,
    """
    **ALTERNATIVES**
    1. **Option B**
       - **Pros**: Good stuff
       - **Cons**: Bad stuff
    """,
    """
    **ALTERNATIVES**
    1. **Option C**
       - **Pros:** Good stuff
       - **Cons:** Bad stuff
    """,
    """
    **ALTERNATIVES**
    1. **Option D**
       - pros: Good stuff
       - cons: Bad stuff
    """
]

for i, text in enumerate(test_cases):
    print(f"--- Test Case {i+1} ---")
    result = parse_analysis(text)
    for alt in result['alternatives']:
        print(f"Option: {alt['option']}")
        print(f"  Pros: '{alt['pros']}'")
        print(f"  Cons: '{alt['cons']}'")
