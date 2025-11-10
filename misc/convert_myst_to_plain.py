#!/usr/bin/env python3
"""
Convert Jupyter Book MyST markdown to plain markdown suitable for standalone notebooks.
Removes MyST directives and features while preserving content.
"""

import re
import sys

def remove_raw_directive(content):
    """Remove {raw} jupyter directives and their content."""
    # Remove the entire raw block
    content = re.sub(r'```\{raw\} jupyter\n.*?```\n', '', content, flags=re.DOTALL)
    return content

def remove_contents_directive(content):
    """Remove {contents} directives."""
    content = re.sub(r'```\{contents\}.*?\n:depth:.*?\n```\n', '', content, flags=re.DOTALL)
    return content

def remove_epigraph_directive(content):
    """Convert {epigraph} to plain blockquote."""
    def replace_epigraph(match):
        quote_content = match.group(1).strip()
        return f'> {quote_content}\n'
    content = re.sub(r'```\{epigraph\}\n(.*?)\n```', replace_epigraph, content, flags=re.DOTALL)
    return content

def convert_code_cells(content):
    """Convert {code-cell} ipython3 directives to plain code blocks."""
    # Remove tags line if present
    content = re.sub(r':tags:.*?\n', '', content)
    # Convert code-cell to plain code block
    content = re.sub(r'```\{code-cell\} ipython3\n', '```python\n', content)
    return content

def remove_index_directive(content):
    """Remove {index} directives."""
    content = re.sub(r'```\{index\}.*?\n```\n', '', content, flags=re.DOTALL)
    return content

def convert_math_directive(content):
    """Convert {math} directive with labels to plain math blocks."""
    def replace_math(match):
        label = match.group(1)
        math_content = match.group(2).strip()
        # Keep the math but remove the label
        return f'$$\n{math_content}\n$$\n'
    content = re.sub(r'```\{math\}\n:label: (.*?)\n\n(.*?)\n```', replace_math, content, flags=re.DOTALL)
    return content

def remove_note_directive(content):
    """Convert {note} directive to plain markdown with emphasis."""
    def replace_note(match):
        note_content = match.group(1).strip()
        return f'**Note:** {note_content}\n'
    content = re.sub(r'```\{note\}\n(.*?)\n```', replace_note, content, flags=re.DOTALL)
    return content

def remove_exercise_directives(content):
    """Remove exercise/solution directives but keep content."""
    # Remove exercise-start with label
    content = re.sub(r'```\{exercise-start\}\n:label:.*?\n```\n', '## Exercise\n', content)
    # Remove exercise-end
    content = re.sub(r'```\{exercise-end\}\n```\n', '', content)
    # Remove exercise with label (single block)
    content = re.sub(r'```\{exercise\}\n:label:.*?\n', '## Exercise\n\n', content)
    # Remove solution-start with class
    content = re.sub(r'```\{solution-start\}.*?\n:class:.*?\n```\n', '## Solution\n', content)
    # Remove solution-end
    content = re.sub(r'```\{solution-end\}\n```\n', '', content)
    return content

def remove_figure_directive(content):
    """Remove {figure} directive (we can't show figures without files)."""
    content = re.sub(r'```\{figure\}.*?\n```\n', '', content, flags=re.DOTALL)
    return content

def remove_cross_references(content):
    """Remove cross-references like {doc}, {eq}, {ref}, {cite}."""
    # Remove {doc}`text <link>`
    content = re.sub(r'\{doc\}`([^<]*?)<[^>]*?>`', r'\1', content)
    content = re.sub(r'\{doc\}`([^`]*?)`', r'\1', content)
    # Remove {eq}`label`
    content = re.sub(r'\{eq\}`([^`]*?)`', r'the equation above', content)
    # Remove {ref}`label`
    content = re.sub(r'\{ref\}`([^`]*?)`', r'', content)
    # Remove {cite}`reference`
    content = re.sub(r'\{cite\}`([^`]*?)`', r'', content)
    return content

def remove_labels(content):
    """Remove standalone labels like (mccall)=."""
    content = re.sub(r'\([a-zA-Z_][a-zA-Z0-9_]*\)=\n', '', content)
    return content

def clean_jupytext_header(content):
    """Simplify jupytext header to remove myst format."""
    # Replace myst format with markdown format
    content = re.sub(
        r'format_name: myst\n    format_version: [^\n]*\n',
        'format_name: markdown\n',
        content
    )
    return content

def convert_myst_to_plain(content):
    """Apply all conversions."""
    content = remove_raw_directive(content)
    content = remove_contents_directive(content)
    content = remove_epigraph_directive(content)
    content = convert_code_cells(content)
    content = remove_index_directive(content)
    content = convert_math_directive(content)
    content = remove_note_directive(content)
    content = remove_exercise_directives(content)
    content = remove_figure_directive(content)
    content = remove_cross_references(content)
    content = remove_labels(content)
    content = clean_jupytext_header(content)
    return content

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_myst_to_plain.py input.md output.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        content = f.read()

    converted = convert_myst_to_plain(content)

    with open(output_file, 'w') as f:
        f.write(converted)

    print(f"Converted {input_file} -> {output_file}")
