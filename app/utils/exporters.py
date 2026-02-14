# app/utils/exporters.py
"""
Data export utilities
Version: 1.0.0
"""
import csv
import json
import io
from datetime import datetime
import pandas as pd
from flask import Response

class BaseExporter:
    """Base exporter class"""
    
    def __init__(self, data, filename_prefix):
        self.data = data
        self.filename_prefix = filename_prefix
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def get_filename(self, extension):
        return f"{self.filename_prefix}_{self.timestamp}.{extension}"

class CSVExporter(BaseExporter):
    """CSV exporter"""
    
    def export(self):
        output = io.StringIO()
        
        if isinstance(self.data, list):
            if self.data:
                writer = csv.DictWriter(output, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
        elif isinstance(self.data, dict):
            # Flatten nested dictionary
            flattened = []
            for key, items in self.data.items():
                if isinstance(items, list):
                    for item in items:
                        item['_data_type'] = key
                        flattened.append(item)
            
            if flattened:
                writer = csv.DictWriter(output, fieldnames=flattened[0].keys())
                writer.writeheader()
                writer.writerows(flattened)
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={self.get_filename("csv")}'
            }
        )

class JSONExporter(BaseExporter):
    """JSON exporter"""
    
    def export(self, pretty=True):
        indent = 2 if pretty else None
        
        return Response(
            json.dumps(self.data, default=str, indent=indent),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename={self.get_filename("json")}'
            }
        )

class ExcelExporter(BaseExporter):
    """Excel exporter"""
    
    def export(self):
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if isinstance(self.data, list):
                df = pd.DataFrame(self.data)
                df.to_excel(writer, sheet_name='Data', index=False)
            elif isinstance(self.data, dict):
                for key, items in self.data.items():
                    if isinstance(items, list):
                        df = pd.DataFrame(items)
                        df.to_excel(writer, sheet_name=key.capitalize(), index=False)
            
            # Auto-adjust column widths
            for worksheet in writer.sheets.values():
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={self.get_filename("xlsx")}'
            }
        )

def get_exporter(format, data, filename_prefix):
    """Factory function to get appropriate exporter"""
    exporters = {
        'csv': CSVExporter,
        'json': JSONExporter,
        'excel': ExcelExporter,
        'xlsx': ExcelExporter
    }
    
    exporter_class = exporters.get(format.lower())
    if not exporter_class:
        raise ValueError(f"Unsupported export format: {format}")
    
    return exporter_class(data, filename_prefix)