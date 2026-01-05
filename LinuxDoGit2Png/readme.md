# Discourse GIF 转 PNG 用户脚本

一个简单的用户脚本，可以自动将 Discourse 论坛上的 GIF 图片链接转换为 PNG 格式。目前针对 linux.do 优化，但可以适配其他 Discourse 网站。

## 功能特点

- 自动将 GIF 图片链接转换为 PNG 格式
- 支持动态加载的内容
- 处理懒加载图片
- 针对 Discourse 论坛优化
- 性能影响小

## 安装方法

1. 首先安装一个用户脚本管理器：

   - [Tampermonkey](https://www.tampermonkey.net/)（推荐）
   - [Greasemonkey](https://www.greasespot.net/)
   - [Violentmonkey](https://violentmonkey.github.io/)

2. 点击此链接安装脚本：[安装脚本](../../raw/main/Gif2Png.user.js)

## 使用说明

安装后脚本会自动运行，无需额外配置。它会：

- 转换页面上现有的 GIF 图片
- 处理滚动时动态加载的图片
- 处理页面新增的图片

## 自定义配置

要在其他 Discourse 论坛上使用此脚本：

1. 在脚本管理器中打开脚本
2. 修改 `@match` 行以匹配目标论坛的网址
3. 保存更改

## 开发相关

如果你想修改脚本：

1. Fork 这个仓库
2. 进行修改
3. 在目标网站上测试脚本
4. 提交 Pull Request

## 开源协议

MIT 协议 - 您可以自由修改和使用

## 参与贡献

欢迎提供改进建议和贡献代码！请随时提交 Pull Request。

## 支持

如果遇到问题或有改进建议，请在此仓库创建 Issue。

## 更新日志

### v0.1

- 初始发布
- 支持将 GIF 图片转换为 PNG
- 支持动态加载的内容
