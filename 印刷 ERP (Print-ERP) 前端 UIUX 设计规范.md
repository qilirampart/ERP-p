# 印刷 ERP (Print-ERP) 前端 UI/UX 设计规范

版本： V2.0 (Modern Bento Edition)

风格关键词： Linear 风格、便当盒布局 (Bento Grid)、通透感、沉浸式

核心目标： 摒弃传统后台的沉重感，打造类似 Notion/Linear 的现代 SaaS 体验。

------

## 1. 视觉系统配置 (Tailwind Config)

项目的视觉灵魂在于“高级灰”与“靛蓝”的搭配。请在 `tailwind.config.js` 中强制写入以下配置：

JavaScript

```
// tailwind.config.js
module.exports = {
  theme: {
    // 1. 字体：使用 Inter 获得最佳的数字显示效果（对报价很重要）
    fontFamily: {
      sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    },
    extend: {
      // 2. 色彩系统：弃用标准 Blue/Black，使用 Zinc/Indigo
      colors: {
        surface: '#F8FAFC',  // 全局背景：极浅灰 (Slate-50 变体)
        panel: '#FFFFFF',    // 卡片背景：纯白
        primary: '#4F46E5',  // 主色：靛蓝 (Indigo-600) 而非 Element Blue
        secondary: '#64748B',// 次要文字：Slate-500
        dark: '#0F172A',     // 深色强调：Slate-900 (用于侧边栏或特种卡片)
      },
      // 3. 阴影系统：强调悬浮感
      boxShadow: {
        'soft': '0 2px 10px rgba(0, 0, 0, 0.03)', // 常态卡片
        'float': '0 10px 30px rgba(79, 70, 229, 0.1)', // 重点元素/悬停
      },
      // 4. 圆角系统：大圆角
      borderRadius: {
        'xl': '12px',      // 按钮/输入框
        '2xl': '24px',     // Bento 卡片/模态框
      }
    }
  }
}
```

------

## 2. 核心组件规范 (Component Specs)

AI 在生成组件代码时，必须遵循以下 CSS 类组合：

### 2.1 "Bento Card" (标准内容容器)

所有功能模块（如表单、图表）必须包裹在 Bento 卡片中，而不是直接放在背景上。

- **类名规则：** `bg-white rounded-2xl p-6 border border-slate-200/60 transition-all hover:shadow-lg hover:-translate-y-0.5`
- **视觉特征：**
  - 大圆角 (24px)。
  - 极细的边框 (Slate-200, 60%透明度)。
  - **微交互：** 鼠标悬停时，卡片轻微上浮并加深阴影。

### 2.2 输入框 (Modern Input)

**严禁**使用 Element Plus 默认的深边框输入框。

- **风格：** 扁平化、无边框（常态）、浅灰背景。

- **覆盖样式 (SCSS)：**

  SCSS

  ```
  .el-input__wrapper {
    box-shadow: none !important; /* 去掉默认边框 */
    background-color: #F1F5F9;   /* Slate-100 */
    border-radius: 12px;
    padding: 8px 12px;
  }
  /* 聚焦时显示靛蓝光圈 */
  .el-input__wrapper.is-focus {
    background-color: #FFFFFF;
    box-shadow: 0 0 0 2px #4F46E5 !important; 
  }
  ```

### 2.3 按钮 (Action Button)

- **主按钮：** `bg-primary text-white shadow-float rounded-xl hover:bg-indigo-600`
- **次要按钮：** `bg-white text-slate-600 border border-slate-200 hover:bg-slate-50`
- **禁止：** 避免使用直角按钮，圆角统一为 `rounded-xl`。

### 2.4 侧边栏 (Navigation)

- **风格：** **浮动式 (Floating) / 通透式**。不再使用传统的“通顶深色侧边栏”。
- **布局：** 侧边栏与屏幕边缘有间隙（或背景透明），选中项使用 `bg-indigo-50 text-primary` 高亮，而不是深色背景。

------

## 3. 布局与层级策略

### 3.1 页面结构 (Z-Layout)

- **底层 (Background):** `#F8FAFC` (Surface)。
- **中层 (Content):** Bento Cards 拼图。
- **顶层 (Highlights):** 关键数据面板（如“实时算价”）可以使用 **深色模式 (`bg-slate-900`)** 或 **磨砂玻璃效果**，形成视觉重心。

### 3.2 字体排印 (Typography)

- **数字：** 金额、尺寸、库存必须使用等宽数字或 Inter 字体，字重 `font-bold`。
- **标签：** 字段名（Label）使用 `text-xs font-bold text-slate-400 uppercase tracking-wider`（小字号、粗体、全大写、宽字距），这是 Linear 风格的精髓。

------

## 4. 给 AI 的 Prompt 模板 (复制用)

在让 AI 开发具体页面（如“生产排程页”）时，请附带以下指令：

> UI 开发指令：
>
> 请使用 Vue 3 + Tailwind CSS 开发该页面，严格遵守 "Modern Bento" 设计规范：
>
> 1. **背景：** 全局背景色使用 `bg-slate-50`。
> 2. **容器：** 内容必须放在 `bg-white rounded-2xl border border-slate-200` 的卡片中。
> 3. **输入框：** 覆盖 Element Plus 样式，使用 `bg-slate-100` 无边框风格，聚焦时显示靛蓝光圈。
> 4. **颜色：** 主色使用 `Indigo-600`，文字颜色使用 `Slate-700`，不要使用纯黑。
> 5. **布局：** 采用 Grid 布局将页面分为不同的 Bento 板块。
> 6. **特殊要求：** 重要数据（如生产进度）请使用深色卡片 (`bg-slate-900 text-white`) 以突出显示。

------

## 5. 示例：样式覆盖代码 (全局 CSS)

将此代码存入 `src/styles/main.scss`：

SCSS

```
/* 引入字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background-color: #F8FAFC;
  color: #1E293B;
}

/* 覆盖 Element Plus 变量 - 注入靛蓝基因 */
:root {
  --el-color-primary: #4F46E5; /* Indigo 600 */
  --el-color-primary-light-3: #6366f1;
  --el-color-primary-light-9: #e0e7ff;
  --el-border-radius-base: 12px;
}

/* 强制卡片风格 */
.bento-card {
  background: #ffffff;
  border-radius: 24px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  transition: all 0.3s ease;
}

.bento-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.06);
}
```