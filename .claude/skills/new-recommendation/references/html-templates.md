# HTML Templates Reference

Complete copy-paste templates for adding a new recommendation. Replace all `[PLACEHOLDER]` values.

---

## Strength indicator SVGs

Use the correct icon inside `.strength-indicator.[class]` on the card, and the correct badge text in the modal.

### Conditional For (plus icon)
```html
<div class="strength-indicator conditional-for">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
    </svg>
</div>
<span class="strength-label">Conditional<br/>For</span>
```
Badge: `<span class="strength-badge conditional-for">⊕ Conditional Recommendation For</span>`

### Conditional Against (minus icon)
```html
<div class="strength-indicator conditional-against">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd"/>
    </svg>
</div>
<span class="strength-label">Conditional<br/>Against</span>
```
Badge: `<span class="strength-badge conditional-against">⊖ Conditional Recommendation Against</span>`

### Strong For (double plus)
```html
<div class="strength-indicator strong-for">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
    </svg>
</div>
<span class="strength-label">Strong<br/>For</span>
```
Badge: `<span class="strength-badge strong-for">⊕⊕ Strong Recommendation For</span>`

### Strong Against (double minus)
```html
<div class="strength-indicator strong-against">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd"/>
    </svg>
</div>
<span class="strength-label">Strong<br/>Against</span>
```
Badge: `<span class="strength-badge strong-against">⊖⊖ Strong Recommendation Against</span>`

---

## Card template (Adult IA)

```html
<div class="recommendation-card" data-conditions="[ra psa axspa]" data-tags="[tag1 tag2]" onclick="openModal('rec-[N]')">
    <div class="card-header">
        <div>
            <div class="card-category">[Category Label]</div>
            <div class="card-title">[Card Title]</div>
        </div>
        <div class="card-strength">
            <!-- INSERT strength indicator + label from above -->
        </div>
    </div>
    <div class="card-body">
        <p class="card-recommendation">[Recommendation text — first ~2 sentences for preview]</p>
        <div class="card-tags">
            <span class="card-tag">[Tag 1]</span>
            <span class="card-tag">[Tag 2]</span>
        </div>
    </div>
    <div class="card-footer">
        <span class="card-link">View details <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd"/></svg></span>
        <span class="card-updated">Updated [Abbrev Month] [YYYY]</span>
    </div>
</div>
```

## Card template (JIA)

Same as Adult IA but:
- Remove `data-conditions` attribute entirely
- Change `openModal('rec-[N]')` to `openModal('jia-rec-[N]')`

---

## Modal template (Adult IA)

