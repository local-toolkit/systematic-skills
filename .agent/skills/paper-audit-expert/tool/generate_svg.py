from academic_svg import AcademicSVG

def generate():
    svg = AcademicSVG(width=1000, height=700, title="IncogniText: 基于对抗隐私属性保护的文本匿名化系统")
    
    # --- Layout Constants ---
    # 3 Columns
    COL1_X = 50
    COL2_X = 360
    COL3_X = 670
    COL_W = 280
    COL_H = 580
    Y_START = 80
    
    # --- Phase 1: Input (Blue Theme) ---
    svg.add_group(COL1_X, Y_START, COL_W, COL_H, "阶段一：输入与上下文", "(原始数据)", AcademicSVG.THEME_BLUE)
    
    # Nodes relative to global canvas for simplicity in this script
    # Input Text
    bx = COL1_X + 40
    by = Y_START + 80
    svg.add_box(bx, by, 200, 50, "原始文本 (x₀)", "User Text")
    
    # Attributes
    by += 100
    svg.add_box(bx, by, 200, 60, "隐私属性集合", "True: At | Target: Ag", fill="#e3f2fd", stroke="#2196f3")
    
    # Arrow Input -> Attr
    svg.add_arrow([(bx+100, by-50), (bx+100, by)], width="2")
    
    # Output to Phase 2
    svg.add_arrow([(bx+200, by+30), (COL2_X, by+30)], label="输入条件")


    # --- Phase 2: Logic Loop (Orange Theme) ---
    svg.add_group(COL2_X, Y_START, COL_W, COL_H, "阶段二：IncogniText 逻辑", "(对抗式迭代)", AcademicSVG.THEME_ORANGE)
    
    # Loop Container (Dashed)
    lx = COL2_X + 20
    ly = Y_START + 80
    svg.add_box(lx, ly, 240, 450, "", stroke="#ff9800", stroke_width="2", stroke_dashdata="5,5", fill="#fff")
    # Loop Label
    svg.add_box(lx+20, ly-15, 200, 30, "对抗迭代循环", fill="#fff3e0", stroke="#ff9800")
    
    # 1. Adversary Model (Top)
    cx = COL2_X + 140 # Center X of Col 2
    ay = ly + 50
    svg.add_box(cx-100, ay, 200, 50, "对抗模型 (M_adv)", "猜测属性 & 解释", fill="#ffebee", stroke="#d32f2f")
    
    # 2. Decision Diamond
    dy = ay + 100
    svg.add_diamond(cx, dy, 120, 60, "猜测 == 真实?")
    
    # Connect Adv -> Diamond
    svg.add_arrow([(cx, ay+50), (cx, dy-30)])

    # 3. Anonymizer (Bottom)
    ny = dy + 120
    svg.add_box(cx-100, ny, 200, 50, "匿名化模型 (M_anon)", "条件重写", fill="#e3f2fd", stroke="#1565c0")
    
    # Logic Paths
    
    # YES (Leak) -> Anonymizer
    # From Bottom of Diamond to Anonymizer Top
    # svg.add_arrow([(cx, dy+30), (cx, ny)], color="#d32f2f", label="是 (存在泄露)") 
    # Label manual placement
    svg.add_arrow([(cx, dy+30), (cx, ny)], color="#d32f2f")
    # Text
    # svg.root... 
    # Use helper in engine if possible, or simple placement? Engine matches reference which uses path+text.
    
    # NO (Safe) -> Output (Green Arrow)
    # Right of Diamond -> Phase 3
    svg.add_arrow([(cx+60, dy), (COL3_X, dy)], color="#2e7d32", width="2", label="否 (安全)")

    # Anonymizer -> Adversary (Loop Back)
    # Left of Anonymizer -> Left of Adversary
    # Path: Left Anon -> Left Loop -> Up -> Right -> Left Adv?
    # Simple Loop: Left Anon -> Up -> Left Adv
    svg.add_arrow([(cx-100, ny+25), (lx+10, ny+25), (lx+10, ay+25), (cx-100, ay+25)], dashed=True, color="#1565c0", label="迭代修正")


    # --- Phase 3: Output (Green Theme) ---
    svg.add_group(COL3_X, Y_START, COL_W, COL_H, "阶段三：输出成品", "(结果)", AcademicSVG.THEME_GREEN)
    
    oy = dy # Align with decision exit
    svg.add_box(COL3_X+40, oy-25, 200, 50, "安全文本 (X_safe)", "已去除隐私特征", fill="#fff", stroke="#2e7d32", stroke_width="2")
    
    # Downstream Utility
    svg.add_arrow([(COL3_X+140, oy+25), (COL3_X+140, oy+100)])
    svg.add_box(COL3_X+40, oy+100, 200, 50, "下游任务效用", "高语义保留", fill="#e8f5e9", stroke="#2e7d32")

    svg.save("IncogniText_architecture.svg")

if __name__ == "__main__":
    generate()
