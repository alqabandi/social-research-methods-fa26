"""Build the Chapter 7 bilingual SVG figures.

Run from this folder:  python3 build_figures.py
Layouts are written once in left-to-right coordinates; Arabic variants are
mirrored horizontally so the reading order runs right to left.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent

NAVY, TEAL, TEAL2 = "#1B2A4A", "#147D79", "#2A9D8F"
GOLD, GOLD2, CORAL, CORAL2 = "#A47712", "#E9C46A", "#C65D4B", "#E76F51"
GRAY, INK, MUTED, LINE = "#F5F7F8", "#25313D", "#6F7985", "#D5DCE3"
NAVY_T, TEAL_T, GOLD_T, CORAL_T = "#EEF2F7", "#EAF6F5", "#FFF7E3", "#FBEDEA"
PALE_GOLD = "#F2D77E"

EN_FONT = "Arial, Helvetica, sans-serif"
AR_FONT = 'Arial, "Noto Sans Arabic", sans-serif'


class Fig:
    def __init__(self, lang, w=1200, h=650):
        self.ar = lang == "ar"
        self.lang = lang
        self.w, self.h = w, h
        self.parts = []
        self.defs = []

    # ---- coordinates -------------------------------------------------
    def mx(self, x):
        return self.w - x if self.ar else x

    def L(self, en, ar):
        return ar if self.ar else en

    # ---- primitives --------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=0, rx=0, dash=None, opacity=None):
        x0 = self.w - x - w if self.ar else x
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def circle(self, cx, cy, r, fill="none", stroke="none", sw=0, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{self.mx(cx):.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{extra}/>')

    def path(self, cmds, fill="none", stroke="none", sw=0, dash=None, marker=None, cap="round"):
        """cmds: list of tuples like ('M', x, y), ('C', x1, y1, x2, y2, x, y), ('Z',)."""
        out = []
        for c in cmds:
            op, nums = c[0], list(c[1:])
            if op == "H":
                nums = [self.mx(n) for n in nums]
            elif op != "V":
                for i in range(0, len(nums), 2):
                    nums[i] = self.mx(nums[i])
            out.append(op + " " + " ".join(f"{n:.1f}" for n in nums))
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        extra += f' marker-end="url(#{marker})"' if marker else ""
        self.add(f'<path d="{" ".join(out)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                 f'stroke-linecap="{cap}" stroke-linejoin="round"{extra}/>')

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=2, dash=None, marker=None):
        self.path([("M", x1, y1), ("L", x2, y2)], stroke=stroke, sw=sw, dash=dash, marker=marker)

    def text(self, x, y, lines, size=22, fill=INK, weight="normal", anchor="middle", lh=1.22,
             italic=False, opacity=None, latin=False):
        if isinstance(lines, str):
            lines = [lines]
        x = self.mx(x)
        style = ""
        if italic and not self.ar:
            style += ' font-style="italic"'
        if opacity is not None:
            style += f' opacity="{opacity}"'
        if latin and self.ar:
            style += ' direction="ltr" unicode-bidi="embed"'
            # an LTR run inside the RTL figure keeps its mirrored anchor meaning
            anchor = {"start": "end", "end": "start"}.get(anchor, anchor)
        spans = []
        for i, ln in enumerate(lines):
            dy = 0 if i == 0 else size * lh
            spans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{escape(ln)}</tspan>')
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                 f'font-weight="{weight}" text-anchor="{anchor}"{style}>{"".join(spans)}</text>')

    # ---- icons (symmetric shapes: only the anchor is mirrored) -------
    def person(self, cx, cy, s=1.0, fill=NAVY, ghost=False, letter=None, cap=False):
        x = self.mx(cx)
        if ghost:
            paint = f'fill="none" stroke="#B8C0C8" stroke-width="{1.6}" stroke-dasharray="4 3"'
        else:
            paint = f'fill="{fill}"'
        self.add(f'<circle cx="{x:.1f}" cy="{cy - 13 * s:.1f}" r="{8.5 * s:.1f}" {paint}/>')
        d = (f"M {x - 14 * s:.1f} {cy + 18 * s:.1f} V {cy + 6 * s:.1f} "
             f"Q {x - 14 * s:.1f} {cy - 3 * s:.1f} {x:.1f} {cy - 3 * s:.1f} "
             f"Q {x + 14 * s:.1f} {cy - 3 * s:.1f} {x + 14 * s:.1f} {cy + 6 * s:.1f} "
             f"V {cy + 18 * s:.1f} Z")
        self.add(f'<path d="{d}" {paint}/>')
        if cap:
            pts = [(x - 12 * s, cy - 21 * s), (x, cy - 26 * s), (x + 12 * s, cy - 21 * s), (x, cy - 16.5 * s)]
            self.add('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
                     + f'" fill="{NAVY}" stroke="#FFFFFF" stroke-width="1"/>')
        if letter:
            self.add(f'<text x="{x:.1f}" y="{cy + 12.5 * s:.1f}" font-size="{13 * s:.1f}" fill="#FFFFFF" '
                     f'font-weight="bold" text-anchor="middle">{escape(letter)}</text>')

    def house(self, cx, cy, color, roof, members, s=1.0):
        x = self.mx(cx)
        self.add(f'<g transform="translate({x:.1f} {cy:.1f}) scale({s})">'
                 f'<rect x="-30" y="-10" width="60" height="32" rx="3" fill="#FFFFFF" stroke="{color}" stroke-width="2.5"/>'
                 f'<polygon points="-37,-9 0,-31 37,-9" fill="{roof}" stroke="{color}" stroke-width="2.5" '
                 f'stroke-linejoin="round"/></g>')
        n = len(members)
        step = 13
        start = cx - step * (n - 1) / 2
        for i, m in enumerate(members):
            s = 0.42 if m == "a" else 0.31
            yy = cy + 12 if m == "a" else cy + 14.5
            self.person(start + step * i, yy, s=s, fill=color)

    # ---- output ------------------------------------------------------
    def marker_defs(self):
        out = []
        for name, col in (("navy", NAVY), ("teal", TEAL), ("coral", CORAL), ("muted", MUTED), ("gold", GOLD)):
            out.append(f'<marker id="ah-{name}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" '
                       f'markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{col}"/></marker>')
        return out

    def save(self, name, title, desc):
        font = AR_FONT if self.ar else EN_FONT
        rtl = ' direction="rtl"' if self.ar else ""
        head = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="t d" '
                f'xml:lang="{self.lang}" lang="{self.lang}"{rtl} font-family=\'{font}\'>\n'
                f'<title id="t">{escape(title)}</title>\n<desc id="d">{escape(desc)}</desc>\n'
                f'<defs>{"".join(self.marker_defs() + self.defs)}</defs>\n'
                f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#FFFFFF"/>\n')
        body = "\n".join(self.parts)
        (OUT / f"{name}_{self.lang}.svg").write_text(head + body + "\n</svg>\n", encoding="utf-8")


# =====================================================================
# 1. Survey workflow
# =====================================================================
def survey_workflow(lang):
    f = Fig(lang, 1200, 800)
    L = f.L
    phases = [
        (NAVY, NAVY_T, L("Phase 1", "المرحلة 1"),
         L(["Question &", "concepts"], ["السؤال", "والمفاهيم"]),
         L("What do we want to know?", "ماذا نريد أن نعرف؟"),
         [(1, L(["Define the", "problem"], ["تحديد المشكلة"])),
          (2, L(["Questions &", "hypotheses"], ["الأسئلة والفروض"])),
          (3, L(["Operational", "definitions"], ["التعريف الإجرائي", "للمتغيرات"])),
          (4, L(["Research plan"], ["خطة البحث"]))]),
        (TEAL, TEAL_T, L("Phase 2", "المرحلة 2"),
         L(["Population, sample", "& instrument"], ["المجتمع والعينة", "والأداة"]),
         L("How will we know?", "كيف سنعرف؟"),
         [(5, L(["Population,", "unit & sample"], ["المجتمع والوحدة", "ونمط العينة"])),
          (6, L(["Instruments &", "measures"], ["الأدوات", "والمقاييس"])),
          (7, L(["Analysis plan"], ["خطة التحليل"]))]),
        (GOLD, GOLD_T, L("Phase 3", "المرحلة 3"),
         L(["Pretest &", "fieldwork"], ["الاختبار الأولي", "والعمل الميداني"]),
         L("Does it work in the field?", "هل تنجح في الميدان؟"),
         [(8, L(["Pretest &", "train the team"], ["اختبار أولي", "وتدريب الفريق"])),
          (9, L(["Collect data"], ["جمع البيانات"]))]),
        (CORAL, CORAL_T, L("Phase 4", "المرحلة 4"),
         L(["Analysis &", "reporting"], ["التحليل", "والتفسير والتقرير"]),
         L("What does it mean?", "ماذا تعني النتائج؟"),
         [(10, L(["Analyze"], ["التحليل"])),
          (11, L(["Interpret"], ["التفسير"])),
          (12, L(["Write the", "report"], ["كتابة التقرير"]))]),
    ]
    colw, gap, x0 = 261, 36, 24
    for i, (col, tint, ph, name, q, steps) in enumerate(phases):
        cx = x0 + i * (colw + gap)
        f.rect(cx, 24, colw, 700, fill=tint, rx=18)
        f.rect(cx, 24, colw, 108, fill=col, rx=18)
        f.rect(cx, 104, colw, 28, fill=col)
        f.text(cx + colw / 2, 54, ph, size=17, fill=PALE_GOLD if col != GOLD else "#FFF3CF", weight="bold")
        f.text(cx + colw / 2, 84, name, size=21, fill="#FFFFFF", weight="bold", lh=1.15)
        f.text(cx + colw / 2, 164, q, size=19, fill=col, weight="bold")
        for j, (n, label) in enumerate(steps):
            ty = 186 + j * 126
            f.rect(cx + 12, ty, colw - 24, 112, fill="#FFFFFF", stroke=col, sw=1.5, rx=12)
            f.circle(cx + 46, ty + 56, 22, fill=col)
            f.text(cx + 46, ty + 64, str(n), size=21, fill="#FFFFFF", weight="bold")
            yy = ty + 64 if len(label) == 1 else ty + 51
            f.text(cx + 164, yy, label, size=21, fill=INK, weight="bold", lh=1.2)
        if i < 3:
            gx = cx + colw
            f.path([("M", gx + 9, 62), ("L", gx + 27, 78), ("L", gx + 9, 94), ("Z",)], fill=MUTED)
    # pretest can send the team back to phase 2
    c2 = x0 + 2 * (colw + gap)
    c1 = x0 + 1 * (colw + gap)
    f.rect(c2 + 12, 446, colw - 24, 122, fill="#FFFFFF", stroke=CORAL, sw=2, rx=12, dash="7 5")
    f.text(c2 + colw / 2, 482, L("Pretest problems?", "مشكلات في الاختبار؟"), size=19, fill=CORAL, weight="bold")
    f.text(c2 + colw / 2, 514, L(["Go back and revise", "steps 5–7"], ["ارجع وعدّل", "الخطوات 5–7"]),
           size=19, fill=INK, lh=1.25)
    f.path([("M", c2 + 12, 470), ("C", c2 - 14, 470, c1 + colw + 18, 372, c1 + colw - 6, 368)],
           stroke=CORAL, sw=3, dash="7 5", marker="ah-coral")
    f.rect(24, 742, 1152, 46, fill=GRAY, rx=12)
    f.text(600, 773, L("Good execution at the end cannot fix a basic mistake at the start.",
                       "التنظيم الجيد في آخر السلسلة لا يصلح خطأً أساسيًا في بدايتها."),
           size=21, fill=NAVY, weight="bold")
    f.save("survey_workflow",
           L("The 12 steps of a survey, grouped into four phases",
             "خطوات المسح الاثنتا عشرة مجمّعة في أربع مراحل"),
           L("Four colored columns read left to right. Phase 1, question and concepts: define the problem, "
             "questions and hypotheses, operational definitions, research plan. Phase 2, population, sample "
             "and instrument: population, unit and sampling design; instruments and measures; analysis plan. "
             "Phase 3, pretest and fieldwork: pretest and train the team; collect data. A dashed arrow shows "
             "that pretest problems send the researcher back to steps 5 to 7. Phase 4, analysis and reporting: "
             "analyze, interpret, write the report. Bottom message: good execution at the end cannot fix a "
             "basic mistake at the start.",
             "أربعة أعمدة ملونة تُقرأ من اليمين إلى اليسار. المرحلة 1، السؤال والمفاهيم: تحديد المشكلة، "
             "والأسئلة والفروض، والتعريف الإجرائي للمتغيرات، وخطة البحث. المرحلة 2، المجتمع والعينة والأداة: "
             "المجتمع والوحدة ونمط العينة، والأدوات والمقاييس، وخطة التحليل. المرحلة 3، الاختبار الأولي "
             "والعمل الميداني: اختبار أولي وتدريب الفريق، ثم جمع البيانات. ويبيّن سهم متقطع أن مشكلات "
             "الاختبار الأولي تعيد الباحث إلى الخطوات 5 إلى 7. المرحلة 4: التحليل والتفسير وكتابة التقرير. "
             "الرسالة: التنظيم الجيد في آخر السلسلة لا يصلح خطأً أساسيًا في بدايتها."))


# =====================================================================
# 2. Time designs
# =====================================================================
def time_designs(lang):
    f = Fig(lang)
    L = f.L
    letters = L(list("ABCDEFGHIJKLMNO"), ["أ", "ب", "ج", "د", "ه", "و", "ز", "ح", "ط", "ي", "ك", "ل", "م", "ن", "س"])
    waves = L(["Wave 1 · 2026", "Wave 2 · 2028", "Wave 3 · 2030"],
              ["الموجة 1 · 2026", "الموجة 2 · 2028", "الموجة 3 · 2030"])
    f.text(155, 36, L("Design", "التصميم"), size=19, fill=MUTED, weight="bold")
    bx = [320 + i * 290 for i in range(3)]
    for i in range(3):
        f.text(bx[i] + 133, 36, waves[i], size=19, fill=MUTED, weight="bold")
    rows = [
        ("cs", NAVY, NAVY_T, L("Cross-sectional", "مقطعي"), "Cross-Sectional",
         L("One sample · one time", "عينة واحدة · مرة واحدة"),
         L("One sample drawn once from the population", "عينة واحدة تُسحب مرة واحدة من المجتمع"),
         L(["sampled once", "", ""], ["عينة واحدة", "", ""])),
        ("trend", TEAL, TEAL_T, L("Trend", "الاتجاه العام"), "Trend",
         L("Fixed: the population", "الثابت: المجتمع"),
         L("Same population (enrolled students) · a new sample each wave",
           "المجتمع نفسه (الطلبة المسجلون) · عينة جديدة في كل موجة"),
         L(["new sample"] * 3, ["عينة جديدة"] * 3)),
        ("cohort", GOLD, GOLD_T, L("Cohort", "الفئة"), "Cohort",
         L("Fixed: the cohort", "الثابت: الفئة نفسها"),
         L("Same cohort (class of 2026) · a new sample each wave; members may differ",
           "الفئة نفسها (دفعة 2026) · عينة جديدة في كل موجة، وقد يختلف الأفراد"),
         L(["new sample · age ≈ 22", "new sample · age ≈ 24", "new sample · age ≈ 26"],
           ["عينة جديدة · العمر ≈ 22", "عينة جديدة · العمر ≈ 24", "عينة جديدة · العمر ≈ 26"])),
        ("panel", CORAL, CORAL_T, L("Panel", "اللوحة"), "Panel",
         L("Fixed: the same units", "الثابت: الوحدات نفسها"),
         L("The same people (A–E) are interviewed in every wave",
           "الأشخاص أنفسهم (أ–هـ) يُسألون في كل موجة"),
         L(["same A–E"] * 3, ["أ–هـ أنفسهم"] * 3)),
    ]
    for k, (kind, col, tint, name, term, fixed, band, caps) in enumerate(rows):
        ry = 56 + k * 146
        f.rect(20, ry + 6, 270, 130, fill=col, rx=14)
        if f.ar:
            f.text(155, ry + 50, name, size=27, fill="#FFFFFF", weight="bold")
            f.text(155, ry + 78, term, size=17, fill="#FFFFFF", opacity=0.85, latin=True)
            f.text(155, ry + 112, fixed, size=19, fill="#FFFFFF", weight="bold")
        else:
            f.text(155, ry + 62, name, size=27, fill="#FFFFFF", weight="bold")
            f.text(155, ry + 100, fixed, size=19, fill="#FFFFFF", weight="bold")
        f.rect(306, ry + 6, 874, 130, fill=tint, rx=14)
        f.text(743, ry + 30, band, size=17, fill=col, weight="bold")
        for i in range(3):
            if kind == "cs" and i > 0:
                f.rect(bx[i], ry + 40, 266, 88, fill="none", stroke="#B8C0C8", sw=1.5, rx=10, dash="6 5")
                f.text(bx[i] + 133, ry + 90, L("not repeated", "لا تكرار"), size=17, fill=MUTED)
                continue
            f.rect(bx[i], ry + 40, 266, 88, fill="#FFFFFF", stroke=col, sw=1.2, rx=10)
            ids = range(5) if kind in ("cs", "panel") else range(5 * i, 5 * i + 5)
            for j, idx in enumerate(ids):
                f.person(bx[i] + 133 + (j - 2) * 48, ry + 80, s=1.0, fill=col,
                         letter=letters[idx], cap=(kind == "cohort"))
            f.text(bx[i] + 133, ry + 122, caps[i], size=15, fill=MUTED)
            if kind == "panel" and i < 2:
                f.line(bx[i] + 266, ry + 84, bx[i + 1], ry + 84, stroke=col, sw=4)
    f.save("time_designs",
           L("Four time designs: cross-sectional, trend, cohort, and panel",
             "أربعة تصاميم زمنية: المقطعي والاتجاه العام والفئة واللوحة"),
           L("Four rows compare three waves (2026, 2028, 2030). Each person icon carries a letter; the same "
             "letter means the same person. Cross-sectional: one sample (A–E) in wave 1 only. Trend: the same "
             "population of enrolled students, but different people each wave (A–E, then F–J, then K–O). "
             "Cohort: every icon wears a graduation cap for the class of 2026; each wave draws a new sample "
             "from that same cohort as it ages from about 22 to 26, so members may differ. Panel: the same "
             "people A–E appear in all three waves, linked by a line.",
             "أربعة صفوف تقارن ثلاث موجات (2026 و2028 و2030). يحمل كل رمز شخص حرفًا، والحرف نفسه يعني "
             "الشخص نفسه. المقطعي: عينة واحدة (أ–هـ) في الموجة الأولى فقط. الاتجاه العام: المجتمع نفسه من "
             "الطلبة المسجلين، لكن أشخاص مختلفون في كل موجة. الفئة: كل رمز يرتدي قبعة تخرج لدفعة 2026، "
             "وتُسحب في كل موجة عينة جديدة من الدفعة نفسها مع تقدمها في العمر من نحو 22 إلى 26، فقد يختلف "
             "الأفراد. اللوحة: الأشخاص أنفسهم أ–هـ يظهرون في الموجات الثلاث ويربطهم خط."))


# =====================================================================
# 3. Attrition bias
# =====================================================================
def attrition_bias(lang):
    f = Fig(lang)
    L = f.L
    lost_coral = {(0, 0), (0, 2), (0, 3), (0, 5), (0, 7), (1, 1), (1, 2), (1, 4), (1, 5), (1, 6)}
    lost_teal = {(2, 2), (3, 5), (4, 1), (4, 6)}
    for side, gx0 in (("before", 90), ("after", 830)):
        for r in range(5):
            for c in range(8):
                x, y = gx0 + c * 40, 122 + r * 50
                stressed = r < 2
                lost = (r, c) in lost_coral or (r, c) in lost_teal
                if side == "after" and lost:
                    f.person(x, y, s=0.85, ghost=True)
                else:
                    f.person(x, y, s=0.85, fill=CORAL if stressed else TEAL)
    f.text(230, 54, L("Wave 1: 1,000 students", "الموجة الأولى: 1,000 طالب"), size=25, fill=NAVY, weight="bold")
    f.text(970, 54, L("Two years later: 650 remain", "بعد سنتين: بقي 650"), size=25, fill=NAVY, weight="bold")
    for gx0, share, label in ((70, 0.40, L("High stress: 40%", "ضغط مرتفع: 40%")),
                              (810, 0.23, L("High stress: 23%", "ضغط مرتفع: 23%"))):
        f.rect(gx0, 378, 320, 28, fill=TEAL, rx=6)
        f.rect(gx0, 378, 320 * share, 28, fill=CORAL, rx=6)
        f.text(gx0 + 160, 440, label, size=22, fill=CORAL, weight="bold")
    f.line(430, 222, 770, 222, stroke=NAVY, sw=5, marker="ah-navy")
    f.text(600, 192, L("350 left the panel", "انسحب 350 من اللوحة"), size=24, fill=NAVY, weight="bold")
    f.text(600, 264, L("250 high-stress or leavers", "250 من الأكثر ضغطًا أو تاركي الجامعة"), size=19, fill=CORAL, weight="bold")
    f.text(600, 292, L("100 other students", "100 من الطلبة الآخرين"), size=19, fill=TEAL, weight="bold")
    f.text(600, 336, L("Retention 65% · the loss is not random", "الاحتفاظ 65% · والفقد ليس عشوائيًا"),
           size=17, fill=MUTED)
    # legend
    f.rect(448, 372, 304, 138, fill=GRAY, rx=12)
    for k, (kw, label) in enumerate(((dict(fill=CORAL), L("High stress or leaving university", "ضغط مرتفع أو ترك الجامعة")),
                                     (dict(fill=TEAL), L("Other students", "طلبة آخرون")),
                                     (dict(ghost=True), L("Dropped out of the panel", "انسحب من اللوحة")))):
        f.person(474, 398 + k * 32, s=0.7, **kw)
        f.text(494, 404 + k * 32, label, size=16, fill=INK, anchor="start")
    f.text(600, 497, L("Each icon = 25 students", "كل رمز = 25 طالبًا"), size=16, fill=MUTED, weight="bold")
    f.rect(40, 534, 1120, 88, fill=NAVY, rx=14)
    f.text(600, 570, L("The retained panel looks healthier, even if no one's stress changed.",
                       "تبدو اللوحة المتبقية أكثر صحة، حتى لو لم يتغير ضغط أي طالب."),
           size=24, fill="#FFFFFF", weight="bold")
    f.text(600, 604, L("The most stressed students were the most likely to leave.",
                       "السبب أن الأكثر ضغطًا كانوا الأكثر انسحابًا."),
           size=20, fill=PALE_GOLD)
    f.save("attrition_bias",
           L("Attrition bias in a panel: 1,000 students shrink to 650",
             "تحيز الاستنزاف في دراسة اللوحة: 1,000 طالب يصبحون 650"),
           L("Two grids of 40 icons, each icon equal to 25 students. Wave 1 has 1,000 students: 400 high-stress "
             "or at risk of leaving university (coral) and 600 others (teal). Two years later 650 remain: 350 "
             "left the panel, 250 of them high-stress or leavers and 100 others; dropouts appear as dashed "
             "outlines. The high-stress share falls from 40% to 23%. Message: the retained panel looks "
             "healthier even if no one's stress changed, because the most stressed were most likely to leave.",
             "شبكتان من 40 رمزًا، وكل رمز يمثل 25 طالبًا. في الموجة الأولى 1,000 طالب: 400 من الأكثر ضغطًا "
             "أو المعرضين لترك الجامعة (باللون المرجاني) و600 آخرون (باللون الأخضر المزرق). بعد سنتين بقي 650: "
             "انسحب 350، منهم 250 من الأكثر ضغطًا أو تاركي الجامعة و100 من غيرهم، ويظهر المنسحبون بخطوط "
             "متقطعة. تنخفض نسبة الضغط المرتفع من 40% إلى 23%. الرسالة: تبدو اللوحة المتبقية أكثر صحة حتى لو "
             "لم يتغير ضغط أي طالب، لأن الأكثر ضغطًا كانوا الأكثر انسحابًا."))


# =====================================================================
# 4. Standardization vs depth
# =====================================================================
def standardization_depth(lang):
    f = Fig(lang)
    L = f.L
    a, b = (TEAL, GOLD) if not f.ar else (GOLD, TEAL)
    f.defs.append(f'<linearGradient id="cont" gradientUnits="userSpaceOnUse" x1="140" x2="1060" y1="44" y2="44">'
                  f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
    f.path([("M", 140, 44), ("L", 1060, 44)], stroke="url(#cont)", sw=6)
    f.path([("M", 150, 30), ("L", 126, 44), ("L", 150, 58), ("Z",)], fill=TEAL)
    f.path([("M", 1050, 30), ("L", 1074, 44), ("L", 1050, 58), ("Z",)], fill=GOLD)
    f.text(330, 84, L("Standardize across many cases", "توحيد عبر حالات كثيرة"), size=19, fill=TEAL, weight="bold")
    f.text(870, 84, L("Go deep into a few cases", "تعمّق في حالات قليلة"), size=19, fill=GOLD, weight="bold")
    panels = [
        (40, TEAL, TEAL_T, L(["Survey"], ["المسح"]),
         L(["Standardization", "Comparability", "Coverage (breadth)"], ["التوحيد", "قابلية المقارنة", "الاتساع والتغطية"]),
         L("How many? How common? Do groups differ?", "كم؟ ما مدى الانتشار؟ هل تختلف الفئات؟"),
         L("Can miss the meaning behind fixed options", "قد يفوته المعنى وراء البدائل الموحدة")),
        (720, GOLD, GOLD_T, L(["Case study / in-depth interview"], ["دراسة الحالة / المقابلة المعمقة"]),
         L(["Context", "Process", "Meaning"], ["السياق", "العملية", "المعنى"]),
         L("How does it unfold? What does it mean?", "كيف تجري العملية؟ وماذا تعني لأصحابها؟"),
         L("Can miss breadth and comparison across cases", "قد يفوتها الاتساع والمقارنة بين الحالات")),
    ]
    for px, col, tint, name, chips, asks, miss in panels:
        cx = px + 220
        f.rect(px, 110, 440, 452, fill=tint, stroke=col, sw=2, rx=18)
        f.text(cx, 152, name, size=25 if len(name[0]) > 12 else 28, fill=col, weight="bold")
        if col == TEAL:
            for r in range(3):
                for c in range(10):
                    f.person(cx - 180 + c * 40, 196 + r * 36, s=0.62, fill=col)
        else:
            f.circle(cx, 236, 62, stroke=col, sw=1.5, dash="5 5")
            f.circle(cx, 236, 44, fill="#FFFFFF", stroke=col, sw=1.5, dash="3 4")
            f.person(cx, 242, s=1.25, fill=col)
            f.rect(cx + 28, 186, 46, 28, fill="#FFFFFF", stroke=col, sw=2, rx=8)
            f.path([("M", cx + 36, 214), ("L", cx + 30, 224), ("L", cx + 46, 214)], fill="#FFFFFF", stroke=col, sw=2)
            for k in range(3):
                f.line(cx + 36, 194 + k * 7 + 1, cx + 66, 194 + k * 7 + 1, stroke=col, sw=2)
        for k, chip in enumerate(chips):
            f.rect(cx - 150, 316 + k * 50, 300, 40, fill="#FFFFFF", stroke=col, sw=2, rx=20)
            f.text(cx, 343 + k * 50, chip, size=21, fill=col, weight="bold")
        f.text(cx, 488, L("Answers questions like", "يجيب عن أسئلة مثل"), size=16, fill=MUTED)
        f.text(cx, 514, asks, size=18, fill=INK, weight="bold")
        f.text(cx, 546, miss, size=16, fill=MUTED, italic=True)
    f.path([("M", 716, 270), ("C", 660, 218, 540, 218, 484, 270)], stroke=NAVY, sw=3, marker="ah-navy")
    f.text(600, 186, L(["Depth sharpens", "survey questions"], ["التعمق يحسّن", "أسئلة المسح"]),
           size=17, fill=NAVY, weight="bold")
    f.path([("M", 484, 412), ("C", 540, 464, 660, 464, 716, 412)], stroke=NAVY, sw=3, marker="ah-navy")
    f.text(600, 486, L(["Breadth shows", "how common it is"], ["الاتساع يبيّن", "مدى انتشار النمط"]),
           size=17, fill=NAVY, weight="bold")
    f.circle(600, 341, 70, fill=NAVY)
    f.text(600, 347, L("Complementary", "متكاملان"), size=L(16, 22), fill="#FFFFFF", weight="bold")
    f.rect(40, 584, 1120, 50, fill=GRAY, rx=12)
    f.text(600, 616, L("Not more vs. less scientific: different kinds of evidence for different questions.",
                       "الفرق ليس «علمي» مقابل «غير علمي»؛ بل نوع الدليل الذي ينتجه كل تصميم."),
           size=21, fill=NAVY, weight="bold")
    f.save("standardization_depth",
           L("Survey and case study: standardization and depth as complementary strengths",
             "المسح ودراسة الحالة: التوحيد والتعمق قوتان متكاملتان"),
           L("A two-headed continuum runs from standardizing across many cases to going deep into a few. "
             "The survey panel shows many identical figures and lists standardization, comparability and "
             "coverage; it answers how many, how common, and whether groups differ, but can miss the meaning "
             "behind fixed options. The case study and in-depth interview panel shows one person in layers of "
             "context and lists context, process and meaning; it answers how things unfold and what they mean, "
             "but can miss breadth and comparison. Arrows between the panels show that depth sharpens survey "
             "questions and breadth shows how common a pattern is. The message: not more versus less "
             "scientific, but different kinds of evidence.",
             "سهم ذو اتجاهين يمتد من التوحيد عبر حالات كثيرة إلى التعمق في حالات قليلة. لوحة المسح تعرض "
             "أشخاصًا كثيرين متماثلين، وتذكر التوحيد وقابلية المقارنة والاتساع؛ وتجيب عن: كم؟ وما مدى "
             "الانتشار؟ وهل تختلف الفئات؟ لكنها قد تفوّت المعنى وراء البدائل الموحدة. لوحة دراسة الحالة "
             "والمقابلة المعمقة تعرض شخصًا واحدًا داخل طبقات من السياق، وتذكر السياق والعملية والمعنى؛ "
             "لكنها قد تفوّت الاتساع والمقارنة. يبيّن سهمان أن التعمق يحسّن أسئلة المسح، وأن الاتساع يبيّن "
             "مدى انتشار النمط. الرسالة: الفرق ليس علميًا مقابل غير علمي، بل نوع الدليل."))


# =====================================================================
# 5. Collection modes
# =====================================================================
def mode_icon(f, kind, cx, cy, col):
    if kind == "phone":
        f.rect(cx - 17, cy - 30, 34, 60, fill="#FFFFFF", stroke=col, sw=3, rx=7)
        f.rect(cx - 11, cy - 22, 22, 38, fill=TEAL_T)
        f.circle(cx, cy + 23, 2.5, fill=col)
        for r in (12, 22):
            f.path([("M", cx + 22, cy - r), ("Q", cx + 22 + r * 0.8, cy, cx + 22, cy + r)], stroke=col, sw=2.5)
    elif kind == "self":
        f.rect(cx - 24, cy - 32, 48, 62, fill="#FFFFFF", stroke=col, sw=3, rx=5)
        for k in range(3):
            y = cy - 18 + k * 16
            f.rect(cx - 15, y - 5, 10, 10, fill="#FFFFFF", stroke=col, sw=2)
            f.line(cx + 1, y, cx + 16, y, stroke=col, sw=2.5)
        f.path([("M", cx - 13, cy - 18), ("L", cx - 10, cy - 14), ("L", cx - 5, cy - 22)], stroke=col, sw=2)
    elif kind == "face":
        f.person(cx - 30, cy - 2, s=1.0, fill=col)
        f.person(cx + 30, cy - 2, s=1.0, fill=col)
        f.rect(cx - 16, cy + 6, 32, 14, fill="#FFFFFF", stroke=col, sw=2.5, rx=2)
        f.line(cx - 22, cy + 26, cx + 22, cy + 26, stroke=col, sw=3)
    elif kind == "computer":
        f.rect(cx - 34, cy - 28, 68, 44, fill="#FFFFFF", stroke=col, sw=3, rx=4)
        f.path([("M", cx - 44, cy + 24), ("L", cx + 44, cy + 24), ("L", cx + 36, cy + 16), ("L", cx - 36, cy + 16), ("Z",)],
               fill=col)
        f.path([("M", cx - 20, cy - 6), ("L", cx, cy - 16), ("M", cx - 20, cy - 6), ("L", cx, cy + 4)], stroke=col, sw=2)
        for x, y in ((cx - 20, cy - 6), (cx, cy - 16), (cx, cy + 4)):
            f.circle(x, y, 4, fill=col)
        f.line(cx + 6, cy - 16, cx + 22, cy - 16, stroke=col, sw=2)
        f.line(cx + 6, cy + 4, cx + 22, cy + 4, stroke=col, sw=2)


def cue_icon(f, kind, cx, cy):
    c = NAVY
    if kind == "reach":
        f.circle(cx, cy, 16, stroke=c, sw=2.5)
        f.add(f'<ellipse cx="{f.mx(cx):.1f}" cy="{cy}" rx="7" ry="16" fill="none" stroke="{c}" stroke-width="2"/>')
        f.line(cx - 16, cy, cx + 16, cy, stroke=c, sw=2)
    elif kind == "clarify":
        f.rect(cx - 18, cy - 15, 36, 26, fill="none", stroke=c, sw=2.5, rx=8)
        f.path([("M", cx - 8, cy + 11), ("L", cx - 12, cy + 19), ("L", cx + 1, cy + 11)], stroke=c, sw=2.5)
        f.text(cx, cy + 5, "?", size=18, fill=c, weight="bold", latin=True)
    elif kind == "privacy":
        f.rect(cx - 14, cy - 3, 28, 21, fill=c, rx=3)
        f.path([("M", cx - 8, cy - 3), ("V", cy - 9), ("C", cx - 8, cy - 20, cx + 8, cy - 20, cx + 8, cy - 9),
                ("V", cy - 3)], stroke=c, sw=3)
    elif kind == "cost":
        for k, off in enumerate((-8, 6, -2)):
            y = cy - 12 + k * 12
            f.line(cx - 18, y, cx + 18, y, stroke=c, sw=2.5)
            f.circle(cx + off, y, 4.5, fill="#FFFFFF", stroke=c, sw=2.5)


def collection_modes(lang):
    f = Fig(lang)
    L = f.L
    modes = [
        ("phone", TEAL, L("Phone", "المسح الهاتفي"), L("interviewer by phone", "مقابل عبر الهاتف"),
         [L(["Wide areas; unknown", "numbers often refused"], ["مناطق متباعدة؛ ورفض", "الأرقام المجهولة"]),
          L(["Interviewer", "can clarify"], ["يستطيع المقابل", "التوضيح"]),
          L(["Others may", "overhear"], ["قد يسمع الآخرون", "المكالمة"]),
          L(["Often cheaper;", "central supervision"], ["أقل كلفة غالبًا؛", "وإشراف مركزي"])]),
        ("self", GOLD, L("Self-administered", "الاستبانة الذاتية"), L("paper or online", "ورقية أو إلكترونية"),
         [L(["Depends on mail or", "internet access"], ["تعتمد على البريد", "أو الإنترنت"]),
          L(["No live help"], ["لا توضيح مباشر"]),
          L(["Often more", "private"], ["خصوصية أعلى", "أحيانًا"]),
          L(["Low cost; unclear", "who answered"], ["كلفة أقل؛ ولا نعرف", "دائمًا من أجاب"])]),
        ("face", NAVY, L("Face-to-face", "المقابلة الشخصية"), L("structured interview", "منظمة وجهًا لوجه"),
         [L(["Travel needed; works", "for non-readers"], ["تتطلب تنقلًا؛ وتناسب", "من يصعب عليه القراءة"]),
          L(["Clarify and", "follow up"], ["توضيح", "ومتابعة"]),
          L(["Interviewer", "is present"], ["وجود المقابل", "قد يحرج المجيب"]),
          L(["Costly; tight", "control of question path"], ["كلفة أعلى؛ وضبط", "مسار الأسئلة"])]),
        ("computer", CORAL, L("Computer-assisted", "بمساعدة الحاسوب"), L("a layer on any channel", "طبقة تضاف إلى أي قناة"),
         [L(["Same coverage as", "the channel used"], ["تغطية القناة", "المستخدمة نفسها"]),
          L(["Depends on", "the channel"], ["بحسب", "القناة"]),
          L(["Self-entry", "can help"], ["الإدخال الذاتي", "قد يساعد"]),
          L(["Setup cost; automatic", "paths and checks"], ["كلفة إعداد؛ ومسارات", "وتنبيهات آلية"])]),
    ]
    cues = [("reach", L("Reach", "الوصول")), ("clarify", L("Clarification", "التوضيح")),
            ("privacy", L("Privacy", "الخصوصية")), ("cost", L("Cost & control", "الكلفة والضبط"))]
    for k, (kind, label) in enumerate(cues):
        ry = 190 + k * 92
        f.rect(20, ry, 1160, 92, fill=GRAY if k % 2 == 0 else "#FFFFFF")
        cue_icon(f, kind, 110, ry + 32)
        f.text(110, ry + 76, label, size=18, fill=NAVY, weight="bold")
    for i, (kind, col, name, sub, cells) in enumerate(modes):
        x0 = 210 + i * 245
        cx = x0 + 117.5
        f.rect(x0, 20, 235, 158, fill={TEAL: TEAL_T, GOLD: GOLD_T, NAVY: NAVY_T, CORAL: CORAL_T}[col], rx=16)
        mode_icon(f, kind, cx, 70, col)
        f.text(cx, 132, name, size=22, fill=col, weight="bold")
        f.text(cx, 158, sub, size=16, fill=MUTED)
        for k, cell in enumerate(cells):
            ry = 190 + k * 92
            yy = ry + 53 if len(cell) == 1 else ry + 40
            f.text(cx, yy, cell, size=L(17, 19), fill=INK, lh=1.3)
        f.rect(x0, 20, 235, 538, fill="none", stroke=col, sw=2.5, rx=16, dash="8 6" if kind == "computer" else None)
    f.text(600, 600, L("No universal ranking: choose by population, topic sensitivity,",
                       "لا يوجد ترتيب عام: يعتمد الاختيار على المجتمع، وحساسية الموضوع،"),
           size=20, fill=NAVY, weight="bold")
    f.text(600, 628, L("question complexity, cost, and the response quality you need.",
                       "وتعقيد الأسئلة، والكلفة، وجودة الاستجابة المطلوبة."),
           size=20, fill=NAVY, weight="bold")
    f.save("collection_modes",
           L("Four ways to collect survey data, compared on four decision cues",
             "أربع طرق لجمع بيانات المسح مقارنة بأربعة معايير للقرار"),
           L("A grid with four columns: phone, self-administered (paper or online), structured face-to-face "
             "interview, and computer-assisted collection, which is drawn with a dashed border as a layer on "
             "any channel. Four rows give short cues on reach, clarification, privacy, and cost and control. "
             "For example, phone reaches wide areas but unknown numbers are often refused; self-administered "
             "forms offer no live help but are often more private; face-to-face allows follow-up but the "
             "interviewer is present; computer assistance automates paths and checks but keeps the coverage "
             "of its channel. Bottom note: there is no universal ranking.",
             "جدول من أربعة أعمدة: المسح الهاتفي، والاستبانة الذاتية الورقية أو الإلكترونية، والمقابلة "
             "الشخصية المنظمة، والجمع بمساعدة الحاسوب، وقد رُسم بإطار متقطع لأنه طبقة تضاف إلى أي قناة. "
             "وتعرض أربعة صفوف إشارات قصيرة عن الوصول، والتوضيح، والخصوصية، والكلفة والضبط. مثلًا: الهاتف "
             "يصل إلى مناطق متباعدة لكن الأرقام المجهولة تُرفض، والاستبانة الذاتية بلا توضيح مباشر لكنها "
             "أكثر خصوصية أحيانًا، والمقابلة الشخصية تسمح بالمتابعة مع وجود المقابل، والحاسوب يضبط المسارات "
             "والتنبيهات لكنه يحتفظ بتغطية القناة نفسها. الملاحظة: لا يوجد ترتيب عام."))


# =====================================================================
# 6. Respondent vs unit of analysis
# =====================================================================
def unit_icon(f, kind, cx, cy):
    x = f.mx(cx)
    s = NAVY
    if kind == "school":
        f.add(f'<rect x="{x - 64:.1f}" y="{cy - 18}" width="128" height="68" fill="{NAVY_T}" stroke="{s}" stroke-width="3"/>')
        f.add(f'<polygon points="{x - 72:.1f},{cy - 18} {x:.1f},{cy - 50} {x + 72:.1f},{cy - 18}" fill="{NAVY_T}" '
              f'stroke="{s}" stroke-width="3" stroke-linejoin="round"/>')
        f.add(f'<line x1="{x:.1f}" y1="{cy - 50}" x2="{x:.1f}" y2="{cy - 72}" stroke="{s}" stroke-width="2.5"/>')
        f.add(f'<polygon points="{x:.1f},{cy - 72} {x + 20:.1f},{cy - 66} {x:.1f},{cy - 60}" fill="{GOLD}"/>')
        n, base = 5, cy + 34
    elif kind == "household":
        f.add(f'<rect x="{x - 58:.1f}" y="{cy - 14}" width="116" height="64" fill="{NAVY_T}" stroke="{s}" stroke-width="3"/>')
        f.add(f'<polygon points="{x - 70:.1f},{cy - 12} {x:.1f},{cy - 60} {x + 70:.1f},{cy - 12}" fill="{NAVY_T}" '
              f'stroke="{s}" stroke-width="3" stroke-linejoin="round"/>')
        n, base = 4, cy + 34
    else:
        f.add(f'<rect x="{x - 52:.1f}" y="{cy - 64}" width="104" height="114" fill="{NAVY_T}" stroke="{s}" stroke-width="3"/>')
        for r in range(3):
            for c in range(4):
                f.add(f'<rect x="{x - 40 + c * 22:.1f}" y="{cy - 54 + r * 18}" width="14" height="10" fill="#FFFFFF" '
                      f'stroke="{s}" stroke-width="1.2"/>')
        n, base = 4, cy + 34
    step = 24
    start = cx - step * (n - 1) / 2
    for i in range(n):
        small = kind == "household" and i >= 2
        f.person(start + step * i, base + (3 if small else 0), s=0.5 if small else 0.62,
                 fill=TEAL if i == 0 else "#8C9BB0")


def respondent_unit(lang):
    f = Fig(lang)
    L = f.L
    f.text(230, 44, L("Respondent", "المجيب"), size=27, fill=TEAL, weight="bold")
    f.text(230, 72, L("who answers the questions", "من يجيب عن الأسئلة"), size=18, fill=MUTED)
    f.text(830, 44, L("Unit of analysis", "وحدة التحليل"), size=27, fill=NAVY, weight="bold")
    f.text(830, 72, L("what we draw conclusions about", "ما نستنتج عنه ونقارن بين حالاته"), size=18, fill=MUTED)
    rows = [
        ("school", L("School director", "مدير المدرسة"), L("fills in the questionnaire", "يملأ الاستبانة"),
         L("School", "المدرسة"), L(["Data on teachers, absence", "policy, and activities"],
                                   ["بيانات عن المعلمين، وسياسة", "الغياب، والأنشطة"])),
        ("household", L("Household member", "أحد أفراد الأسرة"), L("answers for the household", "يجيب نيابة عن الأسرة"),
         L("Household", "الأسرة"), L(["Data on income, size,", "and housing"], ["بيانات عن الدخل، وعدد", "الأفراد، والسكن"])),
        ("org", L("Employee", "موظف"), L("answers for the organization", "يجيب عن مؤسسته"),
         L("Organization", "المؤسسة"), L(["Data on staff size,", "policies, and structure"],
                                         ["بيانات عن عدد العاملين،", "والسياسات، والهيكل"])),
    ]
    for k, (kind, who, how, unit, data) in enumerate(rows):
        ry = 96 + k * 160
        f.rect(30, ry, 1140, 148, fill=GRAY, rx=16)
        f.person(100, ry + 78, s=1.7, fill=TEAL)
        f.text(265, ry + 70, who, size=23, fill=INK, weight="bold")
        f.text(265, ry + 100, how, size=L(17, 19), fill=MUTED)
        f.text(500, ry + 58, L("reports on", "يجيب عن"), size=17, fill=MUTED, weight="bold")
        f.line(420, ry + 76, 580, ry + 76, stroke=TEAL, sw=4, marker="ah-teal")
        unit_icon(f, kind, 690, ry + 78)
        f.text(965, ry + 62, unit, size=25, fill=NAVY, weight="bold")
        f.text(965, ry + 94, data, size=L(17, 19), fill=INK, lh=1.3)
    f.rect(30, 584, 1140, 52, fill=NAVY, rx=14)
    f.text(600, 618, L("The person who answers is not always the unit we draw conclusions about.",
                       "من يجيب عن الأسئلة ليس دائمًا الوحدة التي نستنتج عنها."),
           size=22, fill="#FFFFFF", weight="bold")
    f.save("respondent_unit",
           L("Respondent versus unit of analysis", "المجيب ووحدة التحليل"),
           L("Three examples. A school director fills in the questionnaire, but the unit of analysis is the "
             "school, with data on teachers, absence policy and activities. A household member answers for the "
             "household, the unit, with data on income, size and housing. An employee answers for the "
             "organization, the unit, with data on staff size, policies and structure. In each unit icon the "
             "respondent appears as one highlighted member among others. Message: the person who answers is "
             "not always the unit we draw conclusions about.",
             "ثلاثة أمثلة. مدير المدرسة يملأ الاستبانة، لكن وحدة التحليل هي المدرسة، والبيانات عن المعلمين "
             "وسياسة الغياب والأنشطة. أحد أفراد الأسرة يجيب نيابة عن الأسرة، وهي الوحدة، والبيانات عن الدخل "
             "وعدد الأفراد والسكن. موظف يجيب عن مؤسسته، وهي الوحدة، والبيانات عن عدد العاملين والسياسات "
             "والهيكل. ويظهر المجيب داخل كل وحدة عضوًا مميزًا بين آخرين. الرسالة: من يجيب عن الأسئلة ليس "
             "دائمًا الوحدة التي نستنتج عنها."))


# =====================================================================
# 7. Household panel family tree (schematic)
# =====================================================================
def panel_family_tree(lang):
    f = Fig(lang)
    L = f.L
    f.text(600, 30, L("Schematic example inspired by long-running household panels such as the PSID: not actual PSID data",
                      "مثال توضيحي مستوحى من لوحات الأسر الطويلة مثل PSID، وليس بيانات PSID فعلية"),
           size=17, fill=MUTED, italic=True)
    # legend
    lx = [40, 300, 620, 890]
    f.house(lx[0] + 16, 66, GOLD, GOLD2, [], s=0.5)
    f.text(lx[0] + 44, 66, L("Original sample family", "أسرة من العينة الأصلية"), size=16, fill=INK, anchor="start")
    f.house(lx[1] + 16, 66, TEAL, TEAL_T, [], s=0.5)
    f.text(lx[1] + 44, 66, L("Household formed by a descendant", "أسرة كوّنها أحد الأبناء أو الأحفاد"),
           size=16, fill=INK, anchor="start")
    f.line(lx[2], 60, lx[2] + 34, 60, stroke="#AEB8C3", sw=4)
    f.text(lx[2] + 44, 66, L("Same household, next wave", "الأسرة نفسها في الموجة التالية"), size=16, fill=INK, anchor="start")
    f.line(lx[3], 60, lx[3] + 34, 60, stroke=TEAL, sw=2.5, dash="6 4")
    f.text(lx[3] + 44, 66, L("Child forms a new household", "ابن أو ابنة يكوّن أسرة جديدة"), size=16, fill=INK, anchor="start")

    wx = [170, 450, 730, 1010]
    for x in wx:
        f.rect(x - 112, 88, 224, 472, fill=GRAY, rx=14)
    hy = {"A": 132, "A1": 197, "A1a": 262, "A2": 327, "B": 412, "B1": 477, "B2": 538}
    members = {
        "A": ["aakk", "aak", "aa", "aa"], "A1": [None, "a", "aa", "aak"], "A2": [None, None, "a", "aa"],
        "A1a": [None, None, None, "a"], "B": ["aakk", "aakk", "aak", "aa"], "B1": [None, None, "a", "aak"],
        "B2": [None, None, None, "a"],
    }
    parent = {"A1": "A", "A2": "A", "A1a": "A1", "B1": "B", "B2": "B"}
    for h, seq in members.items():
        for k in range(3):
            if seq[k] is not None and seq[k + 1] is not None:
                f.line(wx[k] + 40, hy[h], wx[k + 1] - 40, hy[h], stroke="#AEB8C3", sw=4)
    for h, p in parent.items():
        k = next(i for i, m in enumerate(members[h]) if m is not None)
        x1, y1, x2, y2 = wx[k - 1] + 38, hy[p] + 6, wx[k] - 42, hy[h]
        f.path([("M", x1, y1), ("C", x1 + 90, y1, x2 - 90, y2, x2, y2)], stroke=TEAL, sw=2.5, dash="6 4",
               marker="ah-teal")
    for h, seq in members.items():
        orig = h in ("A", "B")
        for k, m in enumerate(seq):
            if m is not None:
                f.house(wx[k], hy[h], GOLD if orig else TEAL, GOLD2 if orig else TEAL_T, list(m))
    f.text(wx[0] - 50, hy["A"] + 6, L("Family A", "الأسرة أ"), size=16, fill=GOLD, weight="bold", anchor="end")
    f.text(wx[0] - 50, hy["B"] + 6, L("Family B", "الأسرة ب"), size=16, fill=GOLD, weight="bold", anchor="end")
    f.text(wx[1], 268, L(["A grown child", "moves out: the new", "household joins", "the panel"],
                         ["ابن يكبر ويستقل:", "فتنضم أسرته", "الجديدة إلى اللوحة"]),
           size=16, fill=TEAL, weight="bold", lh=1.25)
    f.text(wx[3] + 46, hy["A1a"] - 2, L(["3rd", "generation"], ["الجيل", "الثالث"]), size=14, fill=TEAL,
           weight="bold", anchor="start", lh=1.15)
    f.line(60, 574, 1140, 574, stroke=MUTED, sw=2.5, marker="ah-muted")
    labels = L(["Wave 1 · start", "Wave 2 · +10 years", "Wave 3 · +20 years", "Wave 4 · +30 years"],
               ["الموجة 1 · البداية", "الموجة 2 · بعد 10 سنوات", "الموجة 3 · بعد 20 سنة", "الموجة 4 · بعد 30 سنة"])
    counts = L(["2 households", "3 households", "5 households", "7 households"], ["أسرتان", "3 أسر", "5 أسر", "7 أسر"])
    for k, x in enumerate(wx):
        f.text(x, 604, labels[k], size=19, fill=NAVY, weight="bold")
        f.text(x, 630, counts[k], size=17, fill=MUTED)
    f.save("panel_family_tree",
           L("Schematic household panel growing across generations",
             "مخطط توضيحي للوحة أسر تتسع عبر الأجيال"),
           L("A schematic, not actual PSID data. Four waves run left to right over 30 years. Wave 1 interviews "
             "two original sample families, A and B, drawn as gold houses with parents and children inside. "
             "Grey lines show each household re-interviewed in the next wave. As children grow up and move out, "
             "dashed teal lines lead to new teal households that join the panel, including a third-generation "
             "household by wave 4. The panel grows from 2 to 3, 5 and 7 households.",
             "مخطط توضيحي، وليس بيانات PSID فعلية. أربع موجات تمتد من اليمين إلى اليسار عبر 30 سنة. في الموجة "
             "الأولى تُسأل أسرتان من العينة الأصلية، أ وب، مرسومتان منزلين ذهبيين بداخلهما الوالدان والأبناء. "
             "تبيّن الخطوط الرمادية أن كل أسرة تُسأل مجددًا في الموجة التالية. وعندما يكبر الأبناء ويستقلون، "
             "تقود خطوط متقطعة إلى أسر جديدة تنضم إلى اللوحة، منها أسرة من الجيل الثالث في الموجة الرابعة. "
             "ويزداد عدد الأسر من 2 إلى 3 ثم 5 ثم 7."))


if __name__ == "__main__":
    for lang in ("en", "ar"):
        survey_workflow(lang)
        time_designs(lang)
        attrition_bias(lang)
        standardization_depth(lang)
        collection_modes(lang)
        respondent_unit(lang)
        panel_family_tree(lang)
    print("done")
