"""Complete document ingestion pipeline."""

import os
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from models.models import Document, ExtractedRecord, Anomaly
from ingestion.pdf_extractor import PDFExtractor
from ingestion.excel_extractor import ExcelExtractor
from llm.extractor import LLMExtractor
from services.normalizer import DataNormalizer
from services.anomaly_detector import AnomalyDetector


UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "uploads"))


class IngestionPipeline:
    """
    Complete document processing pipeline.
    
    Steps:
    1. Extract raw text from document
    2. Run LLM extraction for structured data
    3. Normalize extracted data
    4. Detect anomalies
    5. Store records in database
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_extractor = PDFExtractor()
        self.excel_extractor = ExcelExtractor()
        self.llm_extractor = LLMExtractor()
        self.normalizer = DataNormalizer()
        self.anomaly_detector = AnomalyDetector()
    
    async def process_document(self, document_id: UUID) -> bool:
        """
        Process a document through the full pipeline.
        
        Args:
            document_id: UUID of the document to process
            
        Returns:
            True if processing succeeded
        """
        # Get document
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        
        if not document:
            return False
        
        try:
            # Step 1: Extract raw text
            raw_text = await self._extract_text(document)
            document.raw_text = raw_text
            
            # Step 2: LLM extraction
            records_data = await self.llm_extractor.extract_records(raw_text)
            
            # Step 3 & 4: Normalize and detect anomalies for each record
            for record_data in records_data:
                # Normalize
                normalized = self.normalizer.normalize_record(record_data)
                
                # Create record
                record = ExtractedRecord(
                    document_id=document.id,
                    component=normalized.get('component'),
                    system=normalized.get('system'),
                    failure_type=normalized.get('failure_type'),
                    maint_action=normalized.get('maint_action'),
                    priority=normalized.get('priority'),
                    start_date=normalized.get('start_date'),
                    end_date=normalized.get('end_date'),
                    cost_estimate=normalized.get('cost_estimate'),
                    summary_notes=normalized.get('summary_notes'),
                    status='open',
                    extraction_method='llm' if records_data else 'regex',
                    confidence_score=0.85
                )
                self.db.add(record)
                self.db.flush()
                
                # Detect anomalies
                anomalies = self.anomaly_detector.detect_anomalies(normalized)
                
                for anomaly_data in anomalies:
                    anomaly = Anomaly(
                        record_id=record.id,
                        document_id=document.id,
                        anomaly_type=anomaly_data['anomaly_type'],
                        severity=anomaly_data['severity'],
                        description=anomaly_data['description'],
                        field_name=anomaly_data.get('field_name'),
                        field_value=anomaly_data.get('field_value'),
                        suggested_fix=anomaly_data.get('suggested_fix')
                    )
                    self.db.add(anomaly)
            
            # Update document status
            document.processed = True
            document.processing_status = 'complete'
            
            self.db.commit()
            return True
            
        except Exception as e:
            document.processing_status = f'error: {str(e)[:100]}'
            self.db.commit()
            raise
    
    async def _extract_text(self, document: Document) -> str:
        """Extract raw text based on file type."""
        file_path = os.path.join(UPLOAD_DIR, f"{document.id}{self._get_extension(document)}")
        
        if document.file_type == 'pdf':
            return self.pdf_extractor.extract_text(file_path)
        
        elif document.file_type in ['excel', 'csv']:
            df = self.excel_extractor.extract_dataframe(file_path)
            return self.excel_extractor.extract_text_representation(df)
        
        elif document.file_type in ['text', 'log']:
            with open(file_path, 'r', errors='ignore') as f:
                return f.read()
        
        return ""
    
    def _get_extension(self, document: Document) -> str:
        """Get file extension from filename."""
        if '.' in document.filename:
            return '.' + document.filename.rsplit('.', 1)[1].lower()
        
        ext_map = {
            'pdf': '.pdf',
            'excel': '.xlsx',
            'csv': '.csv',
            'text': '.txt',
            'log': '.log'
        }
        return ext_map.get(document.file_type, '.txt')
