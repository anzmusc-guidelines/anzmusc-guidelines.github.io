---
name: panellist-headshot
description: >
  Use whenever a panellist headshot is added to or replaced on panellists.html. Triggers
  include "add a headshot for [name]", "[name] sent through their photo", "update the
  panellists page with the new photos", "Vanessa has collected headshots for the new
  panellists". Encodes the 256px / progressive-JPEG / quality-85 recipe that keeps each
  headshot at ~10–20 KB, the filename and alt-text conventions, and the reference check.
---

# Panellist Headshot Skill

**Why this skill exists.** In July 2026 the panellists page was carrying ~41 MB of
headshot images — several were 2000+ px, multi-megabyte files being displayed in a
64 px circle. They were compressed to a total of ~314 KB (a 99% reduction) with no
visible quality loss. This skill exists so that **any new headshot is added in the
same optimised format**, and the page never silently bloats back up. A raw photo
straight from a phone or a professional export is typically 2–6 MB; the same photo
prepared per this skill is ~10–20 KB.

---

# The rule in one line

**Every headshot is displayed at 64 px in a circle. Prepare it as a 256 px-longest-side,
progressive JPEG, quality 85, and it will look sharp on any screen at ~10–20 KB.**

- 256 px = 4× the 64 px display size, which is comfortably sharp on high-resolution
  ("retina") screens with headroom to spare.
- JPEG, not PNG. None of the headshots use transparency (the circular crop hides the
  corners anyway), and JPEG is dramatically smaller than PNG for photographs.
- All headshots use the `.jpg` extension. This keeps the folder uniform and avoids the
  mixed `.png`/`.jpeg`/`.jpg` situation that existed before.

---

# PHASE 0: PREPARATION

## Step 0.1: Collect the raw image and the person's details

When Vanessa requests photos from panellists, ask for: a professional headshot (shoulders
and up), at least 400×400 px, square or portrait, face roughly centred, JPG or PNG.

Confirm before starting:
- The raw headshot image file (any format, any size — it will be processed).
- The person's **display name exactly as it should appear**, including title
  (e.g. "Dr Samuel Whittle", "A/Prof Rachel Black", "Prof Rachelle Buchbinder").
  This becomes the image `alt` text and the visible caption.
- The **filename stem** to use. Convention is `Firstname-Lastname_headshot`
  (hyphen between first and last name, underscore before "headshot"). For hyphenated
  or compound surnames, follow the existing pattern, e.g.
  `Priscilla-CampbellStokes_headshot`, `Rachelle-Buchbinder_headshot`.
  The final filename is always `<stem>.jpg`.

## Step 0.2: Confirm the display size hasn't changed

The 256 px target assumes headshots are still displayed at 64 px. Confirm the avatar
size in `panellists.html` is unchanged:

```
.panellist-avatar { width: 64px; height: 64px; ... }
```

If this has been changed (e.g. to a larger profile display), recompute the target as
`4 × display_size` px and adjust the resize step accordingly.

---

# PHASE 1: PROCESS THE IMAGE

## Step 1: Resize and compress

Process the raw image with the following settings. (This is the exact recipe used for
the July 2026 batch.)

```python
from PIL import Image
import os

TARGET = 256           # longest side, in px (= 4× the 64px display)
SKIP_IF_MAX_DIM_LE = 260  # don't upscale images already this small or smaller
QUALITY = 85           # JPEG quality (use 88 for images left at native small size)

raw_path = 'PATH/TO/raw_photo'        # the incoming image
stem = 'Firstname-Lastname_headshot'  # per Step 0.1
out_path = f'images/headshots/{stem}.jpg'

im = Image.open(raw_path).convert('RGB')   # convert removes any unused alpha channel
w, h = im.size

if max(w, h) <= SKIP_IF_MAX_DIM_LE:
    # Already small — do NOT upscale (it only adds blur). Save as-is, just re-encoded.
    im.save(out_path, 'JPEG', quality=88, optimize=True, progressive=True)
else:
    scale = TARGET / max(w, h)
    new_size = (round(w * scale), round(h * scale))
    im = im.resize(new_size, Image.LANCZOS)   # LANCZOS = high-quality downscale
    im.save(out_path, 'JPEG', quality=QUALITY, optimize=True, progressive=True)

print(f"Saved {out_path}: {im.size}, {os.path.getsize(out_path)/1024:.0f} KB")
```

