"""Figure 1 - BFI pipeline (v3.2). Every label mirrors src/pipeline.py; see the asserts at the bottom."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({'font.family': 'DejaVu Sans', 'mathtext.fontset': 'dejavusans'})
INK, MUT, LINE = '#1f1f1f', '#5c5c58', '#9a9a95'
COL = ['#2a78d6', '#1baf7a', '#eda100', '#8a5cc7', '#eb6834']          # layer accents
TINT = ['#eaf2fc', '#e6f7f0', '#fdf4e0', '#f1ebf9', '#fdeee7']

W, H = 6.33, 3.75                                                         # inches (full text width)
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis('off')

cols = [(0.8, 14.2), (17.6, 17.4), (37.6, 23.6), (63.8, 16.8), (83.2, 16.0)]  # (x, width)
TOP, BOT, HEAD = 48.5, 1.0, 6.2
titles = [('1', 'Input'), ('2', 'Features'), ('3', 'Evidence'), ('4', 'Index'), ('5', 'Decision')]
subs = ['Moodle report', 'per session', 'three signals', 'Equation (3)', 'tiers and gate']

for i, ((x, w), (n, t)) in enumerate(zip(cols, titles)):
    ax.add_patch(FancyBboxPatch((x, BOT), w, TOP - BOT, boxstyle='round,pad=0,rounding_size=1.2',
                                fc=TINT[i], ec=COL[i], lw=1.2))
    ax.add_patch(FancyBboxPatch((x, TOP - HEAD), w, HEAD, boxstyle='round,pad=0,rounding_size=1.2',
                                fc=COL[i], ec=COL[i], lw=1.2))
    ax.text(x + 1.2, TOP - 2.5, f'{n}  {t}', color='white', fontsize=9.5, fontweight='bold', va='center')
    ax.text(x + 1.2, TOP - 4.9, subs[i], color='white', fontsize=6.6, va='center', style='italic')


SCALE = 0.86   # figure is drawn at print width (6.33 in); keeps every label inside its card

def card(x, y, w, h, lines, i, size=7.8, bold_first=False):
    size = size * SCALE
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.7',
                                fc='white', ec=COL[i], lw=0.8))
    n = len(lines); step = h / (n + 1)
    for k, ln in enumerate(lines):
        ax.text(x + w / 2, y + h - step * (k + 1), ln, ha='center', va='center', fontsize=size, color=INK,
                fontweight='bold' if (bold_first and k == 0) else 'normal')
    return (x, y, w, h)


# 1 Input
x, w = cols[0]
card(x + 1, 30.5, w - 2, 9.5, ['Start and end', 'timestamps'], 0)
card(x + 1, 18.5, w - 2, 9.5, ['Effective', 'duration'], 0)
card(x + 1, 6.5, w - 2, 9.5, ['Per-item', 'response', 'and score'], 0)

# 2 Features (aligned with the signals they feed)
x, w = cols[1]
fu = card(x + 1, 35.0, w - 2, 5.2, [r'$u$  unanswered share'], 1, size=7.0)
fl = card(x + 1, 28.8, w - 2, 5.2, [r'$\ell$  entry latency'], 1, size=7.0)
fs = card(x + 1, 22.6, w - 2, 5.2, [r'$s$  short session'], 1, size=7.0)
fn = card(x + 1, 14.2, w - 2, 5.2, [r'$u$ at next session'], 1, size=7.0)
fa = card(x + 1, 3.5, w - 2, 7.2, [r'$a$  answered-item', 'accuracy'], 1, size=7.0)

# 3 Evidence signals
x, w = cols[2]
sP = card(x + 1, 24.5, w - 2, 14.0, ['Disruption evidence', r'$P = 1-(1-u)(1-\tilde\ell)(1-s)$', r'$\tilde\ell=\min(\ell/30,\,1)$'], 2, bold_first=True)
sR = card(x + 1, 12.6, w - 2, 9.6, ['Recovery', r'$R = 1-u_{\mathrm{next}}$  (else 0.5)'], 2, bold_first=True)
sD = card(x + 1, 1.8, w - 2, 9.6, ['Divergence', r'$\hat D = |a-G|\,/\,(1+|a-G|)$', r'$G$: EMA of earlier $a$ ($\lambda$ = 0.5)'], 2, size=7.4, bold_first=True)

# 4 Index
x, w = cols[3]
card(x + 1, 22.0, w - 2, 17.0, ['Behavioral', 'Fairness Index', r'$\alpha P+\beta R$', r'$+\,\gamma\,[\,1-(1-P)\hat D\,]$'], 3, size=7.4, bold_first=False)
card(x + 1, 4.0, w - 2, 15.0, [r'$\alpha,\beta,\gamma>0$', r'$\alpha+\beta+\gamma=1$', 'Axioms A1–A6', r'BFI $\in[0,1]$'], 3, size=7.0)

# 5 Decision
x, w = cols[4]
card(x + 1, 30.0, w - 2, 10.0, [r'BFI $\geq$ 0.80', 'Automatic', 'compensation'], 4, size=7.4, bold_first=True)
card(x + 1, 17.0, w - 2, 11.0, [r'0.60 $\leq$ BFI < 0.80', r'and $P \geq$ 0.05', 'Instructor review'], 4, size=6.5, bold_first=True)
card(x + 1, 6.6, w - 2, 8.2, ['Otherwise', 'No action'], 4, size=7.4, bold_first=True)
ax.text(x + w / 2, 4.2, 'Each session also', ha='center', va='center', fontsize=6.4 * SCALE, color=MUT)
ax.text(x + w / 2, 2.4, r'reports $P, R, \hat D, \rho(s)$', ha='center', va='center', fontsize=6.4 * SCALE, color=MUT)


def link(a, b, rad=0.0):
    (x1, y1, w1, h1), (x2, y2, w2, h2) = a, b
    ax.add_patch(FancyArrowPatch((x1 + w1, y1 + h1 / 2), (x2, y2 + h2 / 2), arrowstyle='-|>', mutation_scale=7,
                                 lw=0.8, color=LINE, connectionstyle=f'arc3,rad={rad}', shrinkA=0.5, shrinkB=0.5))

for f in (fu, fl, fs):
    link(f, sP)
link(fn, sR); link(fa, sD)
# history note under a
ax.text(cols[2][0] + cols[2][1] / 2, 0.2, '', fontsize=1)

# layer-to-layer arrows
for i in range(4):
    xa = cols[i][0] + cols[i][1]; xb = cols[i + 1][0]
    if i == 1:   # features -> signals already linked individually
        continue
    ax.add_patch(FancyArrowPatch((xa + 0.2, 25), (xb - 0.2, 25), arrowstyle='-|>', mutation_scale=11, lw=1.6, color=INK))

# G note
ax.text(cols[2][0] + cols[2][1] / 2, 0.3, '', fontsize=1)

fig.savefig('Figure1_Pipeline.png', dpi=400)
fig.savefig('Figure1_Pipeline.pdf')
fig.savefig('Figure1_Pipeline.svg')
print('saved Figure1_Pipeline.{png,pdf,svg}')

# --- consistency checks against the implementation ---
import inspect, pipeline as pl
src = inspect.getsource(pl)
assert "np.clip(S.latency / 30, 0, 1)" in src                    # l-tilde = min(l/30, 1)
assert "(S.duration < 5) & (S.unans_ratio > 0)" in src            # short-session flag
assert "1 - (1 - u) * (1 - S.lat_n) * (1 - S.short)" in src      # P noisy-OR
assert "np.where(np.isnan(R), 0.5, R)" in src                    # R default 0.5
assert "D / (1 + D)" in src and "abs(S.acc[a] - G)" in src        # D-hat
assert "c * (1 - (1 - P) * Dhat)" in src                          # gated index
assert pl.TAU1 == 0.60 and pl.TAU2 == 0.80 and pl.P_GATE == 0.05
print('figure labels consistent with pipeline.py')
