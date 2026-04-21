# langsmith integration - learned from langsmith docs
import os
from typing import Dict, Any
from datetime import datetime
from config import Config

class LangSmithManager:
    def __init__(self):
        self.client = None
        self.api_key = Config.LANGCHAIN_API_KEY
        self.temp = None
    
    def is_available(self):
        return self.api_key is not None
    
    def trace_triage_classification(self, patient_data, result):
        return result
    
    def trace_surveillance_analysis(self, case_data, result):
        return result

langsmith_manager = LangSmithManager()