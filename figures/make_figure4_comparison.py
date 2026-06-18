import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

# Capability comparison heatmap: approaches x capabilities
approaches = ['Demographic\nParity\n(Dwork+ 2012)',
              'Equalized\nOdds\n(Hardt+ 2016)',
              'Counterfactual\nFairness\n(Kusner+ 2017)',
              'LA Bias\nMitigation\n(Deho+ 2022)',
              'BFI / IABFT\n(This work)']
caps = ['Individual-level\nfairness',
        'No reliance on\ngroup labels',
        'Infrastructure-\naware',
        'Temporal /\ndynamic profile',
        'Recovery\ncompensation',
        'Formal axioms\n+ proofs',
        'Lipschitz\nstability guarantee',
        'Bounded &\ninterpretable score']

# scores: 0 = no, 0.5 = partial, 1 = yes
M = np.array([
 [0,0,0,0,0,1,0,1],     # DP
 [0,0,0.5,0,0,1,0,1],   # EO
 [1,0.5,0,0,0,1,0,0.5], # Counterfactual
 [0.5,0,0,0.5,0,0.5,0.5,0.5], # LA mitigation
 [1,1,1,1,1,1,1,1],     # BFI
], dtype=float)

cmap = LinearSegmentedColormap.from_list('rg', ['#d94f4f','#f4d35e','#2e9e5b'])

fig, ax = plt.subplots(figsize=(11.5,6.2))
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect='auto')

ax.set_xticks(range(len(caps)))
ax.set_xticklabels(caps, fontsize=9)
ax.set_yticks(range(len(approaches)))
ax.set_yticklabels(approaches, fontsize=9.5)
ax.set_xticks(np.arange(-.5, len(caps), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(approaches), 1), minor=True)
ax.grid(which='minor', color='white', linewidth=2.5)
ax.tick_params(which='minor', length=0)
ax.tick_params(axis='x', length=0)

sym = {0:'\u2014', 0.5:'\u25d1', 1:'\u2713'}
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i,j]
        ax.text(j, i, sym[v], ha='center', va='center',
                fontsize=13, color='white', fontweight='bold')

# highlight BFI row
ax.add_patch(mpatches.Rectangle((-.5, 4-.5), len(caps), 1, fill=False,
              edgecolor='#1a3e6e', linewidth=3))

ax.set_title('Figure 4. Capability Comparison of BFI (IABFT) Against Prior Fairness Approaches',
             fontsize=12.5, fontweight='bold', color='#1a3e6e', pad=16)

legend_handles = [
    mpatches.Patch(color='#2e9e5b', label='\u2713  Fully supported'),
    mpatches.Patch(color='#f4d35e', label='\u25d1  Partially supported'),
    mpatches.Patch(color='#d94f4f', label='\u2014  Not supported'),
]
ax.legend(handles=legend_handles, loc='upper center',
          bbox_to_anchor=(0.5,-0.16), ncol=3, frameon=False, fontsize=9.5)

plt.tight_layout()
plt.savefig('Figure4_Comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
print('saved Figure4_Comparison.png')
