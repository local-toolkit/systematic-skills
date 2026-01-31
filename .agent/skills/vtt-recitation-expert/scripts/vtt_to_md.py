import re
import sys

def parse_time(time_str):
    """Convert 00:00:02.320 to seconds (float)"""
    parts = time_str.split(':')
    seconds = 0
    if len(parts) == 3:
        seconds += int(parts[0]) * 3600
        seconds += int(parts[1]) * 60
        seconds += float(parts[2])
    elif len(parts) == 2:
        seconds += int(parts[0]) * 60
        seconds += float(parts[1])
    return seconds

def format_time(seconds):
    """Convert seconds to MM:SS string"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def clean_tag_text(text):
    """Remove <tags> and strip"""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def parse_vtt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    events = []
    current_start = None
    
    # Simple state machine
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
            
        # Timestamp line: 00:00:02.320 --> 00:00:04.470 ...
        if '-->' in line:
            times = line.split('-->')
            start_str = times[0].strip().split(' ')[0] # handle align tags
            current_start = parse_time(start_str)
            continue
            
        # Text line (only if we have a timestamp)
        if current_start is not None:
            clean_text = clean_tag_text(line)
            if clean_text:
                events.append({'time': current_start, 'text': clean_text})

    return events

def stabilize_text(events):
    """
    Deduplicates overlapping subtitles (shingling).
    Returns a list of Char-Timestamp mappings? 
    Or cleaner: List of (Timestamp, Text_Fragment) where fragments are unique.
    """
    if not events:
        return []

    # Strategy: Maintain the "completely processed text" and "current visual line".
    # When new lines come in, check overlap with "current visual line".
    
    processed_chunks = [] # (time, text)
    
    last_visual_line = ""
    
    for i, e in enumerate(events):
        curr_text = e['text']
        curr_time = e['time']
        
        # 1. Exact duplicate or Prefix check (Growth)
        if curr_text == last_visual_line:
            continue
            
        if curr_text.startswith(last_visual_line) and len(last_visual_line) > 0:
            # "Hello" -> "Hello world". New part is " world"
            new_part = curr_text[len(last_visual_line):]
            # Use current time for the new part? Or keep old time?
            # Usually strict VTT growth implies the new word appeared NOW.
            # But the block start time is fixed. 
            # Let's assign the current block's time to the new fragment.
            if new_part:
                processed_chunks.append({'time': curr_time, 'text': new_part})
            last_visual_line = curr_text
            continue
            
        # 2. Suffix/Prefix Overlap (scrolling window)
        # last: "Hello world. It"
        # curr: "world. It is a"
        # Overlap: "world. It"
        
        # Find overlap
        overlap_len = 0
        # Optimization: only check reasonable overlap sizes
        max_check = min(len(last_visual_line), len(curr_text))
        for k in range(max_check, 0, -1):
            if last_visual_line.endswith(curr_text[:k]):
                overlap_len = k
                break
        
        if overlap_len > 0:
            new_part = curr_text[overlap_len:]
            if new_part:
                processed_chunks.append({'time': curr_time, 'text': new_part})
            last_visual_line = curr_text
        else:
            # No overlap, assume new sentence or distinct block
            # Add a space if it looks like prose
            sep = " " if last_visual_line and not last_visual_line.endswith("-") else ""
            processed_chunks.append({'time': curr_time, 'text': sep + curr_text})
            last_visual_line = curr_text
            
    return processed_chunks

def chunk_into_sentences(chunks):
    """
    Reconstructs full text but keeps track of timestamps for sentence starts.
    """
    # 1. Expand chunks into a character map: [(char, time), ...]
    char_map = []
    for c in chunks:
        t = c['time']
        txt = c['text']
        for char in txt:
            char_map.append((char, t))
            
    if not char_map:
        return []

    sentences = []
    current_sent_chars = []
    current_sent_start_time = char_map[0][1] # Default to first char time
    
    # Regex logic is harder on char stream. Let's do a simple pass.
    # We want to split on [.?!] followed by space or end.
    
    i = 0
    n = len(char_map)
    while i < n:
        char, time = char_map[i]
        
        # specific fix for the very first char of a sentence
        if not current_sent_chars:
            current_sent_start_time = time
            
        current_sent_chars.append(char)
        
        # Check end of sentence
        if char in ['.', '?', '!']:
            # Check if next char is space or EOF
            is_eos = False
            if i + 1 >= n:
                is_eos = True
            elif char_map[i+1][0] in [' ', '\n', '"', "'"]: 
                # Basic check. "Dr." problem exists but ignoring for recitation script simplicity.
                is_eos = True
            
            if is_eos:
                # Flush sentence
                sent_text = "".join(current_sent_chars).strip()
                if sent_text:
                    sentences.append({'time': current_sent_start_time, 'text': sent_text})
                current_sent_chars = []
                current_sent_start_time = None # Will set on next loop
                
        i += 1
        
    # Flush remaining
    if current_sent_chars:
        sent_text = "".join(current_sent_chars).strip()
        if sent_text:
            sentences.append({'time': current_sent_start_time or char_map[-1][1], 'text': sent_text})
            
    return sentences

def save_markdown(sentences, original_path):
    out_path = original_path
    if out_path.endswith('.vtt'):
        out_path = out_path[:-4]
    out_path += "_obsidian.md"
        
    with open(out_path, 'w', encoding='utf-8') as f:
        title = original_path.split('/')[-1].replace('.en.vtt', '')
        f.write(f"# {title}\n")
        f.write("\n> 💡 **Usage:** Click timestamp to jump (if supported) or just use as reference.\n\n")
        f.write("---\n\n") # Start separator
        
        count = 0
        section_size = 8 # Number of sentences per "Section"
        
        for s in sentences:
            ts_str = format_time(s['time'])
            text = s['text']
            
            # Obsidian friendly block quote or bold timestamp
            # Format: **[00:12]** This is the text.
            f.write(f"**[{ts_str}]** {text}\n\n")
            
            count += 1
            if count % section_size == 0:
                f.write("---\n\n")
                
    return out_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <vtt_file>")
        sys.exit(1)
        
    vtt_file = sys.argv[1]
    
    events = parse_vtt(vtt_file)
    chunks = stabilize_text(events)
    sentences = chunk_into_sentences(chunks)
    
    out_path = save_markdown(sentences, vtt_file)
    print(f"Done: {out_path}")
