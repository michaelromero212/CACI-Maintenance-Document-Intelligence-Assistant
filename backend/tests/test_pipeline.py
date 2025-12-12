"""Tests for the extraction pipeline."""

import pytest
from datetime import date
from decimal import Decimal

# Test data normalizer
from services.normalizer import DataNormalizer


class TestDataNormalizer:
    """Test suite for DataNormalizer."""
    
    def setup_method(self):
        self.normalizer = DataNormalizer()
    
    def test_normalize_string_removes_whitespace(self):
        assert self.normalizer.normalize_string("  hello  ") == "hello"
        assert self.normalizer.normalize_string("hello  world") == "hello world"
    
    def test_normalize_string_handles_null_values(self):
        assert self.normalizer.normalize_string(None) is None
        assert self.normalizer.normalize_string("null") is None
        assert self.normalizer.normalize_string("N/A") is None
        assert self.normalizer.normalize_string("") is None
    
    def test_normalize_priority_standard_values(self):
        assert self.normalizer.normalize_priority("high") == "high"
        assert self.normalizer.normalize_priority("medium") == "medium"
        assert self.normalizer.normalize_priority("low") == "low"
    
    def test_normalize_priority_alternate_values(self):
        assert self.normalizer.normalize_priority("1") == "high"
        assert self.normalizer.normalize_priority("P1") == "high"
        assert self.normalizer.normalize_priority("critical") == "high"
        assert self.normalizer.normalize_priority("urgent") == "high"
        
        assert self.normalizer.normalize_priority("2") == "medium"
        assert self.normalizer.normalize_priority("moderate") == "medium"
        
        assert self.normalizer.normalize_priority("3") == "low"
        assert self.normalizer.normalize_priority("routine") == "low"
    
    def test_normalize_status(self):
        assert self.normalizer.normalize_status(None) == "open"
        assert self.normalizer.normalize_status("new") == "open"
        assert self.normalizer.normalize_status("started") == "in-progress"
        assert self.normalizer.normalize_status("waiting") == "awaiting-parts"
        assert self.normalizer.normalize_status("done") == "complete"
    
    def test_normalize_date_iso_format(self):
        result = self.normalizer.normalize_date("2024-01-15")
        assert result == date(2024, 1, 15)
    
    def test_normalize_date_us_format(self):
        result = self.normalizer.normalize_date("01/15/2024")
        assert result == date(2024, 1, 15)
    
    def test_normalize_date_returns_none_for_invalid(self):
        assert self.normalizer.normalize_date(None) is None
        assert self.normalizer.normalize_date("invalid") is None
        assert self.normalizer.normalize_date("N/A") is None
    
    def test_normalize_cost(self):
        assert self.normalizer.normalize_cost("2500") == Decimal("2500")
        assert self.normalizer.normalize_cost("$2,500.00") == Decimal("2500.00")
        assert self.normalizer.normalize_cost(2500) == Decimal("2500")
        assert self.normalizer.normalize_cost(None) is None
    
    def test_normalize_record_complete(self):
        record = {
            'component': '  Pump A-101  ',
            'system': 'Hydraulics',
            'priority': '1',
            'maint_action': 'Replace bearings',
            'cost_estimate': '$2,500',
            'start_date': '2024-01-15',
            'end_date': '2024-01-18',
        }
        
        result = self.normalizer.normalize_record(record)
        
        assert result['component'] == 'Pump A-101'
        assert result['priority'] == 'high'
        assert result['cost_estimate'] == Decimal('2500')
        assert result['start_date'] == date(2024, 1, 15)


# Test anomaly detector
from services.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    """Test suite for AnomalyDetector."""
    
    def setup_method(self):
        self.detector = AnomalyDetector()
    
    def test_detects_missing_component(self):
        record = {'component': None, 'priority': 'high'}
        anomalies = self.detector.detect_anomalies(record)
        
        missing = [a for a in anomalies if a['field_name'] == 'component']
        assert len(missing) == 1
        assert missing[0]['severity'] == 'high'
    
    def test_detects_missing_priority(self):
        record = {'component': 'Pump', 'priority': None}
        anomalies = self.detector.detect_anomalies(record)
        
        missing = [a for a in anomalies if a['field_name'] == 'priority']
        assert len(missing) == 1
    
    def test_detects_date_inconsistency(self):
        record = {
            'component': 'Pump',
            'start_date': '2024-01-20',
            'end_date': '2024-01-15'  # Before start
        }
        anomalies = self.detector.detect_anomalies(record)
        
        date_issues = [a for a in anomalies if a['anomaly_type'] == 'date_inconsistency']
        assert len(date_issues) >= 1
    
    def test_detects_extreme_cost(self):
        record = {
            'component': 'Pump',
            'cost_estimate': 2000000  # Over $1M threshold
        }
        anomalies = self.detector.detect_anomalies(record)
        
        cost_issues = [a for a in anomalies if a['anomaly_type'] == 'extreme_value']
        assert len(cost_issues) >= 1
        assert cost_issues[0]['severity'] == 'high'
    
    def test_detects_negative_cost(self):
        record = {'component': 'Pump', 'cost_estimate': -100}
        anomalies = self.detector.detect_anomalies(record)
        
        invalid = [a for a in anomalies if a['anomaly_type'] == 'invalid_value']
        assert len(invalid) >= 1
    
    def test_valid_record_has_minimal_anomalies(self):
        record = {
            'component': 'Pump A-101',
            'priority': 'high',
            'maint_action': 'Replace bearings',
            'start_date': '2024-01-15',
            'end_date': '2024-01-18',
            'cost_estimate': 2500
        }
        anomalies = self.detector.detect_anomalies(record)
        
        # Should only have low-severity or no anomalies
        high_severity = [a for a in anomalies if a['severity'] == 'high']
        assert len(high_severity) == 0


# Test legacy converter column mapping
from ingestion.legacy_converter import LegacyConverter


class TestLegacyConverterMapping:
    """Test column mapping logic for legacy converter."""
    
    def test_maps_standard_columns(self):
        # Note: This test doesn't need DB, just testing mapping logic
        converter = LegacyConverter.__new__(LegacyConverter)
        converter.STANDARD_FIELDS = LegacyConverter.STANDARD_FIELDS
        
        columns = ['Part Name', 'System', 'Priority Level', 'Maintenance Action', 'Cost']
        mappings = converter._map_columns(columns)
        
        assert 'component' in mappings or 'system' in mappings
    
    def test_maps_legacy_style_columns(self):
        converter = LegacyConverter.__new__(LegacyConverter)
        converter.STANDARD_FIELDS = LegacyConverter.STANDARD_FIELDS
        
        columns = ['EQUIP', 'SYS', 'URG', 'WORK DESC', 'COST$', 'BEGIN', 'COMPL']
        mappings = converter._map_columns(columns)
        
        # These should map to our standard fields based on fuzzy matching
        assert len(mappings) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
