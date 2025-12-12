"""Data normalization service."""

import re
from datetime import datetime, date
from typing import Any, Optional, Dict
from decimal import Decimal


class DataNormalizer:
    """Normalize extracted data to standard formats."""
    
    # Standard priority mappings
    PRIORITY_MAP = {
        '1': 'high', 'p1': 'high', 'critical': 'high', 'urgent': 'high',
        '2': 'medium', 'p2': 'medium', 'moderate': 'medium', 'normal': 'medium',
        '3': 'low', 'p3': 'low', 'minor': 'low', 'routine': 'low',
    }
    
    # Standard status mappings
    STATUS_MAP = {
        'new': 'open', 'pending': 'open', 'created': 'open',
        'started': 'in-progress', 'working': 'in-progress', 'active': 'in-progress',
        'waiting': 'awaiting-parts', 'hold': 'awaiting-parts', 'blocked': 'awaiting-parts',
        'done': 'complete', 'finished': 'complete', 'closed': 'complete',
    }
    
    def normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all fields in a record.
        
        Args:
            record: Raw record dictionary
            
        Returns:
            Normalized record dictionary
        """
        return {
            'component': self.normalize_string(record.get('component')),
            'system': self.normalize_string(record.get('system')),
            'failure_type': self.normalize_string(record.get('failure_type')),
            'maint_action': self.normalize_string(record.get('maint_action')),
            'priority': self.normalize_priority(record.get('priority')),
            'status': self.normalize_status(record.get('status', 'open')),
            'start_date': self.normalize_date(record.get('start_date')),
            'end_date': self.normalize_date(record.get('end_date')),
            'cost_estimate': self.normalize_cost(record.get('cost_estimate')),
            'summary_notes': self.normalize_string(record.get('summary_notes')),
        }
    
    def normalize_string(self, value: Any) -> Optional[str]:
        """Clean and normalize string value."""
        if value is None:
            return None
        
        s = str(value).strip()
        
        # Handle null-like values
        if s.lower() in ['null', 'none', 'n/a', 'na', '']:
            return None
        
        # Remove excessive whitespace
        s = ' '.join(s.split())
        
        return s if s else None
    
    def normalize_priority(self, value: Any) -> Optional[str]:
        """Normalize priority to standard values: high, medium, low."""
        if value is None:
            return None
        
        s = str(value).lower().strip()
        
        # Direct match
        if s in ['high', 'medium', 'low']:
            return s
        
        # Mapped match
        if s in self.PRIORITY_MAP:
            return self.PRIORITY_MAP[s]
        
        # Best guess based on keywords
        if any(k in s for k in ['high', 'critical', 'urgent', 'emergency']):
            return 'high'
        if any(k in s for k in ['medium', 'moderate', 'normal']):
            return 'medium'
        if any(k in s for k in ['low', 'minor', 'routine']):
            return 'low'
        
        return None
    
    def normalize_status(self, value: Any) -> str:
        """Normalize status to standard values."""
        if value is None:
            return 'open'
        
        s = str(value).lower().strip()
        
        # Direct match
        if s in ['open', 'in-progress', 'awaiting-parts', 'complete']:
            return s
        
        # Mapped match
        if s in self.STATUS_MAP:
            return self.STATUS_MAP[s]
        
        return 'open'
    
    def normalize_date(self, value: Any) -> Optional[date]:
        """Normalize date to date object."""
        if value is None:
            return None
        
        # Already a date
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        s = str(value).strip()
        
        if s.lower() in ['null', 'none', 'n/a', '']:
            return None
        
        # Try various date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y',
            '%Y%m%d',
            '%B %d, %Y',
            '%b %d, %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def normalize_cost(self, value: Any) -> Optional[Decimal]:
        """Normalize cost to Decimal."""
        if value is None:
            return None
        
        if isinstance(value, Decimal):
            return value
        
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        
        s = str(value).strip()
        
        if s.lower() in ['null', 'none', 'n/a', '']:
            return None
        
        # Remove currency symbols and formatting
        s = re.sub(r'[^\d.\-]', '', s)
        
        try:
            return Decimal(s)
        except:
            return None
    
    def normalize_component_name(self, value: str) -> str:
        """
        Normalize component names to standard format.
        
        Examples:
            "pump A-101" -> "Pump A-101"
            "VALVE_B2" -> "Valve B2"
        """
        if not value:
            return value
        
        # Replace underscores with spaces
        s = value.replace('_', ' ')
        
        # Title case, but preserve identifiers
        parts = s.split()
        normalized = []
        
        for part in parts:
            # If it looks like an identifier, preserve case
            if re.match(r'^[A-Z0-9\-]+$', part):
                normalized.append(part)
            else:
                normalized.append(part.capitalize())
        
        return ' '.join(normalized)
