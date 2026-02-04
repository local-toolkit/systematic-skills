#!/usr/bin/env python3
"""
Generate horizontal 3-layer system architecture SVG for IncogniText paper.
Uses AcademicSVG engine for high-quality academic visualization.
"""

import sys
sys.path.insert(0, '/Users/xujintao/Documents/workspace/systematic-skills/tools/paper-audit-tool')

from academic_svg import AcademicSVG

# Create SVG canvas
svg = AcademicSVG(width=1100, height=650, title="IncogniText: 隐私增强条件文本匿名化系统架构")

# ===== Layer 1: Input Layer (Left) =====
svg.add_group(30, 70, 280, 530, "输入层", "Input Layer", AcademicSVG.THEME_BLUE)

# Input components
svg.add_box(50, 120, 240, 50, "原始用户文本", "xorig", fill="#e3f2fd", stroke="#2196f3")
svg.add_box(50, 190, 240, 50, "目标属性值", "atarget", fill="#e3f2fd", stroke="#2196f3")
svg.add_box(50, 260, 240, 50, "真实属性值 (可选)", "atrue", fill="#bbdefb", stroke="#2196f3", stroke_dashdata="5,3")
svg.add_box(50, 330, 240, 50, "对抗模板", "Tadv", fill="#e3f2fd", stroke="#2196f3")
svg.add_box(50, 400, 240, 50, "匿名化模板", "Tanon", fill="#e3f2fd", stroke="#2196f3")
svg.add_box(50, 470, 240, 80, "属性类型", "age, gender, income,\noccupation, location...", fill="#e3f2fd", stroke="#2196f3")

# ===== Layer 2: Processing Layer (Center) =====
svg.add_group(340, 70, 420, 530, "处理层", "Processing/Logic Layer", AcademicSVG.THEME_ORANGE)

# Adversarial Model
svg.add_box(370, 130, 170, 60, "对抗模型", "Madv", fill="#fff3e0", stroke="#ff9800", stroke_width="2")
svg.add_box(550, 130, 180, 60, "推理 & 推断", "Reasoning R, Inference I", fill="#ffe0b2", stroke="#ff9800")

# Decision diamond
svg.add_diamond(460, 260, 80, 50, "I = atrue?", fill="#fff9c4", stroke="#fbc02d")

# Anonymization Model
svg.add_box(370, 310, 170, 60, "匿名化模型", "Manon", fill="#fff3e0", stroke="#ff9800", stroke_width="2")
svg.add_box(550, 310, 180, 60, "文本重写", "Conditional Rewriting", fill="#ffe0b2", stroke="#ff9800")

# Iterative loop indicator
svg.add_box(370, 400, 360, 50, "迭代循环: i = 1..n (早停机制)", "Adversarial Training Paradigm", fill="#ffecb3", stroke="#ffa000")

# LoRA Distillation (On-device)
svg.add_box(370, 470, 360, 55, "LoRA 知识蒸馏", "Qwen2-1.5B (On-device)", fill="#ffccbc", stroke="#e64a19", stroke_dashdata="5,3")

# Key innovation box
svg.add_box(370, 540, 360, 45, "核心创新: 条件化目标属性 + 对抗早停", None, fill="#fff8e1", stroke="#ff6f00", stroke_width="2")

# ===== Layer 3: Output Layer (Right) =====
svg.add_group(790, 70, 280, 530, "输出层", "Output Layer", AcademicSVG.THEME_GREEN)

# Output components
svg.add_box(810, 120, 240, 60, "匿名化文本", "xanon", fill="#e8f5e9", stroke="#4caf50", stroke_width="2")
svg.add_box(810, 200, 240, 50, "隐私保护", "↓90% 属性泄露", fill="#c8e6c9", stroke="#4caf50")
svg.add_box(810, 270, 240, 50, "效用保持", "ROUGE ~80%", fill="#c8e6c9", stroke="#4caf50")
svg.add_box(810, 340, 240, 50, "LLM效用判断", "Utility ~92%", fill="#c8e6c9", stroke="#4caf50")
svg.add_box(810, 410, 240, 80, "评估指标", "Privacy: 7.2%\nROUGE: 80.7%\nUtility: 92.2%", fill="#a5d6a7", stroke="#2e7d32", stroke_width="2")
svg.add_box(810, 510, 240, 50, "端侧模型部署", "On-device Ready", fill="#dcedc8", stroke="#689f38", stroke_dashdata="5,3")

# ===== Arrows / Connections =====
# Input to Processing
svg.add_arrow([(290, 145), (368, 160)], color="#2196f3", width="2")
svg.add_arrow([(290, 215), (360, 260)], color="#2196f3", width="1.5")
svg.add_arrow([(290, 430), (368, 340)], color="#2196f3", width="1.5")

# Inside Processing
svg.add_arrow([(540, 160), (548, 160)], color="#ff9800", width="2")
svg.add_arrow([(460, 190), (460, 235)], color="#ff9800", width="1.5")
svg.add_arrow([(460, 285), (460, 308)], color="#2e7d32", width="2", label="Yes")
svg.add_arrow([(500, 260), (788, 150)], color="#d32f2f", width="2", dashed=True, label="No → 早停")
svg.add_arrow([(540, 340), (548, 340)], color="#ff9800", width="2")

# Feedback loop
svg.add_arrow([(370, 380), (340, 380), (340, 160), (368, 160)], color="#ff6f00", width="1.5", dashed=True, label="迭代")

# Processing to Output
svg.add_arrow([(730, 340), (788, 150)], color="#4caf50", width="2.5")
svg.add_arrow([(760, 425), (808, 450)], color="#4caf50", width="2")

# Save SVG
output_path = "/Users/xujintao/Documents/workspace/systematic-skills/tools/paper_audit/notes/IncogniText_architecture.svg"
svg.save(output_path)
print(f"SVG saved to: {output_path}")
