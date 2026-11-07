/* Shared header behaviour: the phone "Menu" button and click/keyboard-operable dropdowns.
   On desktop the dropdowns still open on hover; clicking or pressing Enter on a heading also
   toggles it, so keyboard users can reach the menu pages. */
(function () {
    'use strict';
    var header = document.querySelector('header');
    var toggle = document.querySelector('.menu-toggle');
    var nav = document.getElementById('site-nav');
    if (!header || !nav) return;

    function closeAll(except) {
        nav.querySelectorAll('.nav-item.open').forEach(function (it) {
            if (it !== except) { it.classList.remove('open'); it.querySelector('.nav-link').setAttribute('aria-expanded', 'false'); }
        });
    }
    function setMenu(open) {
        header.classList.toggle('menu-open', open);
        if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (!open) closeAll();
    }

    if (toggle) {
        toggle.addEventListener('click', function () { setMenu(!header.classList.contains('menu-open')); });
    }

    nav.querySelectorAll('.nav-item').forEach(function (item) {
        var link = item.querySelector('.nav-link');
        if (!link || !item.querySelector('.dropdown')) return;
        link.setAttribute('aria-haspopup', 'true');
        link.setAttribute('aria-expanded', 'false');
        link.addEventListener('click', function (e) {
            e.preventDefault();                       // the heading is a toggle, not a page
            var open = !item.classList.contains('open');
            closeAll(item);
            item.classList.toggle('open', open);
            link.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { closeAll(); setMenu(false); }
    });
    document.addEventListener('click', function (e) {
        if (!header.contains(e.target)) { closeAll(); if (header.classList.contains('menu-open')) setMenu(false); }
    });
    // close the phone menu if the window grows to desktop width
    window.addEventListener('resize', function () { if (window.innerWidth > 768 && header.classList.contains('menu-open')) setMenu(false); });
})();
