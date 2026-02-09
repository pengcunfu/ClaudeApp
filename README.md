# Claude Configuration Manager - Resources

此目录用于存放应用程序资源文件。

## 目录结构

```
resources/
├── icons/          # 图标文件
├── styles/         # 样式表文件
├── themes/         # 主题文件
└── README.md       # 本文件
```

## 资源说明

### 当前状态
目前应用程序使用系统默认样式(Windows Vista风格)。

### 未来扩展
- 可在此添加自定义图标
- 可添加 QSS 样式表文件
- 可添加应用程序主题配置

## 开发说明

如需添加自定义资源,请遵循以下约定:

1. **图标文件**: 放置在 `icons/` 目录,建议使用 SVG 格式以支持高DPI
2. **样式文件**: 放置在 `styles/` 目录,使用 .qss 扩展名
3. **主题配置**: 放置在 `themes/` 目录,使用 JSON 格式
