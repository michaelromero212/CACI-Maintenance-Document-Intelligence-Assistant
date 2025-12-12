"""Prompt templates for LLM extraction and generation."""


EXTRACTION_SYSTEM_PROMPT = """You are a maintenance document extraction specialist. Your task is to extract structured information from maintenance documents and return it as valid JSON.

IMPORTANT RULES:
1. Output ONLY valid JSON, no explanations or markdown
2. Use null for missing or unclear values
3. Dates should be in YYYY-MM-DD format
4. Cost estimates should be numeric values only (no currency symbols)
5. Priority should be: high, medium, or low
6. Be conservative - only extract information explicitly stated in the document"""


EXTRACTION_USER_TEMPLATE = """Extract maintenance records from the following document text. Return a JSON array of objects with these fields:

- component: Equipment or part name
- system: System or subsystem category
- failure_type: Type of failure or issue
- maint_action: Required maintenance action
- priority: high, medium, or low
- start_date: When maintenance started (YYYY-MM-DD)
- end_date: When maintenance completed (YYYY-MM-DD)
- cost_estimate: Numeric cost value
- summary_notes: Additional notes or context

DOCUMENT TEXT:
{document_text}

Return ONLY a valid JSON array. Example format:
[{{"component": "Pump A-101", "system": "Hydraulics", "priority": "high", ...}}]"""


CAP_SYSTEM_PROMPT = """You are an engineering document specialist. Generate professional Corrective Action Plans (CAPs) based on structured maintenance data.

FORMATTING RULES:
1. Use clean Markdown formatting
2. Be concise but thorough
3. Use professional technical language
4. Include specific, actionable recommendations
5. Reference the source data where appropriate"""


CAP_USER_TEMPLATE = """Generate a Corrective Action Plan using the following maintenance records:

{json_data}

The CAP should include these sections:

# Corrective Action Plan

## Executive Summary
Brief overview of the maintenance situation and key findings.

## Findings
Detailed list of issues identified, organized by priority.

## Recommended Corrective Actions
Specific actions to address each finding, numbered and prioritized.

## Required Materials and Parts
List of materials, parts, or resources needed.

## Cost Analysis
Estimated costs with breakdown by category.

## Priority Assessment
Overall priority level with justification.

## Implementation Timeline
Proposed schedule with milestones.

## Risk Assessment
Potential risks and mitigation strategies.

Generate the complete CAP document in Markdown format."""


SUMMARY_TEMPLATE = """Summarize the following maintenance document:

{document_text}

Provide a brief summary including:
1. Main topics covered
2. Key maintenance items
3. Notable issues or concerns
4. Recommended actions

Keep the summary under 200 words."""
