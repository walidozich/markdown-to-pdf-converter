# md_to_pdf — Markdown to PDF Converter

A lightweight Python script that converts Markdown files into clean, styled PDFs using `reportlab`. No browser, no Pandoc, no LaTeX required.

---

## Features

- **Headings** (H1–H3) with distinct font sizes and colors
- **Bold**, *italic*, and ***bold italic*** inline formatting
- `Inline code` and fenced code blocks with monospace styling
- Ordered and unordered lists
- Blockquotes
- Horizontal rules
- Hyperlinks (clickable in PDF)
- Clean typography with 1-inch margins on US Letter paper

---

## Requirements

- Python 3.7+
- `reportlab`
- `markdown`

Install dependencies:

```bash
pip install reportlab markdown
```

---

## Usage

```bash
# Output defaults to same filename with .pdf extension
python md_to_pdf.py input.md

# Specify a custom output path
python md_to_pdf.py input.md output.pdf
```

### Examples

```bash
python md_to_pdf.py README.md
# → README.pdf

python md_to_pdf.py docs/notes.md exports/notes.pdf
# → exports/notes.pdf
```

---

## Supported Markdown Syntax

| Element            | Syntax Example                        |
|--------------------|---------------------------------------|
| Heading 1          | `# Title`                             |
| Heading 2          | `## Section`                          |
| Heading 3          | `### Subsection`                      |
| Bold               | `**bold**` or `__bold__`              |
| Italic             | `*italic*` or `_italic_`              |
| Bold + Italic      | `***bold italic***`                   |
| Inline code        | `` `code` ``                          |
| Fenced code block  | ` ``` ... ``` `                       |
| Unordered list     | `- item` or `* item` or `+ item`      |
| Ordered list       | `1. item`                             |
| Blockquote         | `> quote`                             |
| Horizontal rule    | `---` or `***`                        |
| Link               | `[text](https://example.com)`         |

---

## Limitations

- Nested lists are not currently supported
- Images (`![alt](url)`) are not rendered
- HTML embedded in Markdown is ignored
- Tables are not supported yet

---

## Project Structure

```
md_to_pdf.py    # Main converter script
README.md       # This file
test.md         # Sample Markdown file for testing
```

---

## License

MIT — free to use and modify.
