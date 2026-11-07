/* Site-wide search for livingguidelines.org.
   Loads /search-index.json (built by .claude/scripts/build_search_index.py) the first time the
   visitor focuses the header search box, then searches entirely in the browser. No server.
   Features: AND matching across words, light stemming (taper/tapering), abbreviation synonyms
   (MTX -> methotrexate), ranking by where the match is (title > recommendation > rationale),
   highlighted snippets, keyboard navigation, deep links that open the right recommendation and tab. */
(function () {
    'use strict';
    var root = document.querySelector('.site-search');
    if (!root) return;
    var input = root.querySelector('.site-search-input');
    var clearBtn = root.querySelector('.site-search-clear');
    var panel = root.querySelector('.site-search-panel');
    var index = null, loading = null, results = [], selected = -1, lastLogged = '';
    var STOP = { the: 1, of: 1, and: 1, or: 1, in: 1, for: 1, to: 1, a: 1, an: 1, with: 1, on: 1, at: 1, by: 1, is: 1, are: 1, be: 1, as: 1, it: 1, this: 1, that: 1, from: 1, who: 1, people: 1 };
    var MAX_RESULTS = 12;

    function loadIndex() {
        if (index || loading) return loading;
        loading = fetch('/search-index.json').then(function (r) { return r.json(); }).then(function (d) {
            d.entries.forEach(function (e) {
                e.ltitle = e.title.toLowerCase();
                e.sections.forEach(function (s) { s.ltext = s.text.toLowerCase(); });
            });
            index = d;
            return d;
        }).catch(function () { setStatus('Search is unavailable right now.'); });
        return loading;
    }

    function stem(w) {
        if (w.length <= 4) return w;
        if (/ies$/.test(w)) return w.slice(0, -3) + 'y';
        if (/(sses|xes|ches|shes)$/.test(w)) return w.slice(0, -2);
        if (/ing$/.test(w) && w.length > 5) return w.slice(0, -3);
        if (/ed$/.test(w) && w.length > 4) return w.slice(0, -2);
        if (/ly$/.test(w) && w.length > 4) return w.slice(0, -2);
        if (/s$/.test(w) && !/ss$/.test(w)) return w.slice(0, -1);
        return w;
    }
    function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
    function wordRe(term) {
        // short terms (RA, GC) must match whole words; longer ones match by stem prefix
        var t = esc(term);
        return term.length <= 3 ? new RegExp('(^|[^a-z0-9])' + t + '(?![a-z0-9])', 'g')
                                : new RegExp('(^|[^a-z0-9])' + t + '[a-z0-9]*', 'g');
    }

    // Each query word becomes a group of alternatives: its stem plus any synonyms.
    function parse(q) {
        var words = q.toLowerCase().replace(/[^a-z0-9/\-\s]/g, ' ').split(/\s+/).filter(function (w) { return w && !STOP[w]; });
        var syn = (index && index.synonyms) || {};
        return words.map(function (w) {
            var alts = [{ re: wordRe(stem(w)), raw: w }];
            (syn[w] || []).forEach(function (phrase) {
                alts.push({ re: new RegExp('(^|[^a-z0-9])' + esc(phrase).replace(/\s+/g, '\\s+'), 'g'), raw: phrase });
            });
            return { word: w, alts: alts };
        });
    }

    function countMatches(re, text) {
        re.lastIndex = 0; var n = 0;
        while (re.exec(text)) { n++; if (n >= 8) break; }
        return n;
    }

    function score(entry, groups, phraseRe) {
        var total = 0, best = null, bestW = 0;
        for (var g = 0; g < groups.length; g++) {
            var found = 0, gBest = null, gW = 0;
            for (var a = 0; a < groups[g].alts.length; a++) {
                var re = groups[g].alts[a].re;
                var n = countMatches(re, entry.ltitle);
                if (n) { found += n * 10; if (gW < 10) { gW = 10; gBest = { title: true }; } }
                for (var s = 0; s < entry.sections.length; s++) {
                    var sec = entry.sections[s];
                    n = countMatches(re, sec.ltext);
                    if (n) {
                        found += sec.w * (1 + Math.min(n, 5) * 0.15);
                        if (sec.w > gW || (sec.w === gW && !gBest)) { gW = sec.w; gBest = { sec: sec, alt: re }; }
                    }
                }
            }
            if (!found) return null;          // every word must match somewhere
            total += found;
            if (gW > bestW) { bestW = gW; best = gBest; }
        }
        if (phraseRe) {
            if (countMatches(phraseRe, entry.ltitle)) total *= 2;
            else for (var i = 0; i < entry.sections.length; i++) if (countMatches(phraseRe, entry.sections[i].ltext)) { total *= 1.5; break; }
        }
        if (entry.type === 'about' && entry.badge !== 'Abbreviation') total *= 0.8; // recs first on ties
        return { entry: entry, score: total, best: best };
    }

    function snippetFor(entry, groups, best) {
        // Choose the highest-weighted *showable* section that contains a match (Category is scored but never shown);
        // fall back to the recommendation text when only the title matched.
        var sec = null, secW = -1;
        entry.sections.forEach(function (s) {
            if (s.snip === false || s.w <= secW) return;
            for (var g = 0; g < groups.length; g++) for (var a = 0; a < groups[g].alts.length; a++)
                if (countMatches(groups[g].alts[a].re, s.ltext)) { sec = s; secW = s.w; return; }
        });
        if (!sec) sec = entry.sections.filter(function (s) { return s.snip !== false; })[0];
        if (!sec) return { html: '', label: '' };
        var text = sec.text, lower = sec.ltext, pos = -1;
        for (var g = 0; g < groups.length && pos < 0; g++)
            for (var a = 0; a < groups[g].alts.length; a++) {
                var re = groups[g].alts[a].re; re.lastIndex = 0; var m = re.exec(lower);
                if (m) { pos = m.index + (m[1] ? m[1].length : 0); break; }
            }
        var start = Math.max(0, pos - 70), end = Math.min(text.length, start + 190);
        if (start > 0) { var sp = text.lastIndexOf(' ', start); if (sp > start - 20) start = sp + 1; }
        if (end < text.length) { var ep = text.indexOf(' ', end); if (ep > 0 && ep < end + 20) end = ep; }
        var out = escapeHtml(text.slice(start, end));
        groups.forEach(function (g) { g.alts.forEach(function (alt) {
            var r = new RegExp(alt.re.source, 'gi');
            out = out.replace(r, function (m, p1) { return p1 + '<mark>' + m.slice(p1.length) + '</mark>'; });
        }); });
        return { html: (start > 0 ? '…' : '') + out + (end < text.length ? '…' : ''), label: sec.label, tab: sec.tab };
    }

    function escapeHtml(s) { return s.replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

    function run(q) {
        q = q.trim();
        root.classList.toggle('has-query', q.length > 0);
        if (q.length < 2) { close(); return; }
        if (!index) { setStatus('Loading…'); loadIndex().then(function () { if (input.value.trim() === q) run(q); }); return; }
        var groups = parse(q);
        if (!groups.length) { close(); return; }
        var phraseRe = groups.length > 1 ? new RegExp('(^|[^a-z0-9])' + esc(q.toLowerCase()).replace(/\s+/g, '\\s+'), 'g') : null;
        results = [];
        for (var i = 0; i < index.entries.length; i++) {
            var r = score(index.entries[i], groups, phraseRe);
            if (r) results.push(r);
        }
        results.sort(function (a, b) { return b.score - a.score; });
        results = results.slice(0, MAX_RESULTS);
        render(q, groups);
        logSearch(q, results.length);
    }

    function hrefFor(r, snip) {
        var e = r.entry;
        if (e.type === 'about') return e.url;
        return e.url + (snip.tab && snip.tab !== 'recommendation' ? '/' + snip.tab : '');
    }

    function render(q, groups) {
        selected = -1;
        if (!results.length) {
            panel.innerHTML = '<div class="site-search-status">No matches for “' + escapeHtml(q) + '”. Try a drug name, condition or abbreviation.</div>';
            open(); return;
        }
        var html = '<ul class="site-search-list" role="listbox" id="site-search-listbox">';
        results.forEach(function (r, i) {
            var snip = snippetFor(r.entry, groups, r.best);
            var href = hrefFor(r, snip);
            var where = r.entry.type === 'about' ? snip.label : (snip.label ? 'in ' + snip.label : '');
            html += '<li role="option" id="site-search-opt-' + i + '" aria-selected="false" class="site-search-result" data-href="' + escapeHtml(href) + '">' +
                '<div class="site-search-head"><span class="site-search-badge ' + r.entry.type + '">' + escapeHtml(r.entry.badge) + '</span>' +
                '<span class="site-search-title">' + escapeHtml(r.entry.title) + '</span></div>' +
                (snip.html ? '<p class="site-search-snippet">' + snip.html + '</p>' : '') +
                (where ? '<div class="site-search-where">' + escapeHtml(where) + '</div>' : '') + '</li>';
        });
        html += '</ul><div class="site-search-foot"><kbd>↑</kbd> <kbd>↓</kbd> to move, <kbd>Enter</kbd> to open, <kbd>Esc</kbd> to close</div>';
        panel.innerHTML = html;
        open();
    }

    function setStatus(msg) { panel.innerHTML = '<div class="site-search-status">' + escapeHtml(msg) + '</div>'; open(); }
    function open() { root.classList.add('open'); input.setAttribute('aria-expanded', 'true'); }
    function close() { root.classList.remove('open'); input.setAttribute('aria-expanded', 'false'); selected = -1; }

    function go(href) {
        logClick(href);
        var here = location.pathname.replace(/index\.html$/, '');
        var target = href.split('#')[0].replace(/index\.html$/, '');
        close();
        if (target === here && href.indexOf('#') >= 0) {
            // same page: set the hash and ask scripts.js to open the modal (hashchange won't fire if unchanged)
            var hash = href.slice(href.indexOf('#'));
            if (location.hash === hash && window.checkHashAndOpenModal) window.checkHashAndOpenModal();
            else location.hash = hash;
        } else {
            location.href = href;
        }
    }

    function select(i) {
        var opts = panel.querySelectorAll('.site-search-result');
        if (!opts.length) return;
        selected = (i + opts.length) % opts.length;
        opts.forEach(function (o, k) { o.setAttribute('aria-selected', k === selected ? 'true' : 'false'); });
        input.setAttribute('aria-activedescendant', 'site-search-opt-' + selected);
        opts[selected].scrollIntoView({ block: 'nearest' });
    }

    // Google Analytics: search terms only, nothing identifying
    var logTimer = null;
    function logSearch(q, n) {
        clearTimeout(logTimer);
        logTimer = setTimeout(function () {
            if (q === lastLogged || q.length < 3 || typeof window.gtag !== 'function') return;
            lastLogged = q;
            window.gtag('event', 'search', { search_term: q, results: n });
        }, 1200);
    }
    function logClick(href) {
        if (typeof window.gtag === 'function') window.gtag('event', 'select_content', { content_type: 'search_result', item_id: href, search_term: input.value.trim() });
    }

    // Events
    var debounce = null;
    input.addEventListener('focus', function () { loadIndex(); if (results.length && input.value.trim().length >= 2) open(); });
    input.addEventListener('input', function () {
        clearTimeout(debounce);
        var v = input.value;
        debounce = setTimeout(function () { run(v); }, 120);
    });
    input.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); if (!root.classList.contains('open')) run(input.value); select(selected + 1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); select(selected - 1); }
        else if (e.key === 'Enter') {
            var opts = panel.querySelectorAll('.site-search-result');
            if (opts.length) { e.preventDefault(); go(opts[selected >= 0 ? selected : 0].getAttribute('data-href')); }
        }
        else if (e.key === 'Escape') { if (root.classList.contains('open')) { e.preventDefault(); close(); } else { input.value = ''; root.classList.remove('has-query'); } }
    });
    panel.addEventListener('mousedown', function (e) { e.preventDefault(); }); // keep input focus
    panel.addEventListener('click', function (e) {
        var li = e.target.closest('.site-search-result');
        if (li) go(li.getAttribute('data-href'));
    });
    clearBtn.addEventListener('click', function () { input.value = ''; root.classList.remove('has-query'); results = []; close(); input.focus(); });
    document.addEventListener('click', function (e) { if (!root.contains(e.target)) close(); });
    document.addEventListener('keydown', function (e) {
        // "/" focuses the search box unless the visitor is already typing somewhere
        if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); input.focus(); }
    });
})();
