# Linux.do 移除外链确认

这是一个 Tampermonkey 用户脚本，用于移除 Linux.do 网站上点击外部链接时的确认弹窗，让外部链接直接在新标签页中打开。

## 功能

- 自动拦截外部链接的点击事件
- 跳过外链确认弹窗
- 直接在新窗口打开外部链接

## 安装方法

### 1. 安装 Tampermonkey 浏览器扩展

首先需要在浏览器中安装 Tampermonkey 扩展：

- **Chrome**: [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
- **Firefox**: [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)
- **Edge**: [Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd)
- **Safari**: [Safari Extensions](https://apps.apple.com/us/app/tampermonkey/id1482490089)

### 2. 安装脚本

安装 Tampermonkey 后，点击下面的链接安装脚本：

**[点击安装脚本](./linux-do-remove-link-modal.user.js)**

或者手动安装：

1. 打开 Tampermonkey 管理面板
2. 点击 "+" 创建新脚本
3. 复制 `linux-do-remove-link-modal.user.js` 中的代码
4. 粘贴到编辑器中
5. 保存（Ctrl+S 或 Cmd+S）

## 使用说明

安装完成后，访问 [Linux.do](https://linux.do/) 网站，点击任何外部链接时将不再显示确认弹窗，而是直接在新标签页中打开。

## 作者

[@onewhitethreee](https://github.com/onewhitethreee)

## 许可证

MIT
