import sys
import re
import json
import logging
import multiprocessing
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET
import html
import markdown
import base64

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLabel, QSplitter, QMessageBox,
    QToolBar, QStatusBar, QFileDialog, QFontDialog, QPushButton,
    QFrame, QScrollArea, QLineEdit, QTabWidget, QTextBrowser,
    QSizePolicy, QSpacerItem
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, Qt, QSize, QRectF, QObject, QThread, Signal, QPointF
from PySide6.QtGui import (
    QIcon, QFont, QTextCharFormat, QSyntaxHighlighter,
    QPalette, QColor, QPainter, QPixmap, QPainterPath, QPen, QBrush
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, model_name: str, messages: List[Dict], options: Dict):
        super().__init__()
        self.model_name = model_name
        self.messages = messages
        self.options = options

    def run(self):
        try:
            import ollama
            response = ollama.chat(
                model=self.model_name,
                messages=self.messages,
                options=self.options
            )
            self.finished.emit(response['message']['content'])
        except Exception as e:
            logger.error(f"Error in OllamaWorker thread: {e}")
            self.error.emit(str(e))


class Theme:
    LIGHT = "light"
    DARK = "dark"

THEMES = {
    Theme.DARK: {
        "Window": "#1E1E1E",
        "WindowText": "#D4D4D4",
        "Base": "#252526",
        "AlternateBase": "#333333",
        "ToolTipBase": "#252526",
        "ToolTipText": "#D4D4D4",
        "Text": "#D4D4D4",
        "Button": "#3E3E42",
        "ButtonText": "#FFFFFF",
        "BrightText": "#FF0000",
        "Link": "#569CD6",
        "Highlight": "#264F78",
        "HighlightedText": "#FFFFFF",
        "Border": "#444444",
        "Accent": "#007ACC",
        "AccentHover": "#1188DD",
        "AccentPressed": "#006AB1",
        "Success": "#4EC9B0",
        "Error": "#F44747",
        "EditorTag": "#569CD6",
        "EditorAttribute": "#9CDCFE",
        "EditorValue": "#CE9178",
        "EditorComment": "#6A9955",
        "ChatUser": "#005F9E",
        "ChatUserText": "#FFFFFF",
        "ChatAI": "#2D2D2D",
        "ChatAIText": "#D4D4D4",
        "ChatMeta": "#888888",
        "PreviewBackground": "#1E1E1E",
    },
    Theme.LIGHT: {
        "Window": "#F0F0F0",
        "WindowText": "#000000",
        "Base": "#FFFFFF",
        "AlternateBase": "#EAEAEA",
        "ToolTipBase": "#FFFFFF",
        "ToolTipText": "#000000",
        "Text": "#000000",
        "Button": "#E1E1E1",
        "ButtonText": "#000000",
        "BrightText": "#FF0000",
        "Link": "#0000FF",
        "Highlight": "#B4D5FF",
        "HighlightedText": "#000000",
        "Border": "#CCCCCC",
        "Accent": "#005FCC",
        "AccentHover": "#0078D7",
        "AccentPressed": "#004C99",
        "Success": "#107C10",
        "Error": "#A80000",
        "EditorTag": "#0000FF",
        "EditorAttribute": "#FF0000",
        "EditorValue": "#A31515",
        "EditorComment": "#008000",
        "ChatUser": "#CCE4F7",
        "ChatUserText": "#000000",
        "ChatAI": "#F0F0F0",
        "ChatAIText": "#000000",
        "ChatMeta": "#666666",
        "PreviewBackground": "#FFFFFF",
    }
}

