# Social Research Methods — Fall 2026

Arabic-first course website for **مناهج البحث الاجتماعي (SOC 209)** at Kuwait University, Fall 2026/2027.

- Course website: <https://alqabandi.github.io/social-research-methods-fa26/>
- Instructor: Dr. Fatima Alqabandi

## Where the website lives

The editable source files live in this repository on the `main` branch. GitHub Actions renders the Quarto project and deploys the generated `_site` directory to GitHub Pages. The generated website is not stored in the personal `alqabandi.github.io` repository.

The personal website should contain only a Teaching-page link to this course site.

## Repository structure

- `index.qmd` — Arabic homepage and current schedule
- `syllabus.qmd` — syllabus landing page
- `assessments.qmd` — project and presentation rubrics
- `slides.qmd` and `slides/` — lecture slides
- `resources.qmd` — public research and data resources
- `materials/` — copied public syllabus and rubric sources plus downloadable PDFs
- `styles.css` — the original single-file stylesheet, kept as a fallback
- `css/` — swappable website themes (see below)
- `scripts/` — translation check and local PDF rendering
- `.github/workflows/publish.yml` — automatic GitHub Pages deployment

Instructor notes, answer keys, student information, and other private materials must not be added to this public repository.

## Changing the website look

`css/base.css` holds all the layout and reads its colours, fonts, and shadows from CSS variables. One theme file supplies those variables:

| Theme | Look |
| --- | --- |
| `css/theme-classic.css` | Navy, gold, and teal — the original design |
| `css/theme-meyers.css` | Cream page, espresso and brass structure |
| `css/theme-scandi.css` | Warm white page, deep pine and sage structure, crisper corners |

All three share the same hierarchy: a dark hero, navbar, and table header to anchor the page, white cards lifting off tinted paper, and callouts with a saturated bar and tint. Only the palette and the type change.

Switch by editing the `css` key in `_quarto.yml`:

```yaml
format:
  html:
    css:
      - css/base.css
      - css/theme-meyers.css
```

Load exactly one theme, always after `base.css`. To add a new look, copy an existing theme file and change the values — no layout rules need touching.

The downloadable syllabus and rubrics in `materials/` set their own `css:` and `embed-resources: true`, so they are self-contained and unaffected by the website theme. Their palettes live in `materials/syllabus-print.css`, `materials/research-proposal-rubric.css`, and `materials/presentation-rubric-landscape.css`.

## Local workflow

Preview ordinary website changes from the repository root:

```sh
/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto preview
```

After changing a syllabus or rubric, regenerate the site and all downloadable PDFs:

```sh
./scripts/render-public-materials.sh
```

The Arabic syllabus is authoritative. If it changes, update and review the English translation, then record that review before rendering:

```sh
python3 scripts/check-syllabus-translation.py --mark-reviewed
./scripts/render-public-materials.sh
```

Commit the edited source files and regenerated PDFs. Pushing to `main` automatically publishes the site.

## Adding lecture slides

Add slide source files under `slides/`, preferably with stable numbered names such as:

```text
slides/01-course-introduction.qmd
slides/02-social-research.qmd
```

Then add the rendered slide link to the corresponding row in `index.qmd`. Avoid embedding large videos or datasets directly in the repository.
