# OCR-GUI-demo

#### 介绍
图像文字识别OCR工具v1.1，含GUI界面。


本代码来源于[gitee仓库](https://gitee.com/signal926/ocr-gui-demo)

修复了闪退Bug，以及修改加载模型的逻辑，只有当第一次使用模型时才会去加载，大大节省时间。

## 安装与启动（快速）

1. 推荐使用虚拟环境：

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   ```

2. 一键安装依赖（项目根目录）：

   ```powershell
   pip install -r requirements.txt
   ```

3. 启动：

   ```powershell
   python main.py
   ```

> 注意：如果没有 GPU，请安装 CPU 版 PaddlePaddle；如需 GPU，请根据 CUDA 版本安装匹配的 PaddlePaddle GPU 轮子。