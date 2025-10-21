# SVG-Pro
An AI-Powered SVG Editor and Research Tool for Text-to-SVG Generation

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-PySide6-2796EC.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

---

SVG-Pro is a desktop application designed for real-time SVG editing and generation, powered by a local Large Language Model (LLM) via Ollama. This project serves as a research tool and a conceptual benchmark to evaluate the spatial and visual reasoning capabilities of LLMs in generating Scalable Vector Graphics from natural language prompts.

It features a live-preview editor, a sophisticated AI chat assistant, syntax highlighting, and dual-theme support for a modern user experience.

### Demonstration

![SVG-Pro AI Assistant in Action](https://github.com/user-attachments/assets/56c7a4f5-4deb-45d5-8c8b-13ab6290bd5d)

### Key Features

*   **Live SVG Editor**: Write SVG code and see your changes rendered in real-time.
*   **AI Assistant**: Generate SVG code from natural language prompts using a local LLM. The assistant is specifically prompted to provide valid, clean SVG.
*   **Real-time Scalable Preview**: The preview panel automatically scales the SVG to fit the viewport while maintaining its aspect ratio.
*   **Syntax Highlighting**: The code editor provides clear and readable syntax highlighting for SVG/XML.
*   **Code Formatting**: Automatically format and prettify your SVG code with a single click.
*   **Dual Theme Support**: Switch between a professional Dark Mode and a clean Light Mode to suit your preference.
*   **Modern UI**: Built with PySide6, the application offers a responsive and intuitive user interface.
*   **File Management**: Standard new, open, and save file operations are fully supported.

### Screenshots

The application features a clean, modern interface with both light and dark themes for optimal viewing comfort.

| Dark Theme | Light Theme |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/b9d432b6-774c-43f1-855d-02e59f0a0f86" alt="Dark Theme" width="100%"> | <img src="https://github.com/user-attachments/assets/b6582dee-3605-402f-960f-20a31bd0a7f9" alt="Light Theme" width="100%"> |

**AI Assistant Chat Interface**

![Chat Interface](https://github.com/user-attachments/assets/71aa374c-dcff-4ab6-b69a-8c3fbf9cca8c)

---

### Project Philosophy: A Benchmark for Visual AI

SVG-Pro was created not as a consumer-facing SVG generator, but as a research platform. The primary objective is to test and benchmark the ability of language models to translate abstract textual descriptions into precise, structured, and visually accurate SVG code.

It is a concept in development, meant to explore the frontier of an LLM's visual intelligence. It is **not** intended as a production-ready SVG generator. The default model (`qwen3:8b`) is a general-purpose model and will often struggle with complex requests, producing only simple shapes or malformed geometry. This is by design to highlight the current limitations and challenges in this domain.

However, the framework is designed to be model-agnostic. By swapping in a more capable, visually-trained model, SVG-Pro could potentially become a powerful generative tool. This project is offered as a foundation for developers and researchers interested in the field of generative vector graphics.

---

### Prerequisites

*   Python 3.8 or newer.
*   [Ollama](https://ollama.com/) installed and running.
*   Git for cloning the repository.

### Installation and Setup

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/dovvnloading/SVG-Pro.git
    cd SVG-Pro
    ```

2.  **Install Python Dependencies**
    The application requires `PySide6`, `ollama`, and `Markdown`. Install them using pip:
    ```sh
    pip install PySide6 ollama Markdown
    ```

3.  **Set Up the Language Model**
    This project uses Ollama to run a local language model. You must pull the model specified in the code (or change it to one you have).
    
    Pull the default model (`qwen3:8b`):
    ```sh
    ollama run qwen3:8b
    ```
    *Ensure the Ollama application or service is running in the background before starting SVG-Pro.*

4.  **Run the Application**
    Execute the main Python script to launch the editor:
    ```sh
    python SVG_render.py
    ```

### Usage

*   Launch the application after completing the setup steps.
*   Use the **Code Editor** tab for manual SVG editing. The preview on the right will update as you type.
*   Navigate to the **AI Assistant** tab to interact with the LLM. Type a description of the SVG you want to create and press Send.
*   The AI will generate SVG code, which will automatically be formatted and loaded into the Code Editor.
*   Use the toolbar buttons for file operations (New, Open, Save), code formatting, and toggling the application theme.

### Contributing

Contributions are welcome and encouraged. This is a research project intended to be a resource for the community. Whether you are fixing a bug, adding a feature, or improving the documentation, your input is valuable.

To contribute:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some YourFeature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a new Pull Request.

Feel free to copy, modify, or use the code for your own research or projects.

### License

This project is licensed under the **MIT License**.

In the spirit of open research, you are free to use, modify, distribute, and build upon this project for any purpose without any restrictions. See the `LICENSE` file for full details.
