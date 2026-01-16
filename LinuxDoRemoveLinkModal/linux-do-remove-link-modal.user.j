// ==UserScript==
// @name         Linux.do 移除外链确认
// @match        https://linux.do/*
// @run-at       document-start
// @grant        GM_addStyle
// @author       onewhitethreee
// ==/UserScript==



// 拦截点击事件
document.addEventListener('click', function (e) {
    const link = e.target.closest('a.normal-external-link-icon, a.risky-external-link-icon');
    if (link && link.href) {
        e.stopImmediatePropagation();
        e.stopPropagation();
        e.preventDefault();
        window.open(link.href, '_blank');
        return false;
    }
}, true);
