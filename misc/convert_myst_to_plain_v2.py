#!/usr/bin/env python3
"""
Convert Jupyter Book MyST markdown to plain markdown suitable for standalone notebooks.
Removes MyST directives and features while preserving content.
Version 2: Better handling of equation references
"""

import re
import sys

def remove_raw_directive(content):
    """Remove {raw} jupyter directives and their content."""
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

def extract_equation_labels(content):
    """Extract equation labels and map them to descriptive names."""
    label_map = {}

    # Find all labeled math blocks
    pattern = r'```\{math\}\n:label: ([a-zA-Z0-9_]+)\n\n(.*?)\n```'
    matches = re.finditer(pattern, content, flags=re.DOTALL)

    for match in matches:
        label = match.group(1)
        equation = match.group(2).strip()

        # Create a short description based on the label or content
        if 'obj_model' in label or 'objective' in label:
            label_map[label] = 'the objective function'
        elif 'odu_pv' in label:
            label_map[label] = 'the Bellman equation'
        elif 'reswage' in label:
            label_map[label] = 'the reservation wage equation'
        elif label.startswith('j1'):
            label_map[label] = 'equation (j1)'
        elif label.startswith('j2'):
            label_map[label] = 'equation (j2)'
        elif label.startswith('j3'):
            label_map[label] = 'equation (j3)'
        elif 'bell1_mccall' in label:
            label_map[label] = "the Bellman equation for v_e"
        elif 'bell2_mccall' in label:
            label_map[label] = "the Bellman equation for v_u"
        elif 'bell01_mccall' in label:
            label_map[label] = "the equation for v_e"
        elif 'bell02_mccall' in label:
            label_map[label] = "the equation for h"
        elif 'bell_scalar' in label:
            label_map[label] = "the scalar equation for h"
        elif 'bell_iter' in label:
            label_map[label] = "the iteration rule"
        elif 'bell_v_e_final' in label:
            label_map[label] = "the expression for v_e"
        elif 'bell' in label.lower():
            label_map[label] = 'the Bellman equation'
        elif 'defh' in label:
            label_map[label] = 'the definition of h'
        elif 'v_e_closed' in label:
            label_map[label] = 'the closed-form expression for v_e'
        else:
            # Default: just use "the equation above" or equation number
            label_map[label] = 'the equation above'

    return label_map

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

def remove_cross_references(content, label_map):
    """Remove cross-references like {doc}, {eq}, {ref}, {cite}."""
    # Remove {doc}`text <link>`
    content = re.sub(r'\{doc\}`([^<]*?)<[^>]*?>`', r'\1', content)
    content = re.sub(r'\{doc\}`([^`]*?)`', r'\1', content)

    # Handle "equations {eq}`label1` and {eq}`label2`" pattern specially
    def replace_equations_and(match):
        return 'these two equations'

    content = re.sub(r'equations \{eq\}`[^`]*?` and \{eq\}`[^`]*?`', replace_equations_and, content)

    # Handle "Equation {eq}`label`" pattern specially
    def replace_equation_ref(match):
        label = match.group(1)
        if label in label_map:
            desc = label_map[label]
            # If description is "equation (X)", capitalize it
            if desc.startswith('equation ('):
                return desc.replace('equation', 'Equation')
            # Otherwise just return the description
            return desc.capitalize() if desc[0].islower() else desc
        return 'The equation above'

    content = re.sub(r'Equation \{eq\}`([^`]*?)`', replace_equation_ref, content)

    # Replace {eq}`label` with appropriate description
    def replace_eq(match):
        label = match.group(1)
        if label in label_map:
            return label_map[label]
        return 'the equation above'

    content = re.sub(r'\{eq\}`([^`]*?)`', replace_eq, content)

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
    # First extract equation labels before removing them
    label_map = extract_equation_labels(content)

    content = remove_raw_directive(content)
    content = remove_contents_directive(content)
    content = remove_epigraph_directive(content)
    content = convert_code_cells(content)
    content = remove_index_directive(content)
    content = convert_math_directive(content)
    content = remove_note_directive(content)
    content = remove_exercise_directives(content)
    content = remove_figure_directive(content)
    content = remove_cross_references(content, label_map)
    content = remove_labels(content)
    content = clean_jupytext_header(content)
    return content

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_myst_to_plain_v2.py input.md output.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        content = f.read()

    converted = convert_myst_to_plain(content)

    with open(output_file, 'w') as f:
        f.write(converted)

    print(f"Converted {input_file} -> {output_file}")
