"""Corrective Action Plan generator."""

from datetime import datetime
from typing import List
from decimal import Decimal

from models.models import Document, ExtractedRecord
from llm.client import LLMClient
from llm.prompts import CAP_SYSTEM_PROMPT, CAP_USER_TEMPLATE


class CAPGenerator:
    """
    Generate Corrective Action Plans using LLM.
    
    Falls back to template-based generation if LLM is unavailable.
    """
    
    def __init__(self):
        self.client = LLMClient()
    
    async def generate(
        self, 
        document: Document, 
        records: List[ExtractedRecord]
    ) -> str:
        """
        Generate a Corrective Action Plan.
        
        Args:
            document: Source document
            records: Extracted maintenance records
            
        Returns:
            Markdown-formatted CAP document
        """
        # Prepare data for LLM
        records_data = self._prepare_records_data(records)
        
        # Try LLM generation
        try:
            prompt = CAP_USER_TEMPLATE.format(json_data=records_data)
            response = await self.client.generate(
                prompt=prompt,
                system_prompt=CAP_SYSTEM_PROMPT,
                max_tokens=4096,
                temperature=0.3
            )
            
            if response and len(response) > 100:
                return response
        except Exception:
            pass  # Fall through to template generation
        
        # Fallback to template generation
        return self._generate_template_cap(document, records)
    
    def _prepare_records_data(self, records: List[ExtractedRecord]) -> str:
        """Convert records to JSON-like string for LLM."""
        items = []
        
        for r in records:
            item = {
                'component': r.component,
                'system': r.system,
                'failure_type': r.failure_type,
                'maint_action': r.maint_action,
                'priority': r.priority,
                'status': r.status,
                'start_date': str(r.start_date) if r.start_date else None,
                'end_date': str(r.end_date) if r.end_date else None,
                'cost_estimate': float(r.cost_estimate) if r.cost_estimate else None,
                'notes': r.summary_notes
            }
            items.append(str(item))
        
        return '\n'.join(items)
    
    def _generate_template_cap(
        self, 
        document: Document, 
        records: List[ExtractedRecord]
    ) -> str:
        """Generate CAP using template (fallback)."""
        # Calculate statistics
        total_cost = sum(
            float(r.cost_estimate) for r in records 
            if r.cost_estimate
        )
        
        high_priority = [r for r in records if r.priority == 'high']
        medium_priority = [r for r in records if r.priority == 'medium']
        low_priority = [r for r in records if r.priority == 'low']
        
        # Build markdown document
        lines = [
            "# Corrective Action Plan",
            "",
            f"**Document:** {document.filename}",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Total Items:** {len(records)}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"This Corrective Action Plan addresses {len(records)} maintenance items "
            f"identified in the source document. The analysis identified "
            f"{len(high_priority)} high-priority items requiring immediate attention, "
            f"{len(medium_priority)} medium-priority items, and {len(low_priority)} "
            f"low-priority items for routine scheduling.",
            "",
        ]
        
        if total_cost > 0:
            lines.extend([
                f"**Estimated Total Cost:** ${total_cost:,.2f}",
                "",
            ])
        
        # Findings
        lines.extend([
            "## Findings",
            "",
        ])
        
        if high_priority:
            lines.append("### High Priority Items")
            lines.append("")
            for i, r in enumerate(high_priority, 1):
                lines.append(f"{i}. **{r.component or 'Unknown Component'}**")
                if r.maint_action:
                    lines.append(f"   - Action: {r.maint_action}")
                if r.failure_type:
                    lines.append(f"   - Issue: {r.failure_type}")
                lines.append("")
        
        if medium_priority:
            lines.append("### Medium Priority Items")
            lines.append("")
            for i, r in enumerate(medium_priority, 1):
                lines.append(f"{i}. **{r.component or 'Unknown Component'}**")
                if r.maint_action:
                    lines.append(f"   - Action: {r.maint_action}")
                lines.append("")
        
        if low_priority:
            lines.append("### Low Priority Items")
            lines.append("")
            for i, r in enumerate(low_priority, 1):
                lines.append(f"{i}. {r.component or 'Unknown Component'}")
            lines.append("")
        
        # Recommended Actions
        lines.extend([
            "## Recommended Corrective Actions",
            "",
        ])
        
        for i, r in enumerate(records, 1):
            if r.maint_action:
                lines.append(f"{i}. {r.maint_action}")
        lines.append("")
        
        # Cost Analysis
        lines.extend([
            "## Cost Analysis",
            "",
        ])
        
        if total_cost > 0:
            lines.append("| Priority | Count | Estimated Cost |")
            lines.append("|----------|-------|----------------|")
            
            if high_priority:
                high_cost = sum(float(r.cost_estimate) for r in high_priority if r.cost_estimate)
                lines.append(f"| High | {len(high_priority)} | ${high_cost:,.2f} |")
            if medium_priority:
                med_cost = sum(float(r.cost_estimate) for r in medium_priority if r.cost_estimate)
                lines.append(f"| Medium | {len(medium_priority)} | ${med_cost:,.2f} |")
            if low_priority:
                low_cost = sum(float(r.cost_estimate) for r in low_priority if r.cost_estimate)
                lines.append(f"| Low | {len(low_priority)} | ${low_cost:,.2f} |")
            
            lines.append(f"| **Total** | **{len(records)}** | **${total_cost:,.2f}** |")
        else:
            lines.append("Cost estimates not available from source document.")
        
        lines.append("")
        
        # Priority Assessment
        lines.extend([
            "## Priority Assessment",
            "",
        ])
        
        if high_priority:
            lines.append(
                f"**Overall Priority: HIGH** - {len(high_priority)} critical items "
                "require immediate attention."
            )
        elif medium_priority:
            lines.append(
                f"**Overall Priority: MEDIUM** - {len(medium_priority)} items "
                "should be scheduled within the next maintenance window."
            )
        else:
            lines.append(
                "**Overall Priority: LOW** - Items can be addressed during "
                "routine maintenance cycles."
            )
        lines.append("")
        
        # Timeline
        lines.extend([
            "## Implementation Timeline",
            "",
            "| Phase | Items | Target Duration |",
            "|-------|-------|-----------------|",
        ])
        
        if high_priority:
            lines.append(f"| Immediate | {len(high_priority)} | 1-2 weeks |")
        if medium_priority:
            lines.append(f"| Short-term | {len(medium_priority)} | 2-4 weeks |")
        if low_priority:
            lines.append(f"| Scheduled | {len(low_priority)} | Next quarter |")
        
        lines.append("")
        
        # Footer
        lines.extend([
            "---",
            "",
            "*This Corrective Action Plan was generated by MDIA. "
            "All recommendations should be reviewed by qualified engineering personnel "
            "before implementation.*",
        ])
        
        return '\n'.join(lines)
