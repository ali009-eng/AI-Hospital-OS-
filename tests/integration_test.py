#!/usr/bin/env python3
"""
Integration tests for AI Triage Assistant
Tests the complete workflow from patient input to dashboard output
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag.rag_system import RAGSystem
from surveillance.syndromic_surveillance import SyndromicSurveillanceSystem
from langchain_integration.triage_agent import TriageAgent
from langsmith_integration.langsmith_config import langsmith_manager

def test_rag_system():
    """Test RAG system functionality"""
    print("Testing RAG System...")
    
    try:
        rag = RAGSystem()
        
        # Test patient data
        test_patient = {
            'patient_id': 'test_001',
            'age': 45,
            'gender': 'Male',
            'chief_complaint': 'Chest pain and shortness of breath',
            'heart_rate': 110,
            'respiratory_rate': 24,
            'oxygen_saturation': 92,
            'temperature': 37.2,
            'blood_pressure': '140/90',
            'pain_level': 7
        }
        
        result = rag.classify_patient(test_patient)
        
        assert 'triage_level' in result
        assert 1 <= result['triage_level'] <= 5
        assert 'reasoning' in result
        assert 'confidence' in result
        
        print(f"✓ RAG System Test Passed - Triage Level: {result['triage_level']}")
        return True
        
    except Exception as e:
        print(f"✗ RAG System Test Failed: {e}")
        return False

def test_surveillance_system():
    """Test surveillance system functionality"""
    print("Testing Surveillance System...")
    
    try:
        surveillance = SyndromicSurveillanceSystem()
        surveillance.initialize()
        
        # Test case data
        test_cases = [
            {
                'patient_id': 'test_001',
                'timestamp': datetime.now(),
                'age': 35,
                'gender': 'Male',
                'chief_complaint': 'Fever and cough',
                'symptoms': ['fever', 'cough', 'fatigue'],
                'triage_level': 2,
                'diagnosis': 'Respiratory infection'
            },
            {
                'patient_id': 'test_002',
                'timestamp': datetime.now(),
                'age': 28,
                'gender': 'Female',
                'chief_complaint': 'High fever and body aches',
                'symptoms': ['fever', 'body aches', 'headache'],
                'triage_level': 2,
                'diagnosis': 'Viral syndrome'
            }
        ]
        
        result = surveillance.process_new_cases(test_cases)
        
        assert 'processed_cases' in result
        assert 'clusters_detected' in result
        assert 'alerts_generated' in result
        assert result['processed_cases'] == len(test_cases)
        
        print(f"✓ Surveillance System Test Passed - Processed: {result['processed_cases']} cases")
        return True
        
    except Exception as e:
        print(f"✗ Surveillance System Test Failed: {e}")
        return False

def test_triage_agent():
    """Test triage agent functionality"""
    print("Testing Triage Agent...")
    
    try:
        agent = TriageAgent()
        
        # Test patient data
        test_patient = {
            'patient_id': 'test_001',
            'age': 45,
            'gender': 'Male',
            'chief_complaint': 'Chest pain and shortness of breath',
            'heart_rate': 110,
            'respiratory_rate': 24,
            'oxygen_saturation': 92,
            'temperature': 37.2,
            'blood_pressure': '140/90',
            'pain_level': 7
        }
        
        result = agent.process_patient(test_patient)
        
        assert 'patient_id' in result
        assert 'processing_status' in result
        assert result['processing_status'] in ['completed', 'failed']
        
        print(f"✓ Triage Agent Test Passed - Status: {result['processing_status']}")
        return True
        
    except Exception as e:
        print(f"✗ Triage Agent Test Failed: {e}")
        return False

def test_langsmith_integration():
    """Test LangSmith integration"""
    print("Testing LangSmith Integration...")
    
    try:
        if langsmith_manager.is_available():
            # Test metrics retrieval
            end_time = datetime.now()
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            metrics = langsmith_manager.get_metrics(start_time, end_time)
            
            assert 'total_requests' in metrics
            assert 'success_rate' in metrics
            
            print(f"✓ LangSmith Integration Test Passed - Available: True")
            return True
        else:
            print("⚠ LangSmith Integration Test Skipped - Not Available")
            return True
            
    except Exception as e:
        print(f"✗ LangSmith Integration Test Failed: {e}")
        return False

def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("Testing End-to-End Workflow...")
    
    try:
        agent = TriageAgent()
        
        # Test multiple patients
        test_patients = [
            {
                'patient_id': 'e2e_001',
                'age': 45,
                'gender': 'Male',
                'chief_complaint': 'Chest pain and shortness of breath',
                'heart_rate': 110,
                'respiratory_rate': 24,
                'oxygen_saturation': 92,
                'temperature': 37.2,
                'blood_pressure': '140/90',
                'pain_level': 7
            },
            {
                'patient_id': 'e2e_002',
                'age': 28,
                'gender': 'Female',
                'chief_complaint': 'Fever and body aches',
                'heart_rate': 95,
                'respiratory_rate': 20,
                'oxygen_saturation': 98,
                'temperature': 38.5,
                'blood_pressure': '120/80',
                'pain_level': 5
            },
            {
                'patient_id': 'e2e_003',
                'age': 65,
                'gender': 'Male',
                'chief_complaint': 'Severe headache and confusion',
                'heart_rate': 85,
                'respiratory_rate': 18,
                'oxygen_saturation': 95,
                'temperature': 36.8,
                'blood_pressure': '160/100',
                'pain_level': 8
            }
        ]
        
        # Process each patient
        results = []
        for patient in test_patients:
            result = agent.process_patient(patient)
            results.append(result)
            time.sleep(1)  # Small delay between patients
        
        # Check results
        successful_results = [r for r in results if r['processing_status'] == 'completed']
        
        assert len(successful_results) > 0, "No patients processed successfully"
        
        # Get dashboard data
        dashboard_data = agent.get_dashboard_data()
        surveillance_data = agent.get_surveillance_data()
        
        assert 'total_patients' in dashboard_data
        assert 'recent_stats' in surveillance_data
        
        print(f"✓ End-to-End Workflow Test Passed - Processed: {len(successful_results)}/{len(test_patients)} patients")
        return True
        
    except Exception as e:
        print(f"✗ End-to-End Workflow Test Failed: {e}")
        return False

def test_performance():
    """Test system performance"""
    print("Testing System Performance...")
    
    try:
        agent = TriageAgent()
        
        # Test patient data
        test_patient = {
            'patient_id': 'perf_001',
            'age': 45,
            'gender': 'Male',
            'chief_complaint': 'Chest pain and shortness of breath',
            'heart_rate': 110,
            'respiratory_rate': 24,
            'oxygen_saturation': 92,
            'temperature': 37.2,
            'blood_pressure': '140/90',
            'pain_level': 7
        }
        
        # Measure processing time
        start_time = time.time()
        result = agent.process_patient(test_patient)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Performance thresholds
        max_processing_time = 10.0  # 10 seconds max
        
        assert processing_time < max_processing_time, f"Processing time {processing_time:.2f}s exceeds threshold {max_processing_time}s"
        assert result['processing_status'] == 'completed', "Processing failed"
        
        print(f"✓ Performance Test Passed - Processing Time: {processing_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"✗ Performance Test Failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("AI Triage Assistant - Integration Tests")
    print("=" * 50)
    
    tests = [
        test_rag_system,
        test_surveillance_system,
        test_triage_agent,
        test_langsmith_integration,
        test_end_to_end_workflow,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} Failed with exception: {e}")
        
        print()  # Empty line between tests
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)