def get_palette(theme_name: str) -> QPalette:
    colors = THEMES[theme_name]
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(colors["Window"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["WindowText"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(colors["Base"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["AlternateBase"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["ToolTipBase"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["ToolTipText"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(colors["Text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(colors["Button"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["ButtonText"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["BrightText"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(colors["Link"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["Highlight"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["HighlightedText"]))
    return palette

def get_stylesheet(theme_name: str) -> str:
    colors = THEMES[theme_name]
    return f"""
        QWidget {{
            color: {colors["Text"]};
            font-family: Segoe UI, sans-serif;
            font-size: 10pt;
        }}
        QMainWindow {{
            background-color: {colors["Window"]};
        }}
        QTabWidget::pane {{
            border: 1px solid {colors["Border"]};
            border-top: none;
        }}
        QTabBar::tab {{
            background: {colors["Button"]};
            border: 1px solid {colors["Border"]};
            border-bottom: none;
            padding: 8px 16px;
            color: {colors["ButtonText"]};
            font-weight: bold;
        }}
        QTabBar::tab:selected {{
            background: {colors["Base"]};
            border-bottom: 1px solid {colors["Base"]};
        }}
        QTabBar::tab:hover {{
            background: {colors["AlternateBase"]};
        }}
        QTextEdit, QTextBrowser {{
            background-color: {colors["Base"]};
            border: 1px solid {colors["Border"]};
            border-radius: 4px;
            padding: 8px;
            color: {colors["Text"]};
            selection-background-color: {colors["Highlight"]};
            selection-color: {colors["HighlightedText"]};
        }}
        QTextBrowser {{
            background-color: transparent;
            border: none;
        }}
        QPushButton {{
            background-color: {colors["Button"]};
            border: 1px solid {colors["Border"]};
            border-radius: 4px;
            color: {colors["ButtonText"]};
            padding: 8px 16px;
            font-size: 9pt;
        }}
        QPushButton:hover {{
            background-color: {colors["AlternateBase"]};
            border-color: {colors["AccentHover"]};
        }}
        QPushButton:pressed {{
            background-color: {colors["Highlight"]};
        }}
        QPushButton:disabled {{
            background-color: {colors["Border"]};
            color: {colors["ChatMeta"]};
        }}
        QLabel {{
            color: {colors["WindowText"]};
            padding: 2px 0px;
        }}
        QLineEdit {{
            background-color: {colors["Base"]};
            border: 1px solid {colors["Border"]};
            border-radius: 4px;
            padding: 8px;
            color: {colors["Text"]};
            selection-background-color: {colors["Highlight"]};
        }}
        QLineEdit:focus {{
            border: 1px solid {colors["Accent"]};
        }}
        QToolBar {{
            background-color: {colors["Window"]};
            border-bottom: 1px solid {colors["Border"]};
            spacing: 6px;
            padding: 6px;
        }}
        QStatusBar {{
            background: {colors["Window"]};
            color: {colors["Text"]};
            border-top: 1px solid {colors["Border"]};
            padding: 4px;
        }}
        QScrollArea {{
            background-color: {colors["Base"]};
            border-radius: 4px;
            border: 1px solid {colors["Border"]};
        }}
        QScrollBar:vertical {{
            border: none;
            background: {colors["Base"]};
            width: 12px;
            margin: 1px 0 1px 0;
        }}
        QScrollBar::handle:vertical {{
            background: {colors["AlternateBase"]};
            min-height: 20px;
            border-radius: 5px;
            border: 1px solid {colors["Border"]};
        }}
        QScrollBar::handle:vertical:hover {{
            background: {colors["Highlight"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {colors["Base"]};
            height: 12px;
            margin: 0 1px 0 1px;
        }}
        QScrollBar::handle:horizontal {{
            background: {colors["AlternateBase"]};
            min-width: 20px;
            border-radius: 5px;
            border: 1px solid {colors["Border"]};
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {colors["Highlight"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        QSplitter::handle {{
            background-color: {colors["Border"]};
        }}
        QSplitter::handle:hover {{
            background-color: {colors["Accent"]};
        }}
        QSplitter::handle:pressed {{
            background-color: {colors["AccentPressed"]};
        }}
    """

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: float = None

    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now().timestamp()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp
        }

class ChatSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(int(datetime.now().timestamp()))
        self.messages: List[Message] = []
        self.system_prompt: Optional[str] = None

    def add_message(self, message: Message):
        self.messages.append(message)

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def get_context_window(self, max_messages: int = 10) -> List[Message]:
        messages = []
        if self.system_prompt:
            messages.append(Message(
                role=MessageRole.SYSTEM,
                content=self.system_prompt
            ))
        messages.extend(self.messages[-max_messages:])
        return messages

    def save_to_file(self, filepath: str):
        data = {
            "session_id": self.session_id,
            "system_prompt": self.system_prompt,
            "messages": [msg.to_dict() for msg in self.messages]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'ChatSession':
        with open(filepath, 'r') as f:
            data = json.load(f)

        session = cls(session_id=data["session_id"])
        session.system_prompt = data["system_prompt"]
        session.messages = [
            Message(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in data["messages"]
        ]
        return session

class AIModelConfig:
    def __init__(
        self,
        model_name: str = "qwen3:8b",
        temperature: float = 0.7,
        max_tokens: int = 20000,
        top_p: float = 0.95,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

class SVGExpertAgent:
    def __init__(self):
        self.session = ChatSession()
        self.model_config = AIModelConfig(
            model_name="qwen3:8b",
            temperature=0.7,
            max_tokens=20000
        )

        self.session.set_system_prompt("""You are a specialized SVG code generation assistant.
Your sole purpose is to provide valid, complete SVG code based on user requests.

**CRITICAL RULES:**
1.  **SVG ONLY:** Your response MUST contain a valid SVG code block.
2.  **MANDATORY FORMAT:** The response format is NOT optional. Any deviation will result in failure.
    -   Explanations or text MUST come BEFORE the code block.
    -   The code block MUST start with ```xml or ```svg.
    -   The final part of your response MUST be the closing ``` of the code block.
3.  **NO TEXT AFTER:** There must be absolutely NO text, explanation, or any characters after the final ``` that closes the code block.

**EXAMPLE OF A PERFECT RESPONSE:**
Here is the SVG for a simple blue circle.
```xml
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="blue" />
</svg>
```
Failure to adhere to this format will render your output useless. Do not fail.""")

    def get_response(self, user_message: str, callback):
        self.session.add_message(Message(
            role=MessageRole.USER,
            content=user_message
        ))

        context = self.session.get_context_window()

        messages = [msg.to_dict() for msg in context]
        options = {
            "temperature": self.model_config.temperature,
            "top_p": self.model_config.top_p,
            "num_predict": self.model_config.max_tokens,
            "frequency_penalty": self.model_config.frequency_penalty,
            "presence_penalty": self.model_config.presence_penalty
        }

        callback(self.model_config.model_name, messages, options)

    def save_session(self, filepath: str):
        self.session.save_to_file(filepath)

    def load_session(self, filepath: str):
        self.session = ChatSession.load_from_file(filepath)

class ModernButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon_name:
            self.setIcon(QIcon(f":/icons/{icon_name}"))

class ScalableSvgWidget(QSvgWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 700)

    def paintEvent(self, event):
        if not self.renderer().isValid():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        viewport = QRectF(0, 0, self.width(), self.height())
        svg_size = self.renderer().defaultSize()

        scaled_size = svg_size.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio)

        x = (self.width() - scaled_size.width()) / 2
        y = (self.height() - scaled_size.height()) / 2

        self.renderer().render(painter, QRectF(x, y, scaled_size.width(), scaled_size.height()))

class SVGHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self.theme_colors = THEMES[Theme.DARK]

        self.tag_format = QTextCharFormat()
        self.tag_format.setFontWeight(QFont.Weight.Bold)

        self.attribute_format = QTextCharFormat()
        self.value_format = QTextCharFormat()
        self.comment_format = QTextCharFormat()

        self.update_theme(self.theme_colors)

    def update_theme(self, colors: Dict[str, str]):
        self.theme_colors = colors

        self.tag_format.setForeground(QColor(colors["EditorTag"]))
        self.attribute_format.setForeground(QColor(colors["EditorAttribute"]))
        self.value_format.setForeground(QColor(colors["EditorValue"]))
        self.comment_format.setForeground(QColor(colors["EditorComment"]))

        self.highlighting_rules = [
            (re.compile(r'</?[\w:-]+'), self.tag_format),
            (re.compile(r'>|/>'), self.tag_format),
            (re.compile(r'[\w:-]+(?=\=)'), self.attribute_format),
            (re.compile(r'"[^"]*"'), self.value_format),
            (re.compile(r'<!--[\s\S]*?-->'), self.comment_format)
        ]
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class PreviewFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        self.svg_widget = ScalableSvgWidget()
        self.container_layout.addWidget(self.svg_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)

    def set_background_color(self, color: str):
        self.container.setStyleSheet(f"background-color: {color};")
        self.scroll_area.setStyleSheet(f"background-color: {color}; border: none;")

class ChatMessageWidget(QWidget):
    def __init__(self, text, is_user, theme_colors, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.theme_colors = theme_colors

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.bubble_frame = QFrame()
        self.bubble_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.bubble_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        bubble_layout = QVBoxLayout(self.bubble_frame)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(0)

        self.text_display = QLabel()
        self.text_display.setText(text)
        self.text_display.setWordWrap(True)
        self.text_display.setOpenExternalLinks(True)
        self.text_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.text_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        bubble_layout.addWidget(self.text_display)
        self.bubble_frame.setLayout(bubble_layout)

        layout.addWidget(self.bubble_frame)
        self.setLayout(layout)

        self.update_theme(theme_colors)

    def set_min_width(self, width: int):
        self.bubble_frame.setMinimumWidth(width)

    def set_max_width(self, width: int):
        self.bubble_frame.setMaximumWidth(width)

    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        bg = theme_colors["ChatUser" if self.is_user else "ChatAI"]
        text = theme_colors["ChatUserText" if self.is_user else "ChatAIText"]
        border = theme_colors["Border" if self.is_user else "ChatAI"]

        self.bubble_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 16px;
                border: 1px solid {border};
            }}
        """)

        self.text_display.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {text};
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            a {{
                color: {theme_colors['Link']};
                text-decoration: underline;
            }}
        """)
        self.text_display.setText(self.text_display.text())

class ModernChatWidget(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.agent = SVGExpertAgent()
        self.theme_colors = THEMES[Theme.DARK]
        self.md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])
        self.thinking_widget = None
        self.max_retries = 2
        self.current_retries = 0
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch(1)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)

        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 12, 15, 12)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask for an SVG design...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = ModernButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        main_layout.addWidget(input_container)

        self.update_theme(self.theme_colors)
    
    def get_markdown_styles(self, is_user) -> str:
        colors = self.theme_colors
        text_color = colors['ChatUserText' if is_user else 'ChatAIText']
        code_bg = colors['Window' if self.theme_colors == THEMES[Theme.DARK] else 'AlternateBase']
        code_text = colors['EditorValue']
        
        return f"""
        <style>
            p {{ margin: 0; padding-bottom: 8px; color: {text_color}; }}
            p:last-child {{ padding-bottom: 0; }}
            ul, ol {{ margin-top: 5px; margin-bottom: 8px; padding-left: 20px; color: {text_color}; }}
            li {{ margin-bottom: 4px; }}
            a {{ color: {colors['Link']}; }}
            pre {{
                background-color: {code_bg};
                border: 1px solid {colors['Border']};
                padding: 10px;
                border-radius: 5px;
                font-family: 'Cascadia Code', 'Courier New', monospace;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            code {{
                font-family: 'Cascadia Code', 'Courier New', monospace;
                background-color: {code_bg};
                padding: 2px 4px;
                border-radius: 3px;
                font-size: 9pt;
                color: {code_text};
            }}
            pre > code {{
                background-color: transparent;
                padding: 0;
                border: none;
            }}
            blockquote {{
                border-left: 3px solid {colors['Accent']};
                padding-left: 10px;
                margin-left: 5px;
                color: {colors['ChatMeta']};
                font-style: italic;
            }}
        </style>
        """

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_all_message_widths()

    def _update_all_message_widths(self):
        viewport_width = self.scroll_area.viewport().width()
        max_width = viewport_width * 0.70
        min_width = viewport_width * 0.20
        
        if max_width <= 0:
            return

        for i in range(self.chat_layout.count() - 1):
            item = self.chat_layout.itemAt(i)
            if item and item.widget():
                container_widget = item.widget()
                message_widget = container_widget.findChild(ChatMessageWidget)
                if message_widget:
                    message_widget.set_max_width(int(max_width))
                    message_widget.set_min_width(int(min_width))

    def update_theme(self, colors: Dict[str, str]):
        self.theme_colors = colors
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {colors["Base"]};
                border: 1px solid {colors["Border"]};
                border-bottom: none;
                border-radius: 8px 8px 0 0;
            }}
        """)
        
        input_container = self.findChild(QFrame, "inputContainer")
        if input_container:
            input_container.setStyleSheet(f"""
                QFrame#inputContainer {{
                    background-color: {colors["Window"]};
                    border: 1px solid {colors["Border"]};
                    border-top: 1px solid {colors["Border"]};
                    border-radius: 0 0 8px 8px;
                }}
            """)

        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors["Base"]};
                border: 1px solid {colors["Border"]};
                border-radius: 4px;
                padding: 8px 12px;
                color: {colors["Text"]};
            }}
            QLineEdit:focus {{
                border-color: {colors["Accent"]};
            }}
            QLineEdit::placeholder {{
                color: {colors["ChatMeta"]};
            }}
        """)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors["Accent"]};
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors["AccentHover"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["AccentPressed"]};
            }}
            QPushButton:disabled {{
                background-color: {colors["Button"]};
                color: {colors["ButtonText"]};
            }}
        """)

        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        if self.thinking_widget:
            self.thinking_widget.deleteLater()
            self.thinking_widget = None
        
        for message in self.agent.session.messages:
            if message.role == MessageRole.USER:
                is_user = True
                escaped_message = html.escape(message.content).replace('\n', '<br>')
                html_content = self.get_markdown_styles(is_user) + f'<p>{escaped_message}</p>'
                self._add_message_widget(html_content, is_user)

            elif message.role == MessageRole.ASSISTANT:
                is_user = False
                response_text = message.content
                match = re.search(r'```(xml|svg)\s*\n([\s\S]*?)\n```', response_text)
                
                chat_text = response_text
                if match:
                    chat_text = response_text.replace(match.group(0), '').strip()
                    if not chat_text:
                        chat_text = "> [SVG code has been inserted into the editor]"
                    else:
                        chat_text += "\n> [SVG code has been inserted into the editor]"
                
                html_content = self.get_markdown_styles(is_user) + self.md.convert(chat_text)
                self._add_message_widget(html_content, is_user)
        
        self._update_all_message_widths()

    def _add_message_widget(self, text, is_user):
        message_widget = ChatMessageWidget(text, is_user, self.theme_colors)
        
        viewport_width = self.scroll_area.viewport().width()
        max_width = viewport_width * 0.70
        min_width = viewport_width * 0.20
        
        if max_width > 0:
            message_widget.set_max_width(int(max_width))
            message_widget.set_min_width(int(min_width))

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        if is_user:
            layout.addStretch()
            layout.addWidget(message_widget)
        else:
            layout.addWidget(message_widget)
            layout.addStretch()

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        
        QApplication.processEvents()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def _start_worker(self, model_name, messages, options):
        self.thread = QThread(self)
        self.worker = OllamaWorker(model_name, messages, options)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._handle_ai_response)
        self.worker.error.connect(self._handle_ai_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        
    def _trigger_ai_call(self):
        context = self.agent.session.get_context_window()

        messages = [msg.to_dict() for msg in context]
        options = {
            "temperature": self.agent.model_config.temperature,
            "top_p": self.agent.model_config.top_p,
            "num_predict": self.agent.model_config.max_tokens,
            "frequency_penalty": self.agent.model_config.frequency_penalty,
            "presence_penalty": self.agent.model_config.presence_penalty
        }
        self._start_worker(self.agent.model_config.model_name, messages, options)

    def _retry_ai_request(self, reason: str):
        if self.current_retries < self.max_retries:
            self.current_retries += 1
            logger.info(f"AI response failed: {reason}. Retrying... (Attempt {self.current_retries}/{self.max_retries})")

            if self.thinking_widget:
                self.thinking_widget.setText(f"<i>AI response invalid. Retrying... (Attempt {self.current_retries}/{self.max_retries})</i>")

            reprompt_message = (
                f"Your previous response was invalid. Reason: {reason}\n\n"
                "You MUST follow the strict formatting rules. Your response MUST contain a valid SVG code block. "
                "The code block must start with ```xml or ```svg. "
                "There must be absolutely no text after the final ``` that closes the code block. "
                "Please try again and provide a correctly formatted response for the last user request."
            )
            self.agent.session.add_message(Message(role=MessageRole.USER, content=reprompt_message))
            self._trigger_ai_call()
        else:
            logger.error("AI failed to provide a valid response after all retries.")
            error_message = f"The AI failed to provide a valid SVG response after {self.max_retries + 1} attempts. Please try rephrasing your request."
            self._handle_final_failure(error_message)

    def _handle_ai_response(self, response_text):
        if not response_text or not response_text.strip():
            self._retry_ai_request("The AI returned an empty response.")
            return

        match = re.search(r'```(xml|svg)\s*\n([\s\S]*?)\n```', response_text)
        if not match:
            self._retry_ai_request("AI response did not contain a valid SVG code block.")
            return

        self.current_retries = 0
        self.agent.session.add_message(Message(role=MessageRole.ASSISTANT, content=response_text))
        
        if self.thinking_widget:
            self.thinking_widget.deleteLater()
            self.thinking_widget = None

        svg_code = match.group(2).strip()
        chat_text = response_text.replace(match.group(0), '').strip()
        
        if not chat_text:
             chat_text = "> [SVG code has been inserted into the editor]"
        else:
            chat_text += "\n> [SVG code has been inserted into the editor]"

        html_content = self.get_markdown_styles(False) + self.md.convert(chat_text)
        self._add_message_widget(html_content, False)
        
        if svg_code:
            self.editor.update_editor_with_svg(svg_code)

        self.send_button.setEnabled(True)
        self.input_field.setFocus()

    def _handle_final_failure(self, error_message: str):
        if self.thinking_widget:
            self.thinking_widget.deleteLater()
            self.thinking_widget = None

        error_color = self.theme_colors["Error"]
        html_content = self.get_markdown_styles(False) + f'<b style="color:{error_color};">ERROR</b><br>{html.escape(error_message)}'
        self._add_message_widget(html_content, False)
        
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
        self.current_retries = 0

    def _handle_ai_error(self, error_message: str):
        logger.error(f"Ollama worker error: {error_message}")
        final_message = f"An unexpected error occurred while communicating with the AI: {error_message}"
        self._handle_final_failure(final_message)

    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self.send_button.setEnabled(False)
        self.input_field.clear()
        
        escaped_message = html.escape(user_message).replace('\n', '<br>')
        html_content = self.get_markdown_styles(True) + f'<p>{escaped_message}</p>'
        self._add_message_widget(html_content, True)

        self.thinking_widget = QLabel("<i>AI is thinking...</i>")
        self.thinking_widget.setStyleSheet(f"color: {self.theme_colors['ChatMeta']}; padding-left: 15px;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.thinking_widget)
        
        QApplication.processEvents()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        
        self.current_retries = 0
        self.agent.session.add_message(Message(role=MessageRole.USER, content=user_message))
        self._trigger_ai_call()

class SVGEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = Theme.DARK
        self.initUI()
        self.apply_theme()

    def initUI(self):
        self.setWindowTitle("SVG Pro")
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowIcon(self.create_cube_icon())

        self.createToolbar()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(4)

        self.tool_tabs = QTabWidget()

        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0,0,0,0)
        self.code_editor = QTextEdit()
        self.highlighter = SVGHighlighter(self.code_editor.document())
        font = QFont("Cascadia Code", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.code_editor.setFont(font)
        self.code_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.code_editor.textChanged.connect(self.update_svg)
        editor_layout.addWidget(self.code_editor)
        self.tool_tabs.addTab(editor_widget, "Code Editor")

        self.chat_widget = ModernChatWidget(editor=self)
        self.tool_tabs.addTab(self.chat_widget, "AI Assistant")

        self.preview_frame = PreviewFrame()
        
        main_splitter.addWidget(self.tool_tabs)
        main_splitter.addWidget(self.preview_frame)
        
        # --- FIX IMPLEMENTED ---
        # This locks the left panel (the QTabWidget containing the editor and chat)
        # to an absolute, fixed width. It will not scale when the window is resized.
        self.tool_tabs.setFixedWidth(550)
        # ---------------------

        self.setCentralWidget(main_splitter)

        self.load_default_svg()

    def create_cube_icon(self) -> QIcon:
        svg_data = """
        <svg width="256" height="256" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(50,50) scale(0.8)">
            <path d="M 0,-40 L 34.64,-20 L 34.64,20 L 0,40 L -34.64,20 L -34.64,-20 Z"
                  fill="#7FDBFF" stroke="#0074D9" stroke-width="2"/>
            <path d="M 0,-40 L 34.64,-20 L 0,0 L -34.64,-20 Z"
                  fill="#0074D9" stroke="#001f3f" stroke-width="1"/>
            <path d="M 0,0 L 34.64,-20 L 34.64,20 L 0,40 Z"
                  fill="#001f3f" stroke="#001f3f" stroke-width="1"/>
            <path d="M 0,0 L -34.64,-20 L -34.64,20 L 0,40 Z"
                  fill="#39CCCC" stroke="#001f3f" stroke-width="1"/>
          </g>
        </svg>
        """
        svg_bytes = QByteArray(svg_data.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        pixmap = QPixmap(256, 256)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def createToolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = ModernButton("New File")
        open_btn = ModernButton("Open")
        save_btn = ModernButton("Save")
        format_btn = ModernButton("Format SVG")
        font_btn = ModernButton("Change Font")
        theme_btn = ModernButton("Toggle Theme")

        new_btn.clicked.connect(self.new_file)
        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_file)
        format_btn.clicked.connect(self.format_code)
        font_btn.clicked.connect(self.change_font)
        theme_btn.clicked.connect(self.toggle_theme)

        toolbar.addWidget(new_btn)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addSeparator()
        toolbar.addWidget(format_btn)
        toolbar.addWidget(font_btn)
        toolbar.addSeparator()
        toolbar.addWidget(theme_btn)

    def toggle_theme(self):
        self.current_theme = Theme.LIGHT if self.current_theme == Theme.DARK else Theme.DARK
        self.apply_theme()

    def apply_theme(self):
        theme_colors = THEMES[self.current_theme]
        app = QApplication.instance()
        app.setPalette(get_palette(self.current_theme))
        app.setStyleSheet(get_stylesheet(self.current_theme))
        
        self.highlighter.update_theme(theme_colors)
        self.chat_widget.update_theme(theme_colors)
        self.preview_frame.set_background_color(theme_colors["PreviewBackground"])


    def update_editor_with_svg(self, svg_code):
        try:
            ET.fromstring(svg_code)
            formatted_xml = minidom.parseString(svg_code).toprettyxml(indent="    ")
            formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())
            self.code_editor.setPlainText(formatted_xml)
            self.statusBar.showMessage("SVG code updated from AI", 3000)
        except ET.ParseError as e:
            self.code_editor.setPlainText(svg_code)
            self.statusBar.showMessage(f"Invalid SVG from AI, inserted raw code: {str(e)}", 5000)

    def update_svg(self):
        try:
            svg_code = self.code_editor.toPlainText()
            if not svg_code.strip():
                self.preview_frame.svg_widget.load(QByteArray())
                return
            svg_bytes = QByteArray(svg_code.encode('utf-8'))
            self.preview_frame.svg_widget.load(svg_bytes)
            if not self.preview_frame.svg_widget.renderer().isValid():
                self.statusBar.showMessage("Invalid SVG syntax", 4000)
            else:
                self.statusBar.showMessage("SVG updated successfully", 3000)
        except Exception as e:
            self.statusBar.showMessage(f"Error rendering SVG: {str(e)}", 5000)

    def load_default_svg(self):
        default_svg = '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:1" />
            <stop offset="100%" style="stop-opacity:1;stop-color:#9B51E0" />
        </linearGradient>
    </defs>
    
    <rect x="0" y="0" width="200" height="200" fill="none" />
          
    <circle cx="100" cy="100" r="80" fill="url(#gradient)" opacity="0.9" />
            
    <circle cx="100" cy="100" r="60" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.6" />
            
    <polygon points="100,60 120,100 100,140 80,100" fill="#FFFFFF" opacity="0.8" />
</svg>'''
        self.code_editor.setPlainText(default_svg)

    def new_file(self):
        reply = QMessageBox.question(self, 'New File',
            "Create new file? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.code_editor.clear()
            self.load_default_svg()

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open SVG file', '', 
            'SVG files (*.svg);;All files (*)')

        if fname:
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.code_editor.setPlainText(f.read())
                self.statusBar.showMessage(f"Opened {fname}", 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not open file: {str(e)}')

    def save_file(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Save SVG file', '', 
            'SVG files (*.svg);;All files (*)')

        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                self.statusBar.showMessage(f"Saved to {fname}", 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not save file: {str(e)}')

    def format_code(self):
        try:
            xml_str = self.code_editor.toPlainText()
            if not xml_str.strip():
                self.statusBar.showMessage("Nothing to format.", 3000)
                return
            root = ET.fromstring(xml_str)
            formatted_xml = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
            formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())[formatted_xml.find('?>')+2:].strip()
            self.code_editor.setPlainText(formatted_xml)
            self.statusBar.showMessage("Code formatted successfully", 3000)
        except Exception as e:
            QMessageBox.warning(self, 'Format Error', f'Could not format XML: {str(e)}')

    def change_font(self):
        font, ok = QFontDialog.getFont(self.code_editor.font(), self)
        if ok:
            self.code_editor.setFont(font)

def main():
    app = QApplication(sys.argv)
    window = SVGEditor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application shutting down.")
