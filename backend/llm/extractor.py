"""LLM-based structured field extraction."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from llm.client import LLMClient
from llm.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE


class LLMExtractor:
    """
    Extract structured maintenance data using LLM.
    
    Falls back to regex-based extraction if LLM is unavailable.
    """
    
    def __init__(self):
        self.client = LLMClient()
    
    async def extract_records(
        self, 
        text: str,
        use_llm: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract maintenance records from document text.
        
        Args:
            text: Raw document text
            use_llm: Whether to attempt LLM extraction
            
        Returns:
            List of extracted record dictionaries
        """
        if use_llm:
            records = await self._llm_extract(text)
            if records:
                return self._validate_records(records)
        
        # Fallback to regex extraction
        return self._regex_extract(text)
    
    async def _llm_extract(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """Extract using LLM."""
        # Truncate text if too long
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated]"
        
        prompt = EXTRACTION_USER_TEMPLATE.format(document_text=text)
        
        return await self.client.extract_json(
            prompt=prompt,
            system_prompt=EXTRACTION_SYSTEM_PROMPT
        )
    
    def _regex_extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback regex-based extraction for common patterns.
        """
        records = []
        
        # Pattern for maintenance entries
        patterns = {
            'component': [
                r'(?:component|equipment|part|item)[\s:]+([A-Za-z0-9\-_\s]+)',
                r'([A-Z][A-Za-z0-9\-]+(?:-\d+)?)\s+(?:maintenance|repair|service)',
            ],
            'priority': [
                r'(?:priority|urgency)[\s:]+(\w+)',
                r'\b(high|medium|low|critical|urgent)\s+priority',
            ],
            'cost': [
                r'\$[\d,]+(?:\.\d{2})?',
                r'(?:cost|estimate)[\s:]+\$?([\d,]+(?:\.\d{2})?)',
            ],
            'date': [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
            ]
        }
        
        # Extract components
        components = []
        for pattern in patterns['component']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            components.extend(matches)
        
        # Find maintenance action blocks
        action_patterns = [
            r'(?:action|repair|maintenance)[\s:]+(.+?)(?:\n|$)',
            r'(?:work order|wo)[\s#:]+\d+[\s:]+(.+?)(?:\n|$)',
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend(matches)
        
        # Build records from extracted data
        if components or actions:
            # Create one record per component or action (whichever is more)
            count = max(len(components), len(actions), 1)
            
            for i in range(min(count, 10)):  # Limit to 10 records
                record = {
                    'component': components[i] if i < len(components) else None,
                    'maint_action': actions[i] if i < len(actions) else None,
                    'priority': None,
                    'system': None,
                    'failure_type': None,
                    'start_date': None,
                    'end_date': None,
                    'cost_estimate': None,
                    'summary_notes': None
                }
                
                # Try to find associated priority
                for pattern in patterns['priority']:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        record['priority'] = match.group(1).lower()
                        break
                
                # Try to find cost
                for pattern in patterns['cost']:
                    match = re.search(pattern, text)
                    if match:
                        cost_str = match.group(0).replace('$', '').replace(',', '')
                        try:
                            record['cost_estimate'] = float(cost_str)
                        except ValueError:
                            pass
                        break
                
                records.append(record)
        
        return records
    
    def _validate_records(
        self, 
        records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and clean extracted records."""
        validated = []
        
        for record in records:
            # Ensure all expected fields exist
            clean_record = {
                'component': self._clean_string(record.get('component')),
                'system': self._clean_string(record.get('system')),
                'failure_type': self._clean_string(record.get('failure_type')),
                'maint_action': self._clean_string(record.get('maint_action')),
                'priority': self._normalize_priority(record.get('priority')),
                'start_date': self._parse_date(record.get('start_date')),
                'end_date': self._parse_date(record.get('end_date')),
                'cost_estimate': self._parse_number(record.get('cost_estimate')),
                'summary_notes': self._clean_string(record.get('summary_notes'))
            }
            
            # Only include if has at least component or action
            if clean_record['component'] or clean_record['maint_action']:
                validated.append(clean_record)
        
        return validated
    
    def _clean_string(self, value: Any) -> Optional[str]:
        """Clean string value."""
        if value is None:
            return None
        s = str(value).strip()
        return s if s and s.lower() != 'null' else None
    
    def _normalize_priority(self, value: Any) -> Optional[str]:
        """Normalize priority to standard values."""
        if not value:
            return None
        
        v = str(value).lower().strip()
        
        if v in ['high', 'critical', 'urgent', '1', 'p1']:
            return 'high'
        elif v in ['medium', 'moderate', 'normal', '2', 'p2']:
            return 'medium'
        elif v in ['low', 'minor', 'routine', '3', 'p3']:
            return 'low'
        
        return v if v != 'null' else None
    
    def _parse_date(self, value: Any) -> Optional[str]:
        """Parse and format date."""
        if not value:
            return None
        
        s = str(value).strip()
        if s.lower() == 'null':
            return None
        
        # Already in correct format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
            return s
        
        # Try common formats
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y']
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _parse_number(self, value: Any) -> Optional[float]:
        """Parse numeric value."""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        try:
            s = str(value).replace('$', '').replace(',', '').strip()
            if s.lower() == 'null':
                return None
            return float(s)
        except ValueError:
            return None
