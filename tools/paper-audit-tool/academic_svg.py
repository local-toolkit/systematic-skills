import xml.etree.ElementTree as ET

class AcademicSVG:
    """
    Academic SVG Engine v2
    Targeting 'SEAL Architecture' reference quality.
    Feature set: Groups, Microsoft YaHei typography, specific color palettes.
    """
    
    # Fonts
    FONT_MAIN = "'Microsoft YaHei', SimHei, sans-serif"
    
    # Palettes (Back, Border, Title, Text)
    THEME_BLUE =  {"fill": "#e3f2fd", "stroke": "#2196f3", "text_title": "#0d47a1", "text_body": "#0d47a1"}
    THEME_ORANGE = {"fill": "#fff3e0", "stroke": "#ff9800", "text_title": "#e65100", "text_body": "#e65100"}
    THEME_GREEN = {"fill": "#e8f5e9", "stroke": "#4caf50", "text_title": "#1b5e20", "text_body": "#1b5e20"}
    THEME_RED =   {"fill": "#ffebee", "stroke": "#d32f2f", "text_title": "#b71c1c", "text_body": "#b71c1c"}
    
    def __init__(self, width=1000, height=700, title="System Architecture"):
        self.width = width
        self.height = height
        self.root = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", viewBox=f"0 0 {width} {height}")
        self.defs = ET.SubElement(self.root, 'defs')
        self._add_markers()
        
        # Background
        ET.SubElement(self.root, 'rect', width=str(width), height=str(height), fill="#f8f9fa")
        
        # Main Title
        t = ET.SubElement(self.root, 'text', x=str(width/2), y="40", text_anchor="middle", fill="#333")
        t.set("font-family", self.FONT_MAIN)
        t.set("font-size", "24")
        t.set("font-weight", "bold")
        t.text = title

    def _add_markers(self):
        # Arrowhead
        marker = ET.SubElement(self.defs, 'marker', id="arrow", markerWidth="10", markerHeight="10", refX="9", refY="3", orient="auto", markerUnits="strokeWidth")
        ET.SubElement(marker, 'path', d="M0,0 L0,6 L9,3 z", fill="#333")
        
        # Conditional colors
        for c, name in [("#d32f2f", "red"), ("#2e7d32", "green"), ("#0d47a1", "blue")]:
             m = ET.SubElement(self.defs, 'marker', id=f"arrow-{name}", markerWidth="10", markerHeight="10", refX="9", refY="3", orient="auto", markerUnits="strokeWidth")
             ET.SubElement(m, 'path', d="M0,0 L0,6 L9,3 z", fill=c)

    def add_group(self, x, y, w, h, title, subtitle=None, theme=THEME_BLUE):
        """Draws a rounded background container with a header."""
        g = ET.SubElement(self.root, 'g', transform=f"translate({x}, {y})")
        
        # Container
        ET.SubElement(g, 'rect', x="0", y="0", width=str(w), height=str(h), rx="10", fill=theme["fill"], stroke=theme["stroke"], stroke_width="2")
        
        # Title
        t = ET.SubElement(g, 'text', x=str(w/2), y="30", text_anchor="middle", fill=theme["text_title"])
        t.set("font-family", self.FONT_MAIN)
        t.set("font-size", "18")
        t.set("font-weight", "bold")
        t.text = title
        
        # Subtitle
        if subtitle:
            st = ET.SubElement(g, 'text', x=str(w/2), y="50", text_anchor="middle", fill=theme["text_body"])
            st.set("font-family", self.FONT_MAIN)
            st.set("font-size", "12")
            st.text = subtitle
            
        return g # Return group to add children to, relative to x,y? 
        # Actually returning a wrapper object or letting user calculate global coords is easier for flat lists.
        # But for group-relative logic, we'd need a context. 
        # For simplicity in this script: Inputs are absolute coordinates, but visually "inside" the logical group areas.

    def add_box(self, x, y, w, h, text, subtext=None, fill="#fff", stroke="#333", stroke_width="1", stroke_dashdata=None):
        """Draws a standard process node."""
        g = ET.SubElement(self.root, 'g', transform=f"translate({x}, {y})")
        
        rect = ET.SubElement(g, 'rect', x="0", y="0", width=str(w), height=str(h), rx="5", fill=fill, stroke=stroke, stroke_width=stroke_width)
        if stroke_dashdata:
            rect.set("stroke-dasharray", stroke_dashdata)
            
        # Center Text
        lines = text.split('\n')
        base_y = h/2 + 5 if not subtext else h/2 - 5
        
        t = ET.SubElement(g, 'text', x=str(w/2), y=str(base_y), text_anchor="middle", fill="#000")
        t.set("font-family", self.FONT_MAIN)
        t.set("font-size", "14")
        if stroke_width == "2": t.set("font-weight", "bold") # bold for heavy boxes
        t.text = lines[0] # multiline support later if needed
        
        if subtext:
             st = ET.SubElement(g, 'text', x=str(w/2), y=str(base_y + 20), text_anchor="middle", fill="#555")
             st.set("font-family", self.FONT_MAIN)
             st.set("font-size", "11")
             st.text = subtext

    def add_diamond(self, cx, cy, w, h, text, fill="#fff9c4", stroke="#fbc02d"):
        """Draws a decision diamond."""
        g = ET.SubElement(self.root, 'g')
        pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
        ET.SubElement(g, 'polygon', points=pts, fill=fill, stroke=stroke, stroke_width="1.5")
        
        t = ET.SubElement(g, 'text', x=str(cx), y=str(cy+4), text_anchor="middle", fill="#333")
        t.set("font-family", self.FONT_MAIN)
        t.set("font-size", "12")
        t.text = text

    def add_arrow(self, points, color="#333", width="1.5", dashed=False, label=None):
        """Draws a connector with arrowhead."""
        p_str = " ".join([f"L{x},{y}" for x,y in points])
        d = f"M{points[0][0]},{points[0][1]} " + p_str[1:] # M x1,y1 L x2,y2 ...
        
        marker_id = "url(#arrow)"
        if color == "#d32f2f": marker_id = "url(#arrow-red)"
        if color == "#2e7d32": marker_id = "url(#arrow-green)"
        if color == "#0d47a1": marker_id = "url(#arrow-blue)"

        path = ET.SubElement(self.root, 'path', d=d, fill="none", stroke=color, stroke_width=width, marker_end=marker_id)
        if dashed:
            path.set("stroke-dasharray", "5,5")
            
        if label:
            # Simple label placement at midpoint of last segment? Or first?
            # Doing midpoint of overall list is complex. Let's do midpoint of *longest* segment or hardcode?
            # Let's assume label on middle of path.
            # Middle of the listed points is an approximation.
            mid = len(points) // 2
            p1 = points[mid-1]
            p2 = points[mid]
            mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
            
            # Label box/bg?
            t = ET.SubElement(self.root, 'text', x=str(mx+5), y=str(my), font_family=self.FONT_MAIN, font_size="11", fill=color)
            t.text = label

    def save(self, filename):
        tree = ET.ElementTree(self.root)
        ET.indent(tree)
        tree.write(filename, encoding="utf-8")
