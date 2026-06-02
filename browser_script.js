// ==UserScript==
// @name         Cajón TPV
// @namespace    http://tampermonkey.net/
// @version      1.0
// @match        https://ecosoftweb.net/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// ==/UserScript==

(function () {
    'use strict';

    const SELECTORS = ['button.open_drawer', 'button.finish', '.open_drawer', '.finish'];
    const ENDPOINT = 'http://127.0.0.1:6543/open-drawer';

    function openDrawer() {
        GM_xmlhttpRequest({ method: 'GET', url: ENDPOINT });
    }

    function attachListeners() {
        SELECTORS.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                if (!el.dataset.cajonHooked) {
                    el.addEventListener('click', openDrawer);
                    el.dataset.cajonHooked = '1';
                }
            });
        });
    }

    new MutationObserver(attachListeners)
        .observe(document.body, { childList: true, subtree: true });

    attachListeners();
})();