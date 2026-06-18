# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'

fig, ax = plt.subplots(figsize=(16, 8.5))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')

# Title
ax.text(50, 97, 'Figure 1. End-to-End Computational Pipeline of the Behavioral Fairness Index (BFI)',
        ha='center', va='top', fontsize=18, fontweight='bold', color='#1a3e6e')
ax.text(50, 92.5, 'Five processing layers transforming raw Moodle logs into a fairness-aware intervention decision',
        ha='center', va='top', fontsize=13, color='#444', style='italic')

layers = [
    ('1', 'INPUT LAYER', 'Raw LMS (Moodle) Data', '#1f6fb2', '#dceaf5',
     ['Raw Moodle event logs', 'Timestamped actions', 'Submission traces']),
    ('2', 'FEATURE\nENGINEERING', 'Behavioral Signals', '#2e8b4f', '#dff0e5',
     ['F\u2081  Inactivity variance', 'F\u2082  Initial latency', 'F\u2083  Efficiency ratio',
      'F\u2084  Behavioral divergence', 'F\u2085  Vulnerability index']),
    ('3', 'MODEL LAYER', 'Prediction & Estimation', '#e08a1e', '#fcefd9',
     ['Random Forest \u2192 P\u1d62', 'Recovery estimator \u2192 R\u1d62', 'Golden Profile \u2192 G\u1d62']),
    ('4', 'MATHEMATICAL\nLAYER', 'BFI Computation', '#7a4fa3', '#ece4f3',
     ['Inputs: P\u1d62, R\u1d62, D\u0302\u1d62', 'BFI\u1d62 = \u03b1P\u1d62 + \u03b2R\u1d62 + \u03b3(1\u2212D\u0302\u1d62)',
      '\u03b1+\u03b2+\u03b3 = 1,  weights \u2265 0', 'Output \u2208 [0, 1]']),
    ('5', 'DECISION LAYER', 'Fairness-Aware Action', '#c0392b', '#fbe3e0',
     ['BFI \u2265 0.80 \u2192 Auto intervention', '0.60 \u2264 BFI < 0.80 \u2192 Review', 'BFI < 0.60 \u2192 No action']),
]

n = len(layers)
box_w = 16.5
gap = (100 - n*box_w) / (n+1)
y_top = 84; y_bot = 14
header_h = 9

centers = []
for i,(num,title,sub,c,fill,items) in enumerate(layers):
    x = gap + i*(box_w+gap)
    cx = x + box_w/2
    centers.append((x, cx))
    # main body
    body = FancyBboxPatch((x, y_bot), box_w, y_top-y_bot,
        boxstyle="round,pad=0.3,rounding_size=1.2", linewidth=2.5,
        edgecolor=c, facecolor=fill, zorder=2)
    ax.add_patch(body)
    # header band
    hdr = FancyBboxPatch((x, y_top-header_h), box_w, header_h,
        boxstyle="round,pad=0.3,rounding_size=1.2", linewidth=0,
        facecolor=c, zorder=3)
    ax.add_patch(hdr)
    # number circle
    circ = plt.Circle((x+2.4, y_top-header_h/2), 1.5, color='white', zorder=5)
    ax.add_patch(circ)
    ax.text(x+2.4, y_top-header_h/2, num, ha='center', va='center',
            fontsize=15, fontweight='bold', color=c, zorder=6)
    # header text (auto multi-line). Shift right to clear the number circle.
    n_lines = title.count('\n') + 1
    title_fs = 12.5 if n_lines == 1 else 10.5
    title_y = y_top - header_h/2 + (1.4 if n_lines == 1 else 1.9)
    sub_y   = y_top - header_h/2 + (-1.7 if n_lines == 1 else -2.6)
    ax.text(cx+1.9, title_y, title, ha='center', va='center',
            fontsize=title_fs, fontweight='bold', color='white', zorder=6,
            linespacing=0.95)
    ax.text(cx+1.9, sub_y, sub, ha='center', va='center',
            fontsize=9.2, color='white', style='italic', zorder=6)
    # items
    iy = y_top - header_h - 5
    step = (iy - y_bot - 3) / max(len(items),1)
    for j,it in enumerate(items):
        yy = iy - j*step - step/2 + 2
        chip = FancyBboxPatch((x+1.3, yy-2.4), box_w-2.6, 4.4,
            boxstyle="round,pad=0.15,rounding_size=0.8", linewidth=1.2,
            edgecolor=c, facecolor='white', zorder=4)
        ax.add_patch(chip)
        fs = 11 if len(it) < 26 else 9.6
        ax.text(cx, yy-0.2, it, ha='center', va='center', fontsize=fs,
                color='#222', zorder=5, fontweight='medium')

# arrows between layers
for i in range(n-1):
    x0 = centers[i][0]+box_w
    x1 = centers[i+1][0]
    ya = (y_top+y_bot)/2
    arr = FancyArrowPatch((x0+0.2, ya), (x1-0.2, ya),
        arrowstyle='-|>', mutation_scale=28, linewidth=3.2,
        color='#333', zorder=7)
    ax.add_patch(arr)

# bottom caption strip
ax.text(50, 8, 'The pipeline enforces Axioms A1\u2013A5 in the Mathematical Layer and the stability guarantees of Theorems T1\u2013T5,',
        ha='center', va='center', fontsize=11, color='#333')
ax.text(50, 4.5, 'producing a transparent, bounded, and interpretable fairness score that drives the three-tier intervention decision.',
        ha='center', va='center', fontsize=11, color='#333')

plt.tight_layout()
plt.savefig('Figure1_Pipeline_v2.png', dpi=300, bbox_inches='tight', facecolor='white')
print('saved Figure1_Pipeline_v2.png')
