"""
Data Tool - Data Analysis Module
Handles CSV/data file analysis and reporting
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataTool:
    """
    Data analysis tool for reading and analyzing data files.
    Supports CSV, JSON, and other common data formats.
    """
    
    def __init__(self):
        """Initialize Data Tool"""
        pass
    
    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, any]:
        """
        Read a CSV file and return its contents.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            
        Returns:
            Dictionary with data and metadata
        """
        try:
            import pandas as pd
            
            path = Path(file_path)
            
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            df = pd.read_csv(path, encoding=encoding)
            
            return {
                "success": True,
                "file_path": str(path.absolute()),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "preview": df.head(10).to_dict('records'),
                "dataframe": df  # For further processing
            }
            
        except ImportError:
            return {"success": False, "error": "Pandas not installed. Run: pip install pandas"}
        except Exception as e:
            return {"success": False, "error": f"Error reading CSV: {str(e)}"}
    
    def analyze_data(self, file_path: str) -> Dict[str, any]:
        """
        Perform comprehensive data analysis.
        
        Args:
            file_path: Path to data file
            
        Returns:
            Analysis results
        """
        try:
            import pandas as pd
            import numpy as np
            
            # Read the file
            read_result = self.read_csv(file_path)
            
            if not read_result.get("success"):
                return read_result
            
            df = read_result["dataframe"]
            
            # Basic statistics
            analysis = {
                "success": True,
                "file_path": file_path,
                "basic_info": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
                },
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "numeric_summary": {},
                "categorical_summary": {},
                "insights": []
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                numeric_stats = df[numeric_cols].describe().to_dict()
                analysis["numeric_summary"] = numeric_stats
                
                # Generate insights
                for col in numeric_cols:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    
                    if std_val > mean_val:
                        analysis["insights"].append(
                            f"Column '{col}' has high variability (std > mean)"
                        )
                    
                    # Check for outliers
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
                    
                    if outliers > 0:
                        analysis["insights"].append(
                            f"Column '{col}' has {outliers} potential outliers"
                        )
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if categorical_cols:
                for col in categorical_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    unique_count = df[col].nunique()
                    
                    analysis["categorical_summary"][col] = {
                        "unique_values": unique_count,
                        "top_values": value_counts
                    }
                    
                    # Insight for categorical
                    if unique_count == len(df):
                        analysis["insights"].append(
                            f"Column '{col}' appears to be a unique identifier"
                        )
            
            # Check for missing values
            missing_total = df.isnull().sum().sum()
            if missing_total > 0:
                missing_pct = (missing_total / (len(df) * len(df.columns))) * 100
                analysis["insights"].append(
                    f"Dataset has {missing_total} missing values ({missing_pct:.2f}% of total)"
                )
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                analysis["insights"].append(
                    f"Dataset has {duplicates} duplicate rows"
                )
            
            return analysis
            
        except ImportError:
            return {"success": False, "error": "Pandas/NumPy not installed"}
        except Exception as e:
            return {"success": False, "error": f"Analysis error: {str(e)}"}
    
    def generate_summary(self, file_path: str) -> Dict[str, any]:
        """
        Generate a text summary of the data analysis.
        
        Args:
            file_path: Path to data file
            
        Returns:
            Summary dictionary with formatted text
        """
        analysis = self.analyze_data(file_path)
        
        if not analysis.get("success"):
            return analysis
        
        summary_lines = [
            "=" * 60,
            "DATA ANALYSIS SUMMARY",
            "=" * 60,
            f"File: {analysis['file_path']}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "BASIC INFORMATION",
            "-" * 40,
            f"Total Rows: {analysis['basic_info']['rows']}",
            f"Total Columns: {analysis['basic_info']['columns']}",
            f"Memory Usage: {analysis['basic_info']['memory_usage']}",
            f"Columns: {', '.join(analysis['basic_info']['column_names'])}",
            ""
        ]
        
        # Numeric summary
        if analysis["numeric_summary"]:
            summary_lines.extend([
                "NUMERIC COLUMNS SUMMARY",
                "-" * 40
            ])
            
            for col, stats in analysis["numeric_summary"].items():
                summary_lines.append(f"\n{col}:")
                summary_lines.append(f"  Mean: {stats.get('mean', 'N/A'):.2f}")
                summary_lines.append(f"  Std: {stats.get('std', 'N/A'):.2f}")
                summary_lines.append(f"  Min: {stats.get('min', 'N/A'):.2f}")
                summary_lines.append(f"  Max: {stats.get('max', 'N/A'):.2f}")
        
        # Categorical summary
        if analysis["categorical_summary"]:
            summary_lines.extend([
                "",
                "CATEGORICAL COLUMNS SUMMARY",
                "-" * 40
            ])
            
            for col, info in analysis["categorical_summary"].items():
                summary_lines.append(f"\n{col}:")
                summary_lines.append(f"  Unique Values: {info['unique_values']}")
                top_val = list(info['top_values'].items())[:3]
                for val, count in top_val:
                    summary_lines.append(f"  - {val}: {count}")
        
        # Missing values
        missing = analysis["missing_values"]
        cols_with_missing = {k: v for k, v in missing.items() if v > 0}
        
        if cols_with_missing:
            summary_lines.extend([
                "",
                "MISSING VALUES",
                "-" * 40
            ])
            for col, count in cols_with_missing.items():
                summary_lines.append(f"  {col}: {count}")
        
        # Insights
        if analysis["insights"]:
            summary_lines.extend([
                "",
                "KEY INSIGHTS",
                "-" * 40
            ])
            for insight in analysis["insights"]:
                summary_lines.append(f"• {insight}")
        
        summary_lines.extend(["", "=" * 60])
        
        summary_text = "\n".join(summary_lines)
        
        return {
            "success": True,
            "summary_text": summary_text,
            "analysis": analysis
        }
    
    def save_analysis(
        self,
        file_path: str,
        output_path: str = None,
        format: str = "txt"
    ) -> Dict[str, any]:
        """
        Analyze data and save results to file.
        
        Args:
            file_path: Path to data file
            output_path: Path for output file
            format: Output format ('txt' or 'json')
            
        Returns:
            Result dictionary
        """
        summary = self.generate_summary(file_path)
        
        if not summary.get("success"):
            return summary
        
        if output_path is None:
            from config import OUTPUT_DIR
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"analysis_{timestamp}.{format}"
        
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                import json
                # Remove non-serializable dataframe
                analysis = summary["analysis"].copy()
                analysis.pop("dataframe", None)
                
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, default=str)
            else:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(summary["summary_text"])
            
            return {
                "success": True,
                "message": f"Analysis saved to {output_path}",
                "file_path": str(output.absolute())
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error saving analysis: {str(e)}"}
    
    def filter_data(
        self,
        file_path: str,
        conditions: Dict[str, any],
        output_path: str = None
    ) -> Dict[str, any]:
        """
        Filter data based on conditions.
        
        Args:
            file_path: Path to data file
            conditions: Dict of column: value or column: {operator: value}
            output_path: Optional path to save filtered data
            
        Returns:
            Filtered data results
        """
        try:
            import pandas as pd
            
            read_result = self.read_csv(file_path)
            
            if not read_result.get("success"):
                return read_result
            
            df = read_result["dataframe"]
            mask = pd.Series([True] * len(df))
            
            for col, condition in conditions.items():
                if col not in df.columns:
                    continue
                
                if isinstance(condition, dict):
                    for op, value in condition.items():
                        if op == "gt":
                            mask &= df[col] > value
                        elif op == "lt":
                            mask &= df[col] < value
                        elif op == "gte":
                            mask &= df[col] >= value
                        elif op == "lte":
                            mask &= df[col] <= value
                        elif op == "contains":
                            mask &= df[col].astype(str).str.contains(value, case=False)
                else:
                    mask &= df[col] == condition
            
            filtered_df = df[mask]
            
            result = {
                "success": True,
                "original_rows": len(df),
                "filtered_rows": len(filtered_df),
                "preview": filtered_df.head(20).to_dict('records')
            }
            
            # Save if output path provided
            if output_path:
                filtered_df.to_csv(output_path, index=False)
                result["saved_to"] = output_path
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Filter error: {str(e)}"}
    
    def get_correlation(self, file_path: str) -> Dict[str, any]:
        """
        Calculate correlation matrix for numeric columns.
        
        Args:
            file_path: Path to data file
            
        Returns:
            Correlation matrix
        """
        try:
            import pandas as pd
            import numpy as np
            
            read_result = self.read_csv(file_path)
            
            if not read_result.get("success"):
                return read_result
            
            df = read_result["dataframe"]
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {"success": False, "error": "No numeric columns found"}
            
            corr_matrix = numeric_df.corr()
            
            # Find high correlations
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr.append({
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": round(corr_val, 3)
                        })
            
            return {
                "success": True,
                "correlation_matrix": corr_matrix.to_dict(),
                "high_correlations": high_corr
            }
            
        except Exception as e:
            return {"success": False, "error": f"Correlation error: {str(e)}"}
    
    def create_sample_csv(self, output_path: str) -> Dict[str, any]:
        """
        Create a sample CSV file for testing.
        
        Args:
            output_path: Path to save sample file
            
        Returns:
            Result dictionary
        """
        try:
            import random
            
            # Generate sample data
            headers = ["ID", "Name", "Age", "City", "Salary", "Department"]
            
            names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
            cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
            departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
            
            rows = []
            for i in range(1, 51):
                row = [
                    i,
                    random.choice(names),
                    random.randint(22, 60),
                    random.choice(cities),
                    random.randint(30000, 120000),
                    random.choice(departments)
                ]
                rows.append(row)
            
            # Write to file
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(",".join(headers) + "\n")
                for row in rows:
                    f.write(",".join(map(str, row)) + "\n")
            
            return {
                "success": True,
                "message": f"Sample CSV created: {output_path}",
                "file_path": str(path.absolute()),
                "rows": len(rows),
                "columns": len(headers)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error creating sample: {str(e)}"}
