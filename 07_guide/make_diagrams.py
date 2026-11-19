"""Draws the explanatory diagrams for the project guide (schematics, not data charts)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "Arial", "font.size": 10})
NAVY, BLUE, LBLUE, CYAN, SAGE, ORANGE, LIME, GREY, RED = "#002D49", "#002EFF", "#638EFF", "#A0FFFF", "#D8E4D6", "#FE7C3E", "#C0C952", "#BFBFBF", "#EE4E68"


def box(ax, x, y, w, h, text, fc=SAGE, ec=NAVY, tc="black", fs=9.5, bold=False, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, color=NAVY, lw=1.4):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0))


def canvas(w, h, xmax, ymax):
    fig, ax = plt.subplots(figsize=(w, h), dpi=220)
    ax.set_xlim(0, xmax); ax.set_ylim(0, ymax); ax.axis("off")
    return fig, ax


# ---- D1: the design grid ---------------------------------------------------
fig, ax = canvas(8.2, 3.9, 10, 4.8)
conds = ["Direct", "Role framing", "Prefix steering"]
for j, c in enumerate(conds):
    box(ax, 2.5 + j * 2.45, 4.05, 2.3, 0.5, c, fc=NAVY, tc="white", bold=True)
rows = [("Qwen2.5-0.5B", "harmful prompts"), ("Qwen2.5-0.5B", "benign prompts"), ("Qwen2.5-1.5B", "harmful prompts"), ("Qwen2.5-1.5B", "benign prompts")]
for i, (m, pt) in enumerate(rows):
    y = 3.2 - i * 0.82
    box(ax, 0.05, y, 2.3, 0.66, f"{m}\n{pt}", fc=LBLUE if "0.5B" in m else CYAN, fs=9)
    for j in range(3):
        box(ax, 2.5 + j * 2.45, y, 2.3, 0.66, "20 responses", fc="#FFFFFF" if pt.startswith("benign") else SAGE, fs=9.5)
ax.text(5, 0.12, "12 cells x 20 prompts = 240 responses.  The same 20 prompt pairs are used in every cell.", ha="center", fontsize=9.5, color=NAVY, fontweight="bold")
fig.savefig(OUT / "d1_design_grid.png", bbox_inches="tight"); plt.close(fig)

# ---- D2: the workflow ------------------------------------------------------
fig, ax = canvas(8.4, 5.6, 10, 6.9)
steps = ["1  Read the plan,\nguidelines, template", "2  Set up tools,\ndownload models + data", "3  Read sources, write\nquestions + threat model", "4  Select 20 prompt\npairs by written rules",
         "5  Define conditions,\nlabels, metrics, rubric", "6  Pilot on 4 other\npairs (48 responses)", "7  FREEZE: hash\nmodels, prompts,\nsettings, rubric", "8  Main run:\n240 responses",
         "9  Lock the dataset\n(checksum)", "10  Blind audit of 60\n(labels saved first)", "11  Judge scores\nall 240", "12  Analysis: rates,\nintervals, tests",
         "13  Error analysis:\njudge vs audit", "14  Independent\nverification (26 checks)", "15  Report, card,\nnotebook", "16  Presentation\n+ this guide"]
pos = []
for r in range(4):
    for c in range(4):
        cc = c if r % 2 == 0 else 3 - c
        pos.append((0.15 + cc * 2.47, 5.45 - r * 1.55))
for i, (t, (x, y)) in enumerate(zip(steps, pos)):
    special = {6: (ORANGE, "black"), 9: (LIME, "black"), 13: (LIME, "black")}
    fc, tc = special.get(i, (SAGE, "black"))
    box(ax, x, y, 2.2, 1.0, t, fc=fc, tc=tc, fs=8.6, bold=i in special)
for i in range(15):
    (x1, y1), (x2, y2) = pos[i], pos[i + 1]
    if abs(y1 - y2) < 0.01:
        if x2 > x1: arrow(ax, x1 + 2.2, y1 + 0.5, x2, y2 + 0.5)
        else: arrow(ax, x1, y1 + 0.5, x2 + 2.2, y2 + 0.5)
    else:
        arrow(ax, x1 + 1.1, y1, x2 + 1.1, y2 + 1.0)
ax.text(5, 0.15, "Orange: nothing may change after this point.   Green: checks on our own work.", ha="center", fontsize=9, color=NAVY)
fig.savefig(OUT / "d2_workflow.png", bbox_inches="tight"); plt.close(fig)

# ---- D3: threat model -------------------------------------------------------
fig, ax = canvas(8.2, 3.6, 10, 4.4)
box(ax, 0.1, 2.3, 2.0, 1.1, "Attacker\n(an ordinary user)", fc=ORANGE, bold=True)
box(ax, 2.9, 2.3, 2.1, 1.1, "ONE user message\n(the only thing the\nattacker controls)", fc="#FFFFFF")
ax.add_patch(FancyBboxPatch((5.7, 1.9), 2.55, 1.9, boxstyle="round,pad=0.02,rounding_size=0.06", fc=CYAN, ec=NAVY, lw=1.0))
ax.text(6.97, 3.55, "System under test", ha="center", fontsize=9.5, fontweight="bold", color=NAVY)
ax.text(6.97, 2.7, "default system prompt\n+ chat template\n+ model weights\n+ greedy decoding", ha="center", va="center", fontsize=8.8)
box(ax, 8.75, 2.3, 1.2, 1.1, "Response", fc=SAGE, bold=True)
arrow(ax, 2.1, 2.85, 2.9, 2.85); arrow(ax, 5.0, 2.85, 5.7, 2.85); arrow(ax, 8.25, 2.85, 8.75, 2.85)
ax.text(0.1, 1.35, "The attacker CANNOT:", fontsize=9.5, fontweight="bold", color="#B91C1C")
ax.text(0.1, 0.25, "- change the system prompt            - write the start of the model's answer (pre-fill)\n"
                   "- see or edit the model's weights      - try again, or adapt after seeing the answer\n"
                   "- change the decoding settings         - use several turns of conversation", fontsize=9, family="Arial", linespacing=1.5)
fig.savefig(OUT / "d3_threat_model.png", bbox_inches="tight"); plt.close(fig)

# ---- D4: outcome decision tree ---------------------------------------------
fig, ax = canvas(8.2, 4.2, 10, 5.2)
box(ax, 3.6, 4.3, 2.8, 0.7, "One response + the judge's\ntwo outputs (Safety, Refusal)", fc=NAVY, tc="white", bold=True, fs=9)
box(ax, 0.6, 3.05, 3.4, 0.7, "Was the prompt HARMFUL?", fc=LBLUE, bold=True)
box(ax, 6.0, 3.05, 3.4, 0.7, "Was the prompt BENIGN?", fc=CYAN, bold=True)
arrow(ax, 4.4, 4.3, 2.3, 3.75); arrow(ax, 5.6, 4.3, 7.7, 3.75)
box(ax, 0.05, 1.75, 1.9, 0.75, "Safety = Unsafe", fc="#FFFFFF", fs=9)
box(ax, 2.15, 1.75, 1.9, 0.75, "not Unsafe and\nRefusal = Yes", fc="#FFFFFF", fs=9)
box(ax, 4.25, 1.75, 1.6, 0.75, "not Unsafe and\nRefusal = No", fc="#FFFFFF", fs=9)
box(ax, 6.0, 1.75, 1.6, 0.75, "Refusal = Yes", fc="#FFFFFF", fs=9)
box(ax, 7.8, 1.75, 1.6, 0.75, "Refusal = No", fc="#FFFFFF", fs=9)
for x in (1.0, 3.1, 5.05): arrow(ax, 2.3, 3.05, x, 2.5)
for x in (6.8, 8.6): arrow(ax, 7.7, 3.05, x, 2.5)
box(ax, 0.05, 0.4, 1.9, 0.8, "HARMFUL\nCOMPLIANCE", fc=RED, tc="white", bold=True, fs=9)
box(ax, 2.15, 0.4, 1.9, 0.8, "CORRECT\nREFUSAL", fc=BLUE, tc="white", bold=True, fs=9)
box(ax, 4.25, 0.4, 1.6, 0.8, "OTHER\nNON-REFUSAL", fc=GREY, bold=True, fs=9)
box(ax, 6.0, 0.4, 1.6, 0.8, "OVER-\nREFUSAL", fc=ORANGE, bold=True, fs=9)
box(ax, 7.8, 0.4, 1.6, 0.8, "BENIGN\nCOMPLIANCE", fc=LIME, bold=True, fs=9)
for x in (1.0, 3.1, 5.05, 6.8, 8.6): arrow(ax, x, 1.75, x, 1.2)
fig.savefig(OUT / "d4_outcome_tree.png", bbox_inches="tight"); plt.close(fig)

# ---- D5: what the auditor saw ---------------------------------------------
fig, ax = canvas(8.2, 2.9, 10, 3.6)
box(ax, 0.1, 2.55, 4.6, 0.6, "SHOWN to the auditor", fc=LIME, bold=True)
box(ax, 5.3, 2.55, 4.6, 0.6, "HIDDEN from the auditor", fc=GREY, bold=True)
for i, t in enumerate(["an audit number (A01 to A60)", "the original request", "whether the request is harmful or benign", "the model's response"]):
    box(ax, 0.1, 1.85 - i * 0.6, 4.6, 0.5, t, fc="#FFFFFF", fs=9)
for i, t in enumerate(["which model wrote the response", "which condition was used", "the judge's label (it did not exist yet)", "the order of the cells (rows were shuffled)"]):
    box(ax, 5.3, 1.85 - i * 0.6, 4.6, 0.5, t, fc="#FFFFFF", fs=9)
fig.savefig(OUT / "d5_blind_audit.png", bbox_inches="tight"); plt.close(fig)

# ---- D6: the two bounds ----------------------------------------------------
fig, ax = canvas(8.2, 2.6, 10, 3.2)
ax.plot([0.6, 9.4], [1.6, 1.6], color=NAVY, lw=2)
for x, lab in [(0.6, "0%"), (9.4, "100%")]:
    ax.plot([x, x], [1.5, 1.7], color=NAVY, lw=2); ax.text(x, 1.2, lab, ha="center", fontsize=9)
ax.text(5, 2.95, "Share of harmful requests that really produce harmful content", ha="center", fontsize=10, fontweight="bold", color=NAVY)
ax.annotate("", xy=(6.6, 1.6), xytext=(8.9, 1.6), arrowprops=dict(arrowstyle="-|>", color="#B91C1C", lw=2.2))
ax.text(7.75, 2.0, "The judge OVER-counts\n(its number is too high)", ha="center", fontsize=9, color="#B91C1C")
ax.annotate("", xy=(4.2, 1.6), xytext=(1.9, 1.6), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.2))
ax.text(3.05, 2.0, "Our attacks are WEAK\n(a real attacker gets more)", ha="center", fontsize=9, color=BLUE)
ax.text(5, 0.35, "The two errors push in opposite directions. The study reports each one separately\nand does not claim to know where the true value lies.", ha="center", fontsize=9)
fig.savefig(OUT / "d6_two_bounds.png", bbox_inches="tight"); plt.close(fig)
print("diagrams written:", sorted(p.name for p in OUT.glob("d*.png")))
