// ==UserScript==
// @name         我不要头像动！
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  将所有 linux.do 域名下的 GIF 图片链接改为 PNG
// @author       onewhiteClaude
// @match        https://linux.do/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // 替换图片 src
    function replaceGifToPng(img) {
        const currentSrc = img.getAttribute('src');
        if (currentSrc && currentSrc.includes('linux.do') && currentSrc.includes('.gif')) {
            console.log('找到 GIF 图片:', currentSrc);
            const newSrc = currentSrc.replace(/\.gif($|\?)/i, '.png$1');
            console.log('替换为:', newSrc);
            img.setAttribute('src', newSrc);
        }
    }

    // 处理页面上现有的图片
    function processExistingImages() {
        const images = document.querySelectorAll('img[src*="linux.do"][src*=".gif"]');
        console.log('找到', images.length, '个 GIF 图片');
        images.forEach(replaceGifToPng);
    }

    // 监听属性变化的函数
    function handleAttributeChange(mutation) {
        if (mutation.type === 'attributes' &&
            mutation.attributeName === 'src' &&
            mutation.target.nodeName === 'IMG') {
            replaceGifToPng(mutation.target);
        }
    }

    // 处理新添加节点的函数
    function handleAddedNode(node) {
        // 直接处理如果是图片节点
        if (node.nodeName === 'IMG') {
            replaceGifToPng(node);
        }
        // 处理节点内的所有图片
        if (node.querySelectorAll) {
            const images = node.querySelectorAll('img[src*="linux.do"][src*=".gif"]');
            images.forEach(replaceGifToPng);
        }
    }

    // 监听新增的 DOM 元素
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            // 处理属性变化
            if (mutation.type === 'attributes') {
                handleAttributeChange(mutation);
            }
            // 处理节点添加
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(handleAddedNode);
            }
        });
    });

    // 配置 observer 选项
    const observerConfig = {
        childList: true,    // 监听子节点变化
        subtree: true,      // 监听所有后代节点
        attributes: true,   // 监听属性变化
        attributeFilter: ['src']  // 只监听 src 属性变化
    };

    // 开始监听
    observer.observe(document.body, observerConfig);

    // 初始化时处理现有图片
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', processExistingImages);
    } else {
        processExistingImages();
    }

    // 处理动态加载的内容
    window.addEventListener('load', processExistingImages);
    // 额外添加滚动事件监听，用于处理懒加载图片
    window.addEventListener('scroll', () => {
        requestAnimationFrame(processExistingImages);
    }, { passive: true });
})();