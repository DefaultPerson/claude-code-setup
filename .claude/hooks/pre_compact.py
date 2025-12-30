#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Pre-compact hook: converts conversation transcript to standalone HTML viewer.
Features: markdown rendering, syntax highlighting, copy buttons per message.
Triggered on both manual (/compact) and auto-compact events.
"""

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path(__file__).parent.parent / "backups"

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Session {session_id} | {date}</title>
<style>
:root {{
  --user-bg: #e3f2fd;
  --user-border: #1976d2;
  --assistant-bg: #f5f5f5;
  --assistant-border: #616161;
  --code-bg: #1e1e1e;
  --code-text: #d4d4d4;
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: #fafafa;
  line-height: 1.6;
}}
.header {{
  background: #fff;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}
.header h1 {{ margin: 0 0 10px; font-size: 1.4em; }}
.meta {{ color: #666; font-size: 0.9em; }}
.message {{
  background: #fff;
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 15px;
  border-left: 4px solid;
  position: relative;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.message.user {{
  background: var(--user-bg);
  border-left-color: var(--user-border);
}}
.message.assistant {{
  background: var(--assistant-bg);
  border-left-color: var(--assistant-border);
}}
.role {{
  font-weight: 600;
  font-size: 0.85em;
  text-transform: uppercase;
  margin-bottom: 10px;
  color: #555;
}}
.copy-btn {{
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.8em;
  opacity: 0.7;
  transition: opacity 0.2s;
}}
.copy-btn:hover {{ opacity: 1; background: #f0f0f0; }}
.copy-btn.copied {{ background: #4caf50; color: #fff; border-color: #4caf50; }}
.content {{ word-wrap: break-word; }}
.content h1, .content h2, .content h3 {{ margin: 0.8em 0 0.4em; }}
.content h1 {{ font-size: 1.4em; }}
.content h2 {{ font-size: 1.2em; }}
.content h3 {{ font-size: 1.1em; }}
.content p {{ margin: 0.5em 0; }}
.content ul, .content ol {{ margin: 0.5em 0; padding-left: 1.5em; }}
.content code {{
  background: #e8e8e8;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 0.9em;
}}
.content pre {{
  background: var(--code-bg);
  color: var(--code-text);
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.8em 0;
}}
.content pre code {{
  background: none;
  padding: 0;
  color: inherit;
}}
.content blockquote {{
  border-left: 3px solid #ddd;
  margin: 0.5em 0;
  padding-left: 15px;
  color: #666;
}}
.content a {{ color: #1976d2; }}
.content table {{
  border-collapse: collapse;
  margin: 0.8em 0;
  width: 100%;
}}
.content th, .content td {{
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}}
.content th {{ background: #f5f5f5; }}
/* Syntax highlighting */
.kw {{ color: #569cd6; }}
.str {{ color: #ce9178; }}
.num {{ color: #b5cea8; }}
.cmt {{ color: #6a9955; }}
.fn {{ color: #dcdcaa; }}
</style>
</head>
<body>
<div class="header">
  <h1>Session Backup</h1>
  <div class="meta">
    <strong>Session:</strong> {session_id}<br>
    <strong>Date:</strong> {date}<br>
    <strong>Trigger:</strong> {trigger}<br>
    <strong>Messages:</strong> {message_count}
  </div>
</div>
<div class="messages">
{messages_html}
</div>
<script>
function copyMessage(btn, id) {{
  const el = document.getElementById(id);
  const text = el.getAttribute('data-raw');
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{
      btn.textContent = 'Copy';
      btn.classList.remove('copied');
    }}, 1500);
  }});
}}
</script>
</body>
</html>'''

MESSAGE_TEMPLATE = '''<div class="message {role}" id="msg-{idx}">
  <button class="copy-btn" onclick="copyMessage(this, 'msg-{idx}')">Copy</button>
  <div class="role">{role_display}</div>
  <div class="content" data-raw="{raw_escaped}">{content_html}</div>
</div>'''


def parse_markdown(text: str) -> str:
    """Simple markdown to HTML converter."""
    lines = text.split('\n')
    result = []
    in_code_block = False
    code_lang = ''
    code_lines = []
    in_list = False
    list_type = None

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            result.append(f'</{list_type}>')
            in_list = False
            list_type = None

    def highlight_code(code: str, lang: str) -> str:
        """Basic syntax highlighting."""
        code = html.escape(code)
        # Keywords
        keywords = r'\b(def|class|import|from|return|if|else|elif|for|while|try|except|finally|with|as|lambda|yield|async|await|True|False|None|and|or|not|in|is|function|const|let|var|export|default|interface|type|enum|public|private|static|void|int|str|bool|float|dict|list|tuple|set)\b'
        code = re.sub(keywords, r'<span class="kw">\1</span>', code)
        # Strings
        code = re.sub(r'(\"[^\"]*\"|\'[^\']*\'|`[^`]*`)', r'<span class="str">\1</span>', code)
        # Numbers
        code = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="num">\1</span>', code)
        # Comments
        code = re.sub(r'(#.*|//.*)', r'<span class="cmt">\1</span>', code)
        return code

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                code_content = '\n'.join(code_lines)
                highlighted = highlight_code(code_content, code_lang)
                result.append(f'<pre><code>{highlighted}</code></pre>')
                code_lines = []
                in_code_block = False
            else:
                close_list()
                code_lang = line[3:].strip()
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Headers
        if line.startswith('### '):
            close_list()
            result.append(f'<h3>{html.escape(line[4:])}</h3>')
            continue
        if line.startswith('## '):
            close_list()
            result.append(f'<h2>{html.escape(line[3:])}</h2>')
            continue
        if line.startswith('# '):
            close_list()
            result.append(f'<h1>{html.escape(line[2:])}</h1>')
            continue

        # Blockquote
        if line.startswith('> '):
            close_list()
            result.append(f'<blockquote>{html.escape(line[2:])}</blockquote>')
            continue

        # Lists
        ul_match = re.match(r'^[-*] (.+)$', line)
        ol_match = re.match(r'^\d+\. (.+)$', line)

        if ul_match:
            if not in_list or list_type != 'ul':
                close_list()
                result.append('<ul>')
                in_list = True
                list_type = 'ul'
            result.append(f'<li>{format_inline(ul_match.group(1))}</li>')
            continue

        if ol_match:
            if not in_list or list_type != 'ol':
                close_list()
                result.append('<ol>')
                in_list = True
                list_type = 'ol'
            result.append(f'<li>{format_inline(ol_match.group(1))}</li>')
            continue

        # Empty line
        if not line.strip():
            close_list()
            continue

        # Paragraph
        close_list()
        result.append(f'<p>{format_inline(line)}</p>')

    close_list()
    if in_code_block:
        code_content = '\n'.join(code_lines)
        result.append(f'<pre><code>{html.escape(code_content)}</code></pre>')

    return '\n'.join(result)


def format_inline(text: str) -> str:
    """Format inline markdown: bold, italic, code, links."""
    text = html.escape(text)
    # Code (backticks)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def extract_messages(transcript_path: str) -> list[dict]:
    """Extract user and assistant messages from JSONL transcript."""
    messages = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    msg_type = entry.get('type', '')
                    if msg_type in ('user', 'assistant'):
                        message = entry.get('message', {})
                        content = message.get('content', [])
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_parts.append(item.get('text', ''))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        if text_parts:
                            messages.append({
                                'role': msg_type,
                                'content': '\n'.join(text_parts)
                            })
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return messages


def generate_html(messages: list[dict], session_id: str, trigger: str) -> str:
    """Generate standalone HTML from messages."""
    messages_html = []
    for idx, msg in enumerate(messages):
        role = msg['role']
        content = msg['content']
        content_html = parse_markdown(content)
        raw_escaped = html.escape(content).replace('"', '&quot;')

        messages_html.append(MESSAGE_TEMPLATE.format(
            role=role,
            role_display='User' if role == 'user' else 'Assistant',
            idx=idx,
            content_html=content_html,
            raw_escaped=raw_escaped
        ))

    return HTML_TEMPLATE.format(
        session_id=session_id[:8] if session_id else 'unknown',
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        trigger=trigger,
        message_count=len(messages),
        messages_html='\n'.join(messages_html)
    )


def backup_transcript(transcript_path: str, session_id: str, trigger: str) -> str | None:
    """Create HTML backup of the transcript."""
    try:
        messages = extract_messages(transcript_path)
        if not messages:
            return None

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_session = session_id[:8] if session_id else "unknown"
        backup_name = f"{timestamp}_{trigger}_{short_session}.html"
        dest = BACKUP_DIR / backup_name

        html_content = generate_html(messages, session_id, trigger)
        dest.write_text(html_content, encoding='utf-8')

        return str(dest)
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        session_id = input_data.get("session_id", "")
        transcript_path = input_data.get("transcript_path", "")
        trigger = input_data.get("trigger", "unknown")

        if transcript_path:
            backup_path = backup_transcript(transcript_path, session_id, trigger)
            if backup_path:
                print(f"Session saved: {backup_path}")

        sys.exit(0)
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
