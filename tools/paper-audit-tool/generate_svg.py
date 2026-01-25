import xml.etree.ElementTree as ET

def create_svg():
    # Constants
    WIDTH = 800
    HEIGHT = 400
    BG_COLOR = "#ffffff"
    STROKE_COLOR = "#000000"
    FILL_COLOR_LIGHT = "#f8f9fa"
    FILL_COLOR_HIGHLIGHT = "#e3f2fd" # Light Blue
    FILL_COLOR_WARN = "#fff3cd" # Light Yellow
    TEXT_COLOR = "#000000"
    FONT_FAMILY = "Arial, sans-serif"
    
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1", width=str(WIDTH), height=str(HEIGHT))
    
    # Background
    ET.SubElement(svg, 'rect', x="0", y="0", width=str(WIDTH), height=str(HEIGHT), fill=BG_COLOR)

    # Styles
    defs = ET.SubElement(svg, 'defs')
    style = ET.SubElement(defs, 'style')
    style.text = f"""
        .box {{ fill: {FILL_COLOR_LIGHT}; stroke: {STROKE_COLOR}; stroke-width: 2; rx: 5; ry: 5; }}
        .highlight {{ fill: {FILL_COLOR_HIGHLIGHT}; stroke: {STROKE_COLOR}; stroke-width: 2; rx: 5; ry: 5; }}
        .decision {{ fill: {FILL_COLOR_WARN}; stroke: {STROKE_COLOR}; stroke-width: 2; rx: 0; ry: 0; transform: rotate(45deg); }}
        .label {{ font-family: {FONT_FAMILY}; font-size: 14px; text-anchor: middle; fill: {TEXT_COLOR}; }}
        .sublabel {{ font-family: {FONT_FAMILY}; font-size: 10px; text-anchor: middle; fill: {TEXT_COLOR}; }}
        .title {{ font-family: {FONT_FAMILY}; font-size: 16px; font-weight: bold; text-anchor: middle; fill: {TEXT_COLOR}; }}
        .arrow {{ stroke: {STROKE_COLOR}; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }}
    """
    
    # Marker for arrow
    marker = ET.SubElement(defs, 'marker', id="arrowhead", markerWidth="10", markerHeight="7", refX="9", refY="3.5", orient="auto")
    ET.SubElement(marker, 'polygon', points="0 0, 10 3.5, 0 7", fill=STROKE_COLOR)

    # --- Layout ---
    
    # Layer Titles (Horizontal)
    ET.SubElement(svg, 'text', x="100", y="30", class_="title").text = "INPUT LAYER"
    ET.SubElement(svg, 'text', x="400", y="30", class_="title").text = "INCOGNITEXT LOOP (Logic)"
    ET.SubElement(svg, 'text', x="700", y="30", class_="title").text = "OUTPUT LAYER"
    
    # Separators
    ET.SubElement(svg, 'line', x1="200", y1="50", x2="200", y2="350", stroke="#cccccc", stroke_dasharray="5,5")
    ET.SubElement(svg, 'line', x1="600", y1="50", x2="600", y2="350", stroke="#cccccc", stroke_dasharray="5,5")

    # --- Input Layer ---
    # Nodes: Original Text, True Attr, Target Attr
    inputs_g = ET.SubElement(svg, 'g')
    
    # Box 1: Original Text
    ET.SubElement(inputs_g, 'rect', x="30", y="100", width="140", height="40", class_="box")
    ET.SubElement(inputs_g, 'text', x="100", y="125", class_="label").text = "User Text (X)"
    
    # Box 2: Attributes
    ET.SubElement(inputs_g, 'rect', x="30", y="180", width="140", height="60", class_="box")
    ET.SubElement(inputs_g, 'text', x="100", y="205", class_="label").text = "Attributes"
    ET.SubElement(inputs_g, 'text', x="100", y="225", class_="sublabel").text = "True (A_true) & Target (A_target)"

    # --- Output Layer ---
    ET.SubElement(svg, 'rect', x="630", y="140", width="140", height="50", class_="highlight")
    ET.SubElement(svg, 'text', x="700", y="170", class_="label").text = "Anonymized Text"
    
    # --- Middle Layer (IncogniText Loop) ---
    loop_g = ET.SubElement(svg, 'g')
    
    # Adversary Model
    ET.SubElement(loop_g, 'rect', x="250", y="100", width="120", height="50", class_="highlight")
    ET.SubElement(loop_g, 'text', x="310", y="130", class_="label").text = "Adversary (M_adv)"
    
    # Decision Diamond (Is Guess Correct?)
    # Center at 400, 125
    # Diamond shape using path or rect with rotate. 
    # To simplify without complex transforms affecting text, I'll draw a path.
    # Top: 400,100; Right: 430,125; Bottom: 400,150; Left: 370,125  Wait, need room.
    # Center it below Adversary maybe? Or to the right.
    # Flow: Adversary -> Guess -> Check.
    
    # Let's adjust positions for a loop.
    # Adversary (Top) -> Check (Right) -> (No: Output) / (Yes: Anonymizer (Bottom)) -> Loop back
    
    # New Coords Middle Layer:
    # Adversary: x=250, y=80
    
    # Decision: x=420, y=80 (Center)
    ET.SubElement(loop_g, 'polygon', points="420,80 460,105 420,130 380,105", fill=FILL_COLOR_WARN, stroke=STROKE_COLOR, stroke_width="2")
    ET.SubElement(loop_g, 'text', x="420", y="100", class_="sublabel").text = "Guess =="
    ET.SubElement(loop_g, 'text', x="420", y="115", class_="sublabel").text = "A_true?"
    
    # Anonymizer (Bottom)
    ET.SubElement(loop_g, 'rect', x="300", y="250", width="140", height="50", class_="highlight")
    ET.SubElement(loop_g, 'text', x="370", y="280", class_="label").text = "Anonymizer (M_anon)"
    
    # Connections
    
    # Input -> Adversary
    ET.SubElement(svg, 'path', d="M 170 120 L 250 125", class_="arrow") # Text -> Adv
    
    # Adversary -> Decision
    ET.SubElement(svg, 'path', d="M 370 125 L 380 105", class_="arrow") # Approx path (Rect to Diamond) -> Fixed: 370 is close to 380.
    # Let's clean up logic.
    # Adversary is 250(x) to 370(x). Decision starts at 380.
    ET.SubElement(svg, 'line', x1="370", y1="125", x2="380", y2="105", class_="arrow") 
    # Actually direct line center to center is better?
    # Adv Center: 310, 125. Decision Center: 420, 105.
    ET.SubElement(svg, 'line', x1="370", y1="125", x2="380", y2="105", stroke=STROKE_COLOR, stroke_width="2") # Correcting arrow placement is tricky without math.
    
    # Let's redraw simpler Layout
    # Row 1: Input(170) -> Adversary(220-340) -> Decision(360-440) -> Output(630)
    # Row 2: Anonymizer (Below)
    
    # Clearer Layout:
    # 1. Inputs (Left)
    # 2. Adversary (Top Middle)
    # 3. Decision (Right Middle)
    # 4. Anonymizer (Bottom Middle)
    # 5. Output (Far Right)
    
    # Re-declare elements for clean code
    
    # Input Lines
    ET.SubElement(svg, 'line', x1="170", y1="120", x2="250", y2="125", class_="arrow") # Text -> Adv (Adjusted)
    
    # Adv -> Decision
    ET.SubElement(svg, 'line', x1="370", y1="125", x2="380", y2="105", marker_end="url(#arrowhead)", stroke=STROKE_COLOR, stroke_width="2", display="none") # manual override
    
    # Proper Paths
    # Input -> Adv
    ET.SubElement(svg, 'path', d="M 170 120 L 250 125", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)")
    
    # Adv -> Decision
    ET.SubElement(svg, 'path', d="M 370 125 L 380 105", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)")
    
    # Decision -> Output (No / False) -> Guess != True (Success for privacy!)
    # Wait, loop stops when Guess != True?
    # Paper: "The iterative application... is executed as long as the inference I... matches... A_true".
    # So: If Guess == True -> Anonymize again.
    # If Guess != True -> Stop (Success).
    
    # Decision (Yes/True) -> Anonymizer
    ET.SubElement(svg, 'text', x="450", y="150", class_="sublabel").text = "Yes (Leak)"
    ET.SubElement(svg, 'path', d="M 420 130 L 420 250 L 440 275", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)", fill="none") # Down to Anonymizer
    
    # Decision (No/False) -> Output
    ET.SubElement(svg, 'text', x="500", y="90", class_="sublabel").text = "No (Safe)"
    ET.SubElement(svg, 'path', d="M 460 105 L 630 165", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)")
    
    # Anonymizer -> Adversary (Loop Back)
    ET.SubElement(svg, 'path', d="M 300 275 L 200 275 L 200 150 L 250 140", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)", fill="none", stroke_dasharray="5,5")
    ET.SubElement(svg, 'text', x="230", y="260", class_="sublabel").text = "Iterative Refinement"

    # Inputs -> Anonymizer (Conditioning)
    ET.SubElement(svg, 'path', d="M 170 210 L 300 260", stroke=STROKE_COLOR, stroke_width="2", marker_end="url(#arrowhead)", stroke_dasharray="2,2")
    ET.SubElement(svg, 'text', x="230", y="230", class_="sublabel").text = "Target / True Attr"

    tree = ET.ElementTree(svg)
    tree.write("IncogniText_architecture.svg")

if __name__ == "__main__":
    create_svg()
