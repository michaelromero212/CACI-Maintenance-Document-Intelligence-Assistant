"""Excel and CSV extraction using pandas."""

import pandas as pd
from io import BytesIO
from typing import List, Dict, Any, Optional


class ExcelExtractor:
    """Extract and parse data from Excel and CSV files."""
    
    def extract_dataframe(
        self, 
        file_path: str, 
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract data from Excel or CSV file.
        
        Args:
            file_path: Path to the file
            sheet_name: Optional sheet name for Excel files
            
        Returns:
            DataFrame with extracted data
        """
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path, sheet_name=sheet_name or 0)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def extract_from_bytes(
        self, 
        content: bytes, 
        file_type: str,
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract data from file bytes.
        
        Args:
            content: File content as bytes
            file_type: Type of file ('csv', 'excel')
            sheet_name: Optional sheet name for Excel files
            
        Returns:
            DataFrame with extracted data
        """
        buffer = BytesIO(content)
        
        if file_type == 'csv':
            return pd.read_csv(buffer)
        elif file_type == 'excel':
            return pd.read_excel(buffer, sheet_name=sheet_name or 0)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """Get list of sheet names from Excel file."""
        if file_path.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(file_path)
            return xl.sheet_names
        return []
    
    def to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of dictionaries.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of row dictionaries
        """
        # Replace NaN with None
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    
    def extract_text_representation(self, df: pd.DataFrame) -> str:
        """
        Create a text representation of the DataFrame.
        
        Useful for LLM processing.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Text representation of the data
        """
        lines = []
        lines.append(f"Columns: {', '.join(df.columns.tolist())}")
        lines.append(f"Total rows: {len(df)}")
        lines.append("")
        
        # Add rows as text
        for idx, row in df.iterrows():
            row_text = " | ".join(
                f"{col}: {val}" for col, val in row.items() 
                if pd.notna(val)
            )
            lines.append(f"Row {idx + 1}: {row_text}")
            
            # Limit to first 100 rows for LLM context
            if idx >= 99:
                lines.append(f"... and {len(df) - 100} more rows")
                break
        
        return "\n".join(lines)
