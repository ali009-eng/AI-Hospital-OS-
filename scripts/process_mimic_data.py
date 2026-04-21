#!/usr/bin/env python3
"""
Script to process MIMIC-IV-ED dataset for RAG system
Run this script after placing your MIMIC data files in the correct directory
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data_processing.mimic_processor import MIMICProcessor
from config import Config

def main():
    """Main function to process MIMIC-IV-ED dataset"""
    
    # Check if data directory exists
    data_path = Path(Config.MIMIC_DATA_PATH)
    if not data_path.exists():
        
        return
    
    # Check for required files
    required_files = [f"{table}.csv" for table in Config.MIMIC_TABLES]
    missing_files = []
    
    for file_name in required_files:
        file_path = data_path / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print("Missing required MIMIC-IV-ED files:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        print("\nPlease download the MIMIC-IV-ED dataset from PhysioNet and place the CSV files in:")
        print(f"  {data_path}")
        return
    
    print("All required MIMIC-IV-ED files found!")
    print("Starting dataset processing...")
    
    try:
        # Initialize processor
        processor = MIMICProcessor()
        
        # Process the dataset
        processor.process_dataset()
        
        print("✅ MIMIC-IV-ED dataset processing completed successfully!")
        print("The RAG system is now ready to use with your data.")
        
    except Exception as e:
        print(f"❌ Error processing dataset: {e}")
        raise

if __name__ == "__main__":
    main()


