"""
Figure 2 — Three-dimensional BFI fairness response surface.
Theoretical visualization generated directly from Equation (11):
    BFI(P, R; d) = alpha*P + beta*R + gamma*(1 - d)
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from bfi_iabft import BFIWeights, bfi, TAU1, TAU2

def main(out="Figure2_BFI_Surface.png"):
    w = BFIWeights()
    d = 0.20
    P = np.linspace(0, 1, 60)
    R = np.linspace(0, 1, 60)
    PP, RR = np.meshgrid(P, R)
    Z = bfi(PP, RR, d, w)
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(PP, RR, Z, cmap="RdYlGn", vmin=0, vmax=1,
                           edgecolor="none", alpha=0.95)
    for tau, c in [(TAU1, "orange"), (TAU2, "green")]:
        ax.plot_surface(PP, RR, np.full_like(Z, tau), color=c, alpha=0.12)
    ax.set_xlabel("P (Disruption Probability)")
    ax.set_ylabel("R (Recovery Score)")
    ax.set_zlabel("BFI")
    ax.set_zlim(0, 1)
    ax.set_title("Figure 2. BFI Fairness Response Surface (D_hat = 0.20)\n"
                 "Theoretical visualization from Equation (11)",
                 fontsize=11, fontweight="bold")
    fig.colorbar(surf, shrink=0.5, aspect=12, label="BFI Value")
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print("saved", out)

if __name__ == "__main__":
    main()
