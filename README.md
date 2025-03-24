# Screen OCR & AI Answer Tool
为了解决浏览器考试无法切屏问题，做一个工具，方便自己薅羊毛。
这是一个基于 Python 的屏幕文字识别与 AI 回答工具，支持通过拖动鼠标选择屏幕区域，识别其中包含的中文、英文和数字混合文本，并通过 DeepSeek API 获取智能回答。识别结果和 AI 回答显示在带有滚动条的窗口中，适合考试、学习或其他需要快速解答的场景。

## 功能特点
- **精准区域选择**：全屏半透明黑色遮罩，拖动时显示白色高亮区域，直观选择屏幕内容。
- **多语言文字识别**：支持中文、英文和数字的混合文本，使用 Tesseract OCR。
- **AI 智能回答**：通过 DeepSeek API 将识别的文字作为问题，获取详细回答。
- **滚动显示**：结果窗口支持滚动条，适合长文本。
- **灵活操作**：支持多次识别同一区域或重新选择区域。

## 安装

### 环境要求
- Python 3.6+
- Windows（代码中使用 Windows 路径，可根据需要修改为其他系统）

### 依赖安装
1. 安装 Python 依赖：
   ```bash
   pip install pyautogui pytesseract pillow openai
   ```
   
3. 配置 DeepSeek API：
   - 获取 API 密钥（当前代码使用 `sk-9f7fc547b6b14901b4`，建议替换为个人密钥）。

## 使用方法

1. **运行程序**：
   ```bash
   python pic2ai2answe11r.py
   ```

## 常见问题
1. **文字识别不准确**：
   - 确保区域足够大，文字清晰。
2. **API 调用失败**：
   - 确认网络连接正常。
   - 检查 API 密钥是否有效。
3. **全屏遮罩异常**：
   - 测试多显示器环境，可能需要调整坐标计算。

## 贡献
欢迎提交 PR 或 Issue：
- 优化 OCR 参数以提高识别率。
- 添加图像预处理功能（如灰度化、二值化）。
- 支持其他 AI API（如 OpenAI、Grok 等）。

## 许可证
本项目采用 [MIT 许可证](LICENSE)。欢迎自由使用和修改。

## 致谢
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [DeepSeek API](https://deepseek.com/)
- [xAI](https://x.ai/)（灵感来源）

---

### **使用说明**
1. 将上述内容保存为 `README.md` 文件。
2. 如果需要，可以添加一个 `LICENSE` 文件（例如 MIT 许可证内容）。
3. 在 GitHub 上创建仓库，将代码和 `README.md` 上传：
   ```bash
   git init
   git add script.py README.md
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
