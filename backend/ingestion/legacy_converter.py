"""Legacy Excel format converter for MSC-style maintenance logs."""

import pandas as pd
import re
import uuid
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from models.models import Document, ExtractedRecord, Anomaly
from models.schemas import LegacyConversionResult


class LegacyConverter:
    """
    Convert legacy MSC-style Excel files to normalized format.
    
    Handles unpredictable column labels by fuzzy matching to
    standard schema fields.
    """
    
    # Standard schema fields
    STANDARD_FIELDS = {
        'component': ['component', 'comp', 'part', 'item', 'equipment', 'asset'],
        'system': ['system', 'sys', 'subsystem', 'category', 'type'],
        'priority': ['priority', 'prio', 'urgency', 'level', 'importance'],
        'maint_action': ['action', 'maintenance', 'maint', 'work', 'repair', 'task', 'description'],
        'cost_estimate': ['cost', 'estimate', 'price', 'amount', 'budget', 'expense'],
        'start_date': ['start', 'begin', 'started', 'initiate', 'open_date'],
        'end_date': ['end', 'complete', 'finish', 'closed', 'due', 'target'],
        'notes': ['notes', 'remarks', 'comments', 'details', 'info', 'additional']
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def convert(
        self, 
        file_content: bytes, 
        filename: str
    ) -> LegacyConversionResult:
        """
        Convert a legacy Excel file to normalized records.
        
        Args:
            file_content: Excel file bytes
            filename: Original filename
            
        Returns:
            Conversion result with statistics
        """
        # Read Excel file
        df = pd.read_excel(BytesIO(file_content))
        
        # Map columns to standard schema
        column_mappings = self._map_columns(df.columns.tolist())
        
        # Create document record
        document = Document(
            filename=filename,
            file_type="legacy_excel",
            file_size=len(file_content),
            processing_status="converted",
            processed=True
        )
        self.db.add(document)
        self.db.flush()
        
        # Convert rows to records
        records_created = 0
        records_with_issues = 0
        
        for idx, row in df.iterrows():
            record_data = self._extract_record_data(row, column_mappings)
            issues = self._validate_record(record_data)
            
            record = ExtractedRecord(
                document_id=document.id,
                component=record_data.get('component'),
                system=record_data.get('system'),
                priority=self._normalize_priority(record_data.get('priority')),
                maint_action=record_data.get('maint_action'),
                cost_estimate=self._parse_cost(record_data.get('cost_estimate')),
                start_date=self._parse_date(record_data.get('start_date')),
                end_date=self._parse_date(record_data.get('end_date')),
                summary_notes=record_data.get('notes'),
                status='open',
                extraction_method='legacy_conversion',
                confidence_score=0.85 if not issues else 0.60
            )
            self.db.add(record)
            self.db.flush()
            
            records_created += 1
            
            # Create anomalies for issues
            if issues:
                records_with_issues += 1
                for issue in issues:
                    anomaly = Anomaly(
                        record_id=record.id,
                        document_id=document.id,
                        anomaly_type=issue['type'],
                        severity=issue['severity'],
                        description=issue['description'],
                        field_name=issue.get('field'),
                        suggested_fix=issue.get('fix')
                    )
                    self.db.add(anomaly)
        
        self.db.commit()
        
        return LegacyConversionResult(
            success=True,
            document_id=document.id,
            records_created=records_created,
            records_with_issues=records_with_issues,
            column_mappings=column_mappings,
            message=f"Successfully converted {records_created} records from {filename}"
        )
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Map source columns to standard schema fields using fuzzy matching.
        
        Args:
            columns: List of source column names
            
        Returns:
            Dictionary mapping standard fields to source columns
        """
        mappings = {}
        columns_lower = {c.lower().strip(): c for c in columns}
        
        for standard_field, keywords in self.STANDARD_FIELDS.items():
            for keyword in keywords:
                for col_lower, col_original in columns_lower.items():
                    if keyword in col_lower:
                        if standard_field not in mappings:
                            mappings[standard_field] = col_original
                        break
                if standard_field in mappings:
                    break
        
        return mappings
    
    def _extract_record_data(
        self, 
        row: pd.Series, 
        mappings: Dict[str, str]
    ) -> Dict[str, any]:
        """Extract record data using column mappings."""
        data = {}
        for standard_field, source_col in mappings.items():
            if source_col in row.index:
                value = row[source_col]
                if pd.notna(value):
                    data[standard_field] = str(value).strip()
        return data
    
    def _validate_record(self, data: Dict) -> List[Dict]:
        """Validate record and return list of issues."""
        issues = []
        
        # Check for missing critical fields
        if not data.get('component'):
            issues.append({
                'type': 'missing_field',
                'severity': 'high',
                'field': 'component',
                'description': 'Missing component/part identifier',
                'fix': 'Review source document for component name'
            })
        
        if not data.get('priority'):
            issues.append({
                'type': 'missing_field',
                'severity': 'medium',
                'field': 'priority',
                'description': 'Missing priority level',
                'fix': 'Assign default priority based on maintenance type'
            })
        
        # Check date consistency
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end:
            try:
                start_dt = self._parse_date(start)
                end_dt = self._parse_date(end)
                if start_dt and end_dt and start_dt > end_dt:
                    issues.append({
                        'type': 'date_inconsistency',
                        'severity': 'high',
                        'field': 'start_date,end_date',
                        'description': f'Start date ({start}) is after end date ({end})',
                        'fix': 'Verify and correct date sequence'
                    })
            except:
                pass
        
        # Check cost estimate
        cost = data.get('cost_estimate')
        if cost:
            try:
                cost_val = self._parse_cost(cost)
                if cost_val and cost_val > 1000000:
                    issues.append({
                        'type': 'extreme_value',
                        'severity': 'medium',
                        'field': 'cost_estimate',
                        'description': f'Unusually high cost estimate: ${cost_val:,.2f}',
                        'fix': 'Verify cost value is correct'
                    })
            except:
                issues.append({
                    'type': 'parse_error',
                    'severity': 'low',
                    'field': 'cost_estimate',
                    'description': f'Could not parse cost value: {cost}',
                    'fix': 'Convert to numeric format'
                })
        
        return issues
    
    def _normalize_priority(self, value: Optional[str]) -> Optional[str]:
        """Normalize priority to standard values."""
        if not value:
            return None
        
        value_lower = value.lower().strip()
        
        # Map various priority formats
        if value_lower in ['1', 'high', 'critical', 'urgent', 'p1']:
            return 'high'
        elif value_lower in ['2', 'medium', 'moderate', 'normal', 'p2']:
            return 'medium'
        elif value_lower in ['3', 'low', 'minor', 'routine', 'p3']:
            return 'low'
        
        return value
    
    def _parse_cost(self, value: Optional[str]) -> Optional[float]:
        """Parse cost string to float."""
        if not value:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,\s]', '', str(value))
            return float(cleaned)
        except:
            return None
    
    def _parse_date(self, value: Optional[str]):
        """Parse date string to date object."""
        if not value:
            return None
        
        # Handle various date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except:
                continue
        
        return None
