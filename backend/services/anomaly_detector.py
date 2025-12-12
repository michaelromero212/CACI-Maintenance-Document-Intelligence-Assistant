"""Anomaly detection service."""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from decimal import Decimal


class AnomalyDetector:
    """
    Detect data quality anomalies in maintenance records.
    
    Checks for:
    - Date inconsistencies
    - Missing critical fields
    - Extreme cost values
    - Unknown components/systems
    """
    
    # Known valid values for validation
    VALID_PRIORITIES = {'high', 'medium', 'low'}
    COST_WARNING_THRESHOLD = 100000  # Flag costs over $100k
    COST_ERROR_THRESHOLD = 1000000   # Flag costs over $1M
    
    def detect_anomalies(
        self, 
        record: Dict[str, Any],
        known_components: Optional[set] = None,
        known_systems: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a single record.
        
        Args:
            record: Record dictionary to check
            known_components: Optional set of known valid components
            known_systems: Optional set of known valid systems
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for missing critical fields
        anomalies.extend(self._check_missing_fields(record))
        
        # Check date consistency
        anomalies.extend(self._check_dates(record))
        
        # Check cost values
        anomalies.extend(self._check_cost(record))
        
        # Check priority validity
        anomalies.extend(self._check_priority(record))
        
        # Check against known values
        if known_components:
            anomalies.extend(
                self._check_unknown_value(
                    record, 'component', known_components
                )
            )
        
        if known_systems:
            anomalies.extend(
                self._check_unknown_value(
                    record, 'system', known_systems
                )
            )
        
        return anomalies
    
    def _check_missing_fields(self, record: Dict[str, Any]) -> List[Dict]:
        """Check for missing critical fields."""
        anomalies = []
        
        critical_fields = [
            ('component', 'high', 'Component identifier is required'),
            ('priority', 'medium', 'Priority level should be assigned'),
            ('maint_action', 'medium', 'Maintenance action should be described'),
        ]
        
        for field, severity, message in critical_fields:
            if not record.get(field):
                anomalies.append({
                    'anomaly_type': 'missing_field',
                    'severity': severity,
                    'description': message,
                    'field_name': field,
                    'field_value': None,
                    'suggested_fix': f'Review source document for {field} information'
                })
        
        return anomalies
    
    def _check_dates(self, record: Dict[str, Any]) -> List[Dict]:
        """Check date field consistency."""
        anomalies = []
        
        start_date = record.get('start_date')
        end_date = record.get('end_date')
        
        if start_date and end_date:
            # Convert to date objects if strings
            if isinstance(start_date, str):
                try:
                    start_date = date.fromisoformat(start_date)
                except:
                    start_date = None
            
            if isinstance(end_date, str):
                try:
                    end_date = date.fromisoformat(end_date)
                except:
                    end_date = None
            
            if start_date and end_date:
                # Check if end is before start
                if end_date < start_date:
                    anomalies.append({
                        'anomaly_type': 'date_inconsistency',
                        'severity': 'high',
                        'description': f'End date ({end_date}) is before start date ({start_date})',
                        'field_name': 'end_date',
                        'field_value': str(end_date),
                        'suggested_fix': 'Verify and correct date sequence'
                    })
                
                # Check for unusually long duration (over 1 year)
                duration = (end_date - start_date).days
                if duration > 365:
                    anomalies.append({
                        'anomaly_type': 'date_inconsistency',
                        'severity': 'low',
                        'description': f'Maintenance duration ({duration} days) exceeds 1 year',
                        'field_name': 'duration',
                        'field_value': str(duration),
                        'suggested_fix': 'Verify dates are correct or split into phases'
                    })
                
                # Check for future dates
                today = date.today()
                if end_date > today + timedelta(days=365):
                    anomalies.append({
                        'anomaly_type': 'date_inconsistency',
                        'severity': 'medium',
                        'description': f'End date ({end_date}) is more than 1 year in the future',
                        'field_name': 'end_date',
                        'field_value': str(end_date),
                        'suggested_fix': 'Verify projected completion date'
                    })
        
        return anomalies
    
    def _check_cost(self, record: Dict[str, Any]) -> List[Dict]:
        """Check cost estimate values."""
        anomalies = []
        
        cost = record.get('cost_estimate')
        if cost is not None:
            try:
                cost_val = float(cost)
                
                if cost_val < 0:
                    anomalies.append({
                        'anomaly_type': 'invalid_value',
                        'severity': 'high',
                        'description': f'Negative cost estimate: ${cost_val:,.2f}',
                        'field_name': 'cost_estimate',
                        'field_value': str(cost_val),
                        'suggested_fix': 'Cost cannot be negative'
                    })
                elif cost_val > self.COST_ERROR_THRESHOLD:
                    anomalies.append({
                        'anomaly_type': 'extreme_value',
                        'severity': 'high',
                        'description': f'Extremely high cost estimate: ${cost_val:,.2f}',
                        'field_name': 'cost_estimate',
                        'field_value': str(cost_val),
                        'suggested_fix': 'Verify cost value or add justification'
                    })
                elif cost_val > self.COST_WARNING_THRESHOLD:
                    anomalies.append({
                        'anomaly_type': 'extreme_value',
                        'severity': 'medium',
                        'description': f'High cost estimate: ${cost_val:,.2f}',
                        'field_name': 'cost_estimate',
                        'field_value': str(cost_val),
                        'suggested_fix': 'Verify cost estimate is accurate'
                    })
            except (ValueError, TypeError):
                anomalies.append({
                    'anomaly_type': 'parse_error',
                    'severity': 'low',
                    'description': f'Could not parse cost value: {cost}',
                    'field_name': 'cost_estimate',
                    'field_value': str(cost),
                    'suggested_fix': 'Convert to numeric format'
                })
        
        return anomalies
    
    def _check_priority(self, record: Dict[str, Any]) -> List[Dict]:
        """Check priority value validity."""
        anomalies = []
        
        priority = record.get('priority')
        if priority and str(priority).lower() not in self.VALID_PRIORITIES:
            anomalies.append({
                'anomaly_type': 'invalid_value',
                'severity': 'low',
                'description': f'Non-standard priority value: {priority}',
                'field_name': 'priority',
                'field_value': str(priority),
                'suggested_fix': 'Use standard priority: high, medium, or low'
            })
        
        return anomalies
    
    def _check_unknown_value(
        self, 
        record: Dict[str, Any],
        field: str,
        known_values: set
    ) -> List[Dict]:
        """Check if value is in known set."""
        anomalies = []
        
        value = record.get(field)
        if value and str(value).lower() not in {v.lower() for v in known_values}:
            anomalies.append({
                'anomaly_type': 'unknown_value',
                'severity': 'low',
                'description': f'Unknown {field}: {value}',
                'field_name': field,
                'field_value': str(value),
                'suggested_fix': f'Verify {field} name or add to known list'
            })
        
        return anomalies
