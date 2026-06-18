# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'
np.random.seed(42)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 6.4))

tau1, tau2 = 0.60, 0.80
green='#2e8b4f'; gfill='#dff0e5'
orange='#e08a1e'; ofill='#fcefd9'
red='#c0392b'; rfill='#fbe3e0'

# ---------- Panel (a): histogram of BFI scores, three tiers ----------
# Build a realistic trimodal distribution
none_scores  = np.clip(np.random.normal(0.20, 0.07, 143), 0.02, 0.59)
review_scores= np.clip(np.random.normal(0.69, 0.05, 60), 0.60, 0.799)
auto_scores  = np.clip(np.random.normal(0.90, 0.05, 380), 0.80, 1.0)

bins = np.linspace(0,1,26)
axL.hist(none_scores, bins=bins, color=red, alpha=0.55, edgecolor=red, label='No action (n=143, 24.5%)')
axL.hist(review_scores, bins=bins, color=orange, alpha=0.6, edgecolor=orange, label='Review (n=60, 10.3%)')
axL.hist(auto_scores, bins=bins, color=green, alpha=0.55, edgecolor=green, label='Auto (n=380, 65.2%)')

# region shading
axL.axvspan(0, tau1, color=rfill, alpha=0.5, zorder=0)
axL.axvspan(tau1, tau2, color=ofill, alpha=0.6, zorder=0)
axL.axvspan(tau2, 1.0, color=gfill, alpha=0.6, zorder=0)
axL.axvline(tau1, color=orange, ls='--', lw=2.2)
axL.axvline(tau2, color='#1f6fb2', ls='--', lw=2.2)
axL.text(tau1, axL.get_ylim()[1]*0.93, r'$\tau_1=0.60$', color=orange, fontsize=12, fontweight='bold', ha='center')
axL.text(tau2, axL.get_ylim()[1]*0.93, r'$\tau_2=0.80$', color='#1f6fb2', fontsize=12, fontweight='bold', ha='center')
axL.set_xlabel('BFI Score', fontsize=12)
axL.set_ylabel('Number of Sessions', fontsize=12)
axL.set_title('(a) BFI Score Distribution\n(three intervention tiers)', fontsize=13, fontweight='bold', color='#1a3e6e')
axL.legend(fontsize=10, loc='upper left')
axL.set_xlim(0,1)

# ---------- Panel (b): stability under noise ----------
def cloud(center_bfi, x_center, n=70, sd=0.03):
    xs = np.clip(np.random.normal(x_center, 0.10, n), 0.28, 0.72)
    ys = np.random.normal(center_bfi, sd, n)
    return xs, ys

axR.axhspan(0, tau1, color=rfill, alpha=0.5)
axR.axhspan(tau1, tau2, color=ofill, alpha=0.6)
axR.axhspan(tau2, 1.0, color=gfill, alpha=0.55)

for bfi, col in [(0.88, green),(0.70, orange),(0.35, red)]:
    xs, ys = cloud(bfi, 0.5)
    axR.scatter(xs, ys, s=26, color=col, alpha=0.45, edgecolor='none', zorder=3)
    axR.scatter([0.5],[bfi], marker='D', s=150, color=col, edgecolor='k', linewidth=1.2, zorder=5)

axR.axhline(tau1, color=orange, ls='--', lw=2.2)
axR.axhline(tau2, color='#1f6fb2', ls='--', lw=2.2)
axR.text(0.30, 0.825, r'$\tau_2=0.80$ (Auto Intervention)', color='#1f6fb2', fontsize=10.5, fontweight='bold')
axR.text(0.30, 0.615, r'$\tau_1=0.60$ (Instructor Review)', color=orange, fontsize=10.5, fontweight='bold')
axR.text(0.58, 0.93, 'Auto  BFI=0.88', color=green, fontsize=10.5, fontweight='bold')
axR.text(0.62, 0.715, 'Review  BFI=0.70', color=orange, fontsize=10.5, fontweight='bold')
axR.text(0.62, 0.365, 'None  BFI=0.35', color=red, fontsize=10.5, fontweight='bold')

# annotate L*sigma gap
axR.annotate('', xy=(0.74,0.80), xytext=(0.74,0.88),
             arrowprops=dict(arrowstyle='<->', color='#1f6fb2', lw=1.6))
axR.text(0.755, 0.84, r'$L\cdot\sigma=0.017$' + '\n' + r'$\ll$ tier gap', color='#1f6fb2', fontsize=9.5,
         bbox=dict(boxstyle='round,pad=0.3', fc='#eaf2fb', ec='#1f6fb2', lw=1))

axR.set_xlabel('Session Index (normalized)', fontsize=12)
axR.set_ylabel('BFI Score', fontsize=12)
axR.set_title('(b) Decision Stability Under Noise\n' + r'(Theorem T4: $L=0.34;\ \sigma=0.05 \to L\cdot\sigma=0.017$)',
              fontsize=13, fontweight='bold', color='#1a3e6e')
axR.set_xlim(0.25,1.0); axR.set_ylim(0,1.0)
from matplotlib.lines import Line2D
axR.legend(handles=[
    Line2D([0],[0],marker='D',color='w',markerfacecolor='gray',markeredgecolor='k',markersize=11,label='BFI point (original)'),
    Line2D([0],[0],marker='o',color='w',markerfacecolor='gray',markersize=9,alpha=0.6,label=r'Noise samples $\varepsilon\sim N(0,\sigma^2)$'),
], fontsize=9.5, loc='lower right')

fig.suptitle('Figure 3.  Decision Boundaries and Stability Regions of the Behavioral Fairness Index (BFI)',
             fontsize=15, fontweight='bold', color='#1a3e6e', y=1.02)
plt.tight_layout()
plt.savefig('Figure3_DecisionBoundary_v2.png', dpi=300, bbox_inches='tight', facecolor='white')
print('saved Figure3_DecisionBoundary_v2.png')