If the face is off-centre or small in the frame, square-crop centred on the face
**before** resizing, so the 64 px circle shows the face rather than background.

**Sanity check the output:**
- File size should be roughly **10–20 KB**. If it is over ~40 KB, something is off —
  check that the resize actually happened (the source may have been an unusual format)
  and that quality is 85, not higher.
- Longest side should be 256 px (or the native size if it was already ≤260 px).
- Format JPEG, mode RGB.

## Step 2: Visual quality check (REQUIRED)

Before committing, **look at the processed image at display size** — produce a contact
sheet showing each new headshot at 256 px and as a simulated 64 px circle, and show it
to Sam. Faces must be sharp with natural skin tones and no blocky JPEG artefacts. The
image is displayed as a 64 px circle with `object-fit: cover`, so the centre of the face
is what matters; the corners are cropped off by the circle.

If a face looks soft or blocky, raise quality to 90 and re-save (the size cost is small).
If the *source* was low-resolution (e.g. under ~200 px), it will look soft no matter what —
that is a source problem, not a compression problem; request a higher-resolution original
if possible, but never upscale to fake sharpness.

---

# PHASE 2: ADD TO THE PAGE

## Step 3: Place the image file

Save the processed `.jpg` into `images/headshots/`. If replacing an existing person's
photo that was a `.png` or `.jpeg`, **delete the old file** so the folder does not end up
with two copies (e.g. both `Jo-Tan_headshot.png` and `Jo-Tan_headshot.jpg`). Only the
`.jpg` should remain.

## Step 4: Add (or update) the panellist entry in `panellists.html`

Match the existing markup exactly. The image tag pattern is:

```html
<img src="images/headshots/<stem>.jpg" alt="<Display Name>" loading="lazy">
```

- `src` uses the `.jpg` filename from Step 1.
- `alt` is the person's full display name including title (per Step 0.1). This is what a
  screen reader announces and is important for accessibility — never leave it blank.
- `loading="lazy"` defers loading until the image is scrolled near, which keeps the page
  fast. Every headshot img should have it.

For an existing panellist, replace the initials inside the avatar `<div>` with the `<img>` —
and **keep the avatar's classes**. Chair/facilitator avatars have an extra `chair` class:

```html
<!-- before -->
<div class="panellist-avatar chair">RB</div>
<!-- after -->
<div class="panellist-avatar chair"><img src="images/headshots/Rachelle-Buchbinder_headshot.jpg" alt="Prof Rachelle Buchbinder" loading="lazy"></div>
```

Insert the full panellist card in the correct position within the existing grid, following
the surrounding entries as the template (avatar + name + role/affiliation). If the panel
member is being added as part of a new recommendation, cross-check the
`new-recommendation` skill, Step 11 (Panellists page), which may also apply.

## Step 5: Verify and open a pull request (REQUIRED)

Run `python3 .claude/scripts/verify_site.py` from the repo root. It errors on any headshot
`<img src>` that doesn't resolve to a real `.jpg` (which would show as a broken-image icon
on the live page) and warns on any headshot file over 40 KB. Then commit on a branch and
open a pull request — never push to `main`.

---

# Notes

- **Do not batch-reprocess the whole folder unnecessarily.** This skill is for *adding
  or replacing* individual headshots. Re-running compression on already-compressed images
  degrades them slightly each time (JPEG is lossy). Only process raw/oversized sources.
- **The page should look identical after adding a photo** — same size and position as the
  others. The only thing this skill controls is that the file is small and correctly
  referenced.
- **If ever displaying headshots larger than 64 px** (e.g. a future redesign with bigger
  profile photos), revisit the 256 px target — it should stay at 4× the largest size the
  image is displayed at.

---

*Established July 2026 alongside the headshot optimisation that reduced the panellists
page image payload from ~41 MB to ~314 KB.*
