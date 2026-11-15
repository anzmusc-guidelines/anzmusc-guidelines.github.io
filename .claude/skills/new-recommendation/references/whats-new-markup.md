# What's New markup (ready to paste)

Both What's New blocks were removed on 15 Nov 2026 because their entries had aged out (entries come
off after ~6 months — see `.claude/site-decisions.md`). The CSS for them is still in each page, so
re-adding the markup below restores the sections exactly. Each page has an HTML comment marking the
spot (search for `What's New`).

Entries are listed newest first. Keep only entries under ~6 months old.

## Gateway `index.html`

Goes between the pathway-cards `</section>` and `<section class="about-section">`. Each item is a
link to the rec on its guideline page (`adult/#rec-N` or `jia/#jia-rec-N`); badge/label class is
`adult` (teal) or `jia` (purple). Meta line: `Month YYYY • New recommendation` (or `• Updated`).
The grid is two columns; with one entry the card sits left, which is acceptable.

```html
    <section class="whats-new-section">
        <div class="whats-new-container">
            <div class="whats-new-header">
                <h2>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clip-rule="evenodd"/></svg>
                    What's New
                </h2>
            </div>
            <div class="whats-new-grid">
                <a href="jia/#jia-rec-5" class="whats-new-item">
                    <div class="whats-new-badge jia">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/></svg>
                    </div>
                    <div class="whats-new-content">
                        <div class="whats-new-label jia">Juvenile Idiopathic Arthritis</div>
                        <div class="whats-new-title">b/tsDMARD dose reduction or discontinuation for JIA</div>
                        <div class="whats-new-meta">October 2025 • New recommendation</div>
                    </div>
                </a>
            </div>
        </div>
    </section>
```

## Adult `adult/index.html` hero panel

Goes inside `.hero-content`, directly after the `</div>` that closes `.hero-text`. Badge/label class
is `new` (green) or `updated` (blue). Meta line: `Month YYYY • conditions`. The item opens the modal
directly with `openModal('rec-N')`.

```html
            <div class="whats-new-section">
                <div class="whats-new-container">
                    <div class="whats-new-header">
                        <h2>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clip-rule="evenodd"/></svg>
                            What's New
                        </h2>
                    </div>
                    <div class="whats-new-grid">
                        <!-- New recommendation: HCQ retinopathy screening -->
                        <div class="whats-new-item" onclick="openModal('rec-18')">
                            <div class="whats-new-badge new">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/></svg>
                            </div>
                            <div class="whats-new-content">
                                <div class="whats-new-label new">New Recommendation</div>
                                <div class="whats-new-title">Retinopathy screening for adults taking hydroxychloroquine</div>
                                <div class="whats-new-meta">March 2026 • RA, SLE</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
```

The JIA page has never had a hero panel; the gateway section covers JIA recommendations.