```html
<div class="modal-overlay" id="modal-rec-[N]">
    <div class="modal-content">
        <div class="modal-header">
            <div>
                <div class="modal-category">[Category Label]</div>
                <h2 class="modal-title">[Modal Title]</h2>
            </div>
            <button class="modal-close" onclick="closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/></svg></button>
        </div>
        <div class="modal-tabs-container"><div class="modal-tabs">
            <button type="button" class="modal-tab active" data-tab="recommendation" onclick="switchTab('rec-[N]', 'recommendation')">Recommendation</button>
            <button type="button" class="modal-tab" data-tab="etd" onclick="switchTab('rec-[N]', 'etd')">Evidence to Decision</button>
            <button type="button" class="modal-tab" data-tab="practical" onclick="switchTab('rec-[N]', 'practical')">Practical Info</button>
            <button type="button" class="modal-tab" data-tab="data" onclick="switchTab('rec-[N]', 'data')">Data</button>
            <button type="button" class="modal-tab" data-tab="moreinfo" onclick="switchTab('rec-[N]', 'moreinfo')">More Info</button>
        </div></div>
        <div class="modal-body">

            <!-- TAB 1: RECOMMENDATION -->
            <div class="tab-content active" id="rec-[N]-recommendation">
                <!-- INSERT strength badge from above -->
                <div class="recommendation-box">
                    <p>[Full recommendation text]</p>
                </div>
                <!-- OPTIONAL remark box: -->
                <div class="remark-box">
                    <p>[Remark text if applicable — delete this block if no remark]</p>
                </div>
                <div class="content-section">
                    <h3>Rationale</h3>
                    <p>[Rationale paragraph(s)]</p>
                </div>
            </div>

            <!-- TAB 2: EVIDENCE TO DECISION -->
            <div class="tab-content" id="rec-[N]-etd">
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Benefits and Harms</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Certainty of the Evidence</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Patient Values and Preferences</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Resource Use</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Equity</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Acceptability</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
                <div class="etd-domain">
                    <div class="etd-domain-header">
                        <span class="etd-domain-title">Feasibility</span>
                        <span class="etd-rating">[Rating]</span>
                    </div>
                    <div class="etd-domain-text"><p>[Assessment text]</p></div>
                </div>
            </div>

            <!-- TAB 3: PRACTICAL INFO -->
            <div class="tab-content" id="rec-[N]-practical">
                <div class="content-section">
                    <h3>Implementation</h3>
                    <p>[Implementation guidance]</p>
                </div>
                <!-- Add further content-section blocks as needed -->
            </div>

            <!-- TAB 4: DATA -->
            <div class="tab-content" id="rec-[N]-data">
                <div class="data-content">
                    <div class="pico-section">
                        <h3><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style="width:18px;height:18px;vertical-align:text-bottom;margin-right:6px;"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd"/></svg>PICO [N]: Clinical Question (PICO)</h3>
                        <p class="pico-text">[PICO statement]</p>
                    </div>
                    <div class="evidence-section">
                        <h3><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" style="width:18px;height:18px;vertical-align:text-bottom;margin-right:6px;"><path d="M10.75 16.82A7.462 7.462 0 0115 15.5c.71 0 1.396.098 2.046.282A.75.75 0 0018 15.06v-11a.75.75 0 00-.546-.721A9.006 9.006 0 0015 3a8.963 8.963 0 00-4.25 1.065V16.82zM9.25 4.065A8.963 8.963 0 005 3c-.85 0-1.673.118-2.454.339A.75.75 0 002 4.06v11a.75.75 0 00.954.721A7.462 7.462 0 015 15.5c1.579 0 3.042.487 4.25 1.32V4.065z"/></svg>Evidence Summaries</h3>
                        <ul class="evidence-list">
                            <li><a href="[GOOGLE_DRIVE_URL]" target="_blank">Initial Evidence Synthesis ([Full Month YYYY])</a></li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- TAB 5: MORE INFO -->
            <div class="tab-content" id="rec-[N]-moreinfo">
                <div class="panel-info">
                    <h3><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z"/></svg> Panel Members</h3>
                    <div class="panel-members">
                        <span class="panel-member chair">Prof Rachelle Buchbinder (Chair)</span>
                        <span class="panel-member chair">Dr Samuel Whittle (Facilitator)</span>
                        <span class="panel-member chair">Dr Sue Brennan (Facilitator)</span>
                        <!-- Add voting panel members: -->
                        <span class="panel-member">[Panel Member Name]</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 011.5 0V4h.25A2.75 2.75 0 0118 6.75v8.5A2.75 2.75 0 0115.25 18H4.75A2.75 2.75 0 012 15.25v-8.5A2.75 2.75 0 014.75 4H5V2.75A.75.75 0 015.75 2zm-1 5.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h10.5c.69 0 1.25-.56 1.25-1.25v-6.5c0-.69-.56-1.25-1.25-1.25H4.75z" clip-rule="evenodd"/></svg></div>
                    <div class="info-content">
                        <div class="info-label">Panel Meeting Date</div>
                        <div class="info-value">[Day Month YYYY]</div>
                    </div>
                </div>
            </div>

        </div><!-- end modal-body -->

        <div class="modal-footer">
            <div class="modal-footer-left">
                <span class="card-updated">Last updated: [Full Month YYYY]</span>
                <a href="https://docs.google.com/forms/d/e/1FAIpQLSevmap58hDjm9OAKdOB9gd1VSXUaRAIRn-q8XcYFgmwv2WczQ/viewform?usp=pp_url&entry.1797546299=[URL-ENCODED-REC-TITLE]" target="_blank" class="feedback-link">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M3 4a2 2 0 00-2 2v1.161l8.441 4.221a1.25 1.25 0 001.118 0L19 7.162V6a2 2 0 00-2-2H3z"/><path d="M19 8.839l-7.77 3.885a2.75 2.75 0 01-2.46 0L1 8.839V14a2 2 0 002 2h14a2 2 0 002-2V8.839z"/></svg>
                    Suggest feedback
                </a>
            </div>
            <div class="modal-footer-right">
                <a href="https://app.magicapp.org/#/guideline/LqRV3n" target="_blank" class="magicapp-link">View in MAGICapp <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clip-rule="evenodd"/><path fill-rule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clip-rule="evenodd"/></svg></a>
            </div>
        </div>

    </div><!-- end modal-content -->
</div><!-- end modal-overlay -->
```

---

## JIA modal differences

For JIA modals, make these changes to the template above:

1. `id="modal-jia-rec-[N]"`
2. All `switchTab('rec-[N]', ...)` → `switchTab('jia-rec-[N]', ...)`
3. All `id="rec-[N]-[tab]"` → `id="jia-rec-[N]-[tab]"`
4. Feedback form base URL: `1FAIpQLSfarxWPaubepAaUzvm3HLxMgM57JlzKRtej-eWcRt7vw4wBAg/viewform`
5. MAGICapp URL: `https://app.magicapp.org/#/guideline/10522/section/[SECTION_ID]`

---

## Remark box (optional)

Used when there is a qualifying remark accompanying the main recommendation. Place immediately after the `recommendation-box` div, before the rationale section:

```html
<div class="remark-box">
    <p>[Remark text]</p>
</div>
```

---

## Feedback URL encoding reference

Common characters to URL-encode in the `entry.1797546299` parameter:
- Space → `%20`
- `/` → `%2F`
- `(` → `%28`
- `)` → `%29`
- `:` → `%3A`
- `,` → `%2C`
- `&` → `%26`

Example: "Retinopathy screening for adults taking hydroxychloroquine" → `Retinopathy%20screening%20for%20adults%20taking%20hydroxychloroquine`
