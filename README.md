# 🎨 墨韵丹青 —— AI 诗画生成系统

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**用代码重燃水墨温度，让算法传承东方美学**  
将《全唐诗》的意境转化为数字画卷，构建诗画共生的文化元宇宙




## 🌟 项目亮点

### 🖼️ 诗画互文
- 输入任意古诗词，30秒生成装裱完整的数字水墨卷轴
- 支持**五言绝句/七言律诗/宋词元曲**等多种体裁
- 智能解析"孤舟蓑笠翁"等300+经典意象符号

### 🎭 六朝风骨
- 复刻**宋代山水/唐代金碧/明清工笔**等历史画风
- 内置《芥子园画谱》数字化笔法库
- 支持自定义宣纸纹理与印章系统

### 🛡️ 文化基因
- MD5内容指纹防重复生成
- 诗词-绘画跨模态关联数据集
- 可扩展的传统美学符号库

## 🛠️ 技术架构

```mermaid
graph TD
    A[用户输入诗句] --> B(Jieba意象解析)
    B --> C{风格矩阵}
    C --> D[水墨渲染引擎]
    C --> E[青绿设色引擎]
    C --> F[工笔勾线引擎]
    D/E/F --> G[通义万相AI]
    G --> H[数字装裱系统]
    H --> I[输出高清卷轴]
