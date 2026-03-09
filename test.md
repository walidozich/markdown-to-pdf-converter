# Markdown to PDF — Test File

This file tests every feature supported by `md_to_pdf.py`. Run it with:

```bash
python md_to_pdf.py test.md
```

---

## 1. Headings

# Heading 1
## Heading 2
### Heading 3

---

## 2. Inline Formatting

This is **bold text** using double asterisks.

This is __also bold__ using double underscores.

This is *italic text* using single asterisks.

This is _also italic_ using single underscores.

This is ***bold and italic*** all at once.

This is `inline code` inside a sentence.

---

## 3. Paragraphs

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.

---

## 4. Unordered Lists

- Apples
- Bananas
- Cherries

* Node.js
* Python
* Rust

+ First item
+ Second item
+ Third item

---

## 5. Ordered Lists

1. Install dependencies
2. Run the script
3. Open the output PDF
4. Celebrate

---

## 6. Blockquotes

> "The best way to predict the future is to invent it."
> — Alan Kay

> This is a longer blockquote that spans a bit more text to test how wrapping looks inside the styled blockquote box in the final PDF output.

---

## 7. Horizontal Rules

Three dashes:

---

Three asterisks:

***

---

## 8. Fenced Code Blocks

Python example:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

JavaScript example:

```javascript
const fetchData = async (url) => {
  const response = await fetch(url);
  const data = await response.json();
  return data;
};
```

Bash example:

```bash
#!/bin/bash
for file in *.md; do
  python md_to_pdf.py "$file"
  echo "Converted: $file"
done
```

SQL example:

```sql
SELECT users.name, COUNT(orders.id) AS total_orders
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE users.active = 1
GROUP BY users.name
ORDER BY total_orders DESC;
```

---

## 9. Links

Visit [OpenAI](https://openai.com) or [Anthropic](https://anthropic.com) for more on AI.

Check out the [ReportLab documentation](https://docs.reportlab.com) for PDF generation details.

---

## 10. Mixed Content

Here's a paragraph that uses **bold**, *italic*, `inline code`, and a [link](https://example.com) all in one sentence — this tests that inline rendering composes correctly.

Steps to run this project:

1. Clone the repo
2. Install dependencies with `pip install reportlab markdown`
3. Run `python md_to_pdf.py test.md`
4. Open **test.pdf** in your PDF viewer

> **Tip:** You can batch convert all `.md` files in a folder using the bash snippet from Section 8 above.

---

## 11. Edge Cases

Empty inline code: ``

Short bold: **x**

Short italic: *y*

A lone horizontal rule right below this line:

---

Paragraph immediately after a horizontal rule.

A paragraph ending with a link right at the end: [click here](https://example.com)
