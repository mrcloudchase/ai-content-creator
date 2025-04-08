# Define content types based on the Diátaxis framework
CONTENT_TYPES = {
    "tutorial": {
        "name": "Tutorial",
        "description": "Step-by-step guides for learning by doing",
        "purpose": "To teach users how to accomplish a specific task through hands-on learning with concrete examples",
        "markdown_template": """
# [Title of the Tutorial]

## Introduction
Brief introduction to what the tutorial will cover and why it's important.

## Prerequisites
- What users need to know before starting
- Required tools or software
- Any setup needed

## Step 1: [First Step Title]
Detailed explanation of the first step with code examples or screenshots.

## Step 2: [Second Step Title]
Detailed explanation of the second step with code examples or screenshots.

## Step 3: [Third Step Title]
Detailed explanation of the third step with code examples or screenshots.

## Troubleshooting
Common issues and how to resolve them.

## Next Steps
What to learn next or how to expand on this knowledge.

## Summary
Recap of what was learned in this tutorial.
"""
    },
    "how-to": {
        "name": "How-To Guide",
        "description": "Problem-oriented instructions for accomplished users",
        "purpose": "To provide practical, task-oriented instructions for users who already understand the basics and need to solve a specific problem",
        "markdown_template": """
# How to [Task Name]

## Overview
Brief overview of what this guide will help you accomplish.

## Requirements
- List of requirements or prerequisites
- Any specific versions or configurations needed

## Steps to [Task Name]

### 1. [First Step]
Clear, concise instructions for the first step.

### 2. [Second Step]
Clear, concise instructions for the second step.

### 3. [Third Step]
Clear, concise instructions for the third step.

## Verification
How to verify that the task was completed successfully.

## Troubleshooting
Common issues and their solutions.

## Related Resources
Links to related documentation or resources.
"""
    },
    "explanation": {
        "name": "Explanation",
        "description": "Understanding-oriented background knowledge",
        "purpose": "To provide conceptual understanding and background knowledge about a topic, helping users understand the 'why' behind concepts",
        "markdown_template": """
# Understanding [Topic Name]

## Introduction
Overview of the topic and why understanding it is important.

## What is [Topic Name]?
Clear definition and explanation of the core concept.

## Why is [Topic Name] Important?
Explanation of the significance and relevance of the topic.

## Key Concepts
- **Concept 1**: Explanation of the first key concept
- **Concept 2**: Explanation of the second key concept
- **Concept 3**: Explanation of the third key concept

## How [Topic Name] Works
Detailed explanation of the underlying principles and mechanisms.

## Real-World Applications
Examples of how this concept is applied in practice.

## Common Misconceptions
Addressing common misunderstandings about the topic.

## Further Reading
Resources for deeper exploration of the topic.
"""
    },
    "reference": {
        "name": "Reference",
        "description": "Information-oriented technical details",
        "purpose": "To provide comprehensive, factual information about a topic in a structured format for quick lookup and verification",
        "markdown_template": """
# [Topic Name] Reference

## Overview
Brief overview of what this reference covers.

## Syntax
```
[Code or syntax examples]
```

## Parameters
| Parameter | Type | Description | Required | Default |
|-----------|------|-------------|----------|---------|
| param1    | type | description | Yes/No   | value   |
| param2    | type | description | Yes/No   | value   |

## Return Values
Description of what the function or method returns.

## Examples
```[language]
// Example code
```

## Notes
Important notes or considerations.

## See Also
Links to related reference documentation.
"""
    }
} 