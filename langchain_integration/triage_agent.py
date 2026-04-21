# Emergency Department Triage Agent
# Integrates LangChain agents with RAG system for patient classification
from typing import List, Dict, Any, Optional, Type
import json
from datetime import datetime

from langchain.agents import Tool, AgentExecutor, create_react_agent # important for the agent, tools to update the api and the 
# create react agent this will be usd to make the agent later 
from langchain.prompts import PromptTemplate    # making a chain to invoke very important as well 
from langchain.tools import BaseTool # basetool class to makr the tool 
from langchain.callbacks import BaseCallbackHandler, CallbackManager # for tracing and monitoring uing a free api key from langchain 
from pydantic import BaseModel, Field # data vaildtion 

from rag.rag_system import RAGSystem # will be used later to make the prompt 
from surveillance.syndromic_surveillance import SyndromicSurveillanceSystem # syndromic surveilncc
from config import Config # config file easyier to manage insted of hard coded values 


class TriageTool(BaseTool):
    """Tool for patient triage classification using RAG system."""
    
    name = "patient_triage"
    description = "Classify patient triage level based on symptoms and vitals"
    
    def __init__(self, rag_system: RAGSystem):
        super().__init__()
        self.rag_system = rag_system
    
    def _run(self, patient_data: Dict[str, Any]) -> str:
        """Execute triage classification for patient data."""
        
        try:
            result = self.rag_system.classify_patient(patient_data)
            
            # format the output
            output = {
                'patient_id': patient_data.get('patient_id'),
                'triage_level': result['triage_level'],
                'esi_level': Config.ESI_LEVELS.get(result['triage_level'], 'Unknown'),
                'reasoning': result['reasoning'],
                'risk_factors': result['risk_factors'],
                'recommendations': result['recommendations'],
                'confidence': result['confidence'],
                'rag_cases_used': result['retrieved_cases'],
                'timestamp': datetime.now().isoformat()
            }
            
            return json.dumps(output, indent=2)
            
        except Exception as e:
            # Return safe fallback on error
            return json.dumps({
                'error': str(e),
                'patient_id': patient_data.get('patient_id'),
                'triage_level': 3,  # Default to medium priority
                'timestamp': datetime.now().isoformat()
            })

class DashboardUpdateTool(BaseTool):
    """Tool for updating dashboard with patient information"""
    
    name = "update_dashboard"
    description = "update dashboard with patient info"
    
    def __init__(self):
        super().__init__()
        self.dashboard_data = []
        self.patient_queue = []  # patient queue
    
    def _run(self, patient_id: str, triage_result: Dict[str, Any], timestamp: str) -> str:
        """Update dashboard with patient information"""
        if not patient_id:
            return json.dumps({
                'status': 'error',
                'error': 'patient_id is required',
                'timestamp': datetime.now().isoformat()
            })
        
        if not triage_result or not isinstance(triage_result, dict):
            return json.dumps({
                'status': 'error',
                'error': 'triage_result must be a dictionary',
                'patient_id': patient_id,
                'timestamp': datetime.now().isoformat()
            })
        
        try:
            # create entry
            dashboard_entry = {
                'patient_id': patient_id,
                'triage_level': triage_result.get('triage_level', 3),
                'esi_level': Config.ESI_LEVELS.get(triage_result.get('triage_level', 3), 'Unknown'),
                'priority_score': self._calculate_priority_score(triage_result),
                'timestamp': timestamp,
                'status': 'active',
                'last_updated': datetime.now().isoformat()
            }
            
            self.dashboard_data.append(dashboard_entry)
            
            # sort by priority (lower = higher priority)
            self.dashboard_data.sort(key=lambda x: (x['triage_level'], x['timestamp']))
            
            # keep only recent ones
            if len(self.dashboard_data) > Config.MAX_PATIENTS_DISPLAY:
                self.dashboard_data = self.dashboard_data[-Config.MAX_PATIENTS_DISPLAY:]
            
            summary = self._generate_dashboard_summary()
            
            return json.dumps({
                'status': 'success',
                'patient_id': patient_id,
                'dashboard_updated': True,
                'current_position': self._get_patient_position(patient_id),
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            # print(f"debug: error in dashboard update: {e}")  # had this for debugging
            return json.dumps({
                'status': 'error',
                'error': str(e),
                'patient_id': patient_id,
                'timestamp': datetime.now().isoformat()
            })
    
    def _calculate_priority_score(self, triage_result: Dict[str, Any]) -> float:
        """
        Calculate priority score for patient.
        
        Formula: base_score * confidence_multiplier * risk_multiplier
        Higher score = higher priority
        """
        base_score = 5 - triage_result.get('triage_level', 3)  # invert triage level (1->4, 5->0)
        
        # adjust based on confidence
        confidence = triage_result.get('confidence', 0.5)
        confidence_multiplier = 0.5 + (confidence * 0.5)
        
        # adjust based on risk factors
        risk_factors = triage_result.get('risk_factors', '')
        risk_multiplier = 1.0
        if 'high' in risk_factors.lower() or 'critical' in risk_factors.lower():
            risk_multiplier = 1.5
        elif 'low' in risk_factors.lower() or 'minor' in risk_factors.lower():
            risk_multiplier = 0.8
        
        return base_score * confidence_multiplier * risk_multiplier
    
    def _get_patient_position(self, patient_id: str) -> int:
        # get patient position in queue
        for i, entry in enumerate(self.dashboard_data):
            if entry['patient_id'] == patient_id:
                return i + 1
        return -1
    
    def _generate_dashboard_summary(self) -> Dict[str, Any]:
        """Generate dashboard summary statistics"""
        if not self.dashboard_data:
            return {'total_patients': 0}
        
        triage_levels = [entry['triage_level'] for entry in self.dashboard_data]
        
        return {
            'total_patients': len(self.dashboard_data),
            'triage_distribution': {
                'level_1': len([t for t in triage_levels if t == 1]),
                'level_2': len([t for t in triage_levels if t == 2]),
                'level_3': len([t for t in triage_levels if t == 3]),
                'level_4': len([t for t in triage_levels if t == 4]),
                'level_5': len([t for t in triage_levels if t == 5])
            },
            'high_priority_patients': len([t for t in triage_levels if t <= 2]),
            'average_wait_time': self._calculate_average_wait_time()
        }
    
    def _calculate_average_wait_time(self) -> float:
        """Calculate average wait time based on queue position and triage levels"""
        if not self.patient_queue:
            return 0.0
        
        # Simplified calculation based on queue position and triage level
        # Higher priority patients wait less
        total_wait = 0.0
        count = 0
        
        for i, patient in enumerate(self.patient_queue):
            # Base wait time increases with queue position
            # But decreases with higher priority (lower triage level)
            base_wait = (i + 1) * 5  # 5 minutes per position
            priority_reduction = (6 - patient.get('triage_level', 3)) * 2  # Higher priority reduces wait
            estimated_wait = max(0, base_wait - priority_reduction)
            total_wait += estimated_wait
            count += 1
        
        return round(total_wait / count if count > 0 else 0.0, 1)
    
    def add_patient_to_queue(self, patient_data: Dict[str, Any], triage_result: Dict[str, Any]) -> None:
        """Add patient to priority queue"""
        if not patient_data or not isinstance(patient_data, dict):
            raise ValueError("patient_data must be a non-empty dictionary")
        
        if not triage_result or not isinstance(triage_result, dict):
            raise ValueError("triage_result must be a non-empty dictionary")
        
        queue_entry = {
            'patient_id': patient_data.get('patient_id'),
            'age': patient_data.get('age'),
            'gender': patient_data.get('gender'),
            'chief_complaint': patient_data.get('chief_complaint'),
            'triage_level': triage_result.get('triage_level', 3),
            'esi_level': Config.ESI_LEVELS.get(triage_result.get('triage_level', 3), 'Unknown'),
            'arrival_time': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat(),
            'status': 'waiting',
            'reasoning': triage_result.get('reasoning', ''),
            'risk_factors': triage_result.get('risk_factors', ''),
            'recommendations': triage_result.get('recommendations', ''),
            'confidence': triage_result.get('confidence', 0.5)
        }
        
        self.patient_queue.append(queue_entry)
        
        # sort by ESI level (lower = higher priority)
        self.patient_queue.sort(key=lambda x: (x['triage_level'], x['arrival_time']))
        
        # keep only recent ones
        if len(self.patient_queue) > 100:
            self.patient_queue = self.patient_queue[-100:]
    
    def remove_patient_from_queue(self, patient_id: str) -> bool:
        # remove patient from queue
        # TODO: add error handling here
        
        original_length = len(self.patient_queue)
        self.patient_queue = [p for p in self.patient_queue if p['patient_id'] != patient_id]
        return len(self.patient_queue) < original_length
    
    def replace_patient_in_queue(self, old_patient_id: str, new_patient_data: Dict[str, Any], new_triage_result: Dict[str, Any]) -> bool:
        # replace patient in queue
        # TODO: add validation here
        
        self.remove_patient_from_queue(old_patient_id)
        self.add_patient_to_queue(new_patient_data, new_triage_result)
        return True
    
    def get_sorted_patient_queue(self) -> List[Dict[str, Any]]:
        # get sorted queue
        # TODO: optimize this sorting
        
        self.patient_queue.sort(key=lambda x: (x['triage_level'], x['arrival_time']))
        return self.patient_queue.copy()

class SurveillanceTool(BaseTool):
    """Tool for analyzing cases for syndromic surveillance"""
    
    name = "surveillance_analysis"
    description = "analyze case for surveillance"
    
    def __init__(self, surveillance_system: SyndromicSurveillanceSystem):
        super().__init__()
        self.surveillance_system = surveillance_system
    
    def _run(self, case_data: Dict[str, Any]) -> str:
        # execute surveillance analysis
        # TODO: add more validation here
        
        try:
            result = self.surveillance_system.process_new_cases([case_data])
            
            output = {
                'case_id': case_data.get('patient_id'),
                'surveillance_result': result,
                'clusters_detected': result['clusters_detected'],
                'alerts_generated': result['alerts_generated'],
                'timestamp': datetime.now().isoformat()
            }
            
            return json.dumps(output, indent=2)
            
        except Exception as e:
            # print(f"debug: surveillance error: {e}")  # had this for debugging
            return json.dumps({
                'error': str(e),
                'case_id': case_data.get('patient_id'),
                'timestamp': datetime.now().isoformat()
            })

class TriageCallbackHandler(BaseCallbackHandler):
    # callback handler - copied this from langchain tutorial
    # TODO: add more functionality to this handler
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        # called when llm starts
        # print("debug: LLM started")  # had this for debugging
        pass
    
    def on_llm_end(self, response, **kwargs) -> None:
        # called when llm ends
        # print("debug: LLM ended")  # had this for debugging
        pass
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        # called when tool starts
        # print("debug: Tool started")  # had this for debugging
        pass
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        # called when tool ends
        # print("debug: Tool ended")  # had this for debugging
        pass

class TriageAgent:
    """
    Main Triage Agent using LangChain ReAct agent pattern.
    
    Orchestrates triage classification, dashboard updates, and surveillance analysis.
    """
    
    def __init__(self):
        # initialize systems
        self.rag_system = RAGSystem()
        self.surveillance_system = SyndromicSurveillanceSystem()
        self.surveillance_system.initialize()
        
        # initialize tools
        self.triage_tool = TriageTool(self.rag_system)
        self.dashboard_tool = DashboardUpdateTool()
        self.surveillance_tool = SurveillanceTool(self.surveillance_system)
        
        # create tools list
        self.tools = [
            self.triage_tool,
            self.dashboard_tool,
            self.surveillance_tool
        ]
        
        # create agent
        self.agent = self._create_agent()
        
    
    def _create_agent(self) -> AgentExecutor:
        # create the react agent - learned this from langchain docs
        # TODO: ask professor about this prompt
        
        prompt_template = """
You are an AI-powered triage assistant for emergency departments. Your role is to help nurses prioritize patients and assist epidemiologists with surveillance.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        # create callback manager
        callback_manager = CallbackManager([TriageCallbackHandler()])
        
        # create the agent
        agent = create_react_agent(
            llm=self.rag_system.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            callback_manager=callback_manager,
            max_iterations=5,  # max iterations
            early_stopping_method="generate"
        )
        
        return agent_executor
    
    def process_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single patient through the complete triage workflow.
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            Dictionary with processing results including triage classification
        """
        if not patient_data or not isinstance(patient_data, dict):
            raise ValueError("patient_data must be a non-empty dictionary")
        
        try:
            # create input for agent
            agent_input = f"""
Process this patient for triage and surveillance:

Patient ID: {patient_data.get('patient_id', 'unknown')}
Age: {patient_data.get('age', 'unknown')}
Gender: {patient_data.get('gender', 'unknown')}
Chief Complaint: {patient_data.get('chief_complaint', 'not specified')}
Vital Signs: Heart Rate: {patient_data.get('heart_rate', 'N/A')}, 
Respiratory Rate: {patient_data.get('respiratory_rate', 'N/A')}, 
Oxygen Saturation: {patient_data.get('oxygen_saturation', 'N/A')}, 
Temperature: {patient_data.get('temperature', 'N/A')}, 
Blood Pressure: {patient_data.get('blood_pressure', 'N/A')}, 
Pain Level: {patient_data.get('pain_level', 'N/A')}

Please:
1. Classify the patient's triage level using the patient_triage tool
2. Update the dashboard with the triage result using the update_dashboard tool
3. Analyze the case for surveillance using the surveillance_analysis tool

Provide a comprehensive summary of the patient's triage level, priority, and any surveillance alerts.
"""
            
            # execute the agent
            result = self.agent.invoke({"input": agent_input})
            
            # also add patient to queue directly
            triage_result = self.rag_system.classify_patient(patient_data)
            self.dashboard_tool.add_patient_to_queue(patient_data, triage_result)
            
            return {
                'patient_id': patient_data.get('patient_id'),
                'agent_response': result.get('output', ''),
                'triage_result': triage_result,
                'processing_status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # print(f"debug: error processing patient: {e}")  # had this for debugging
            return {
                'patient_id': patient_data.get('patient_id'),
                'error': str(e),
                'processing_status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def batch_process_patients(self, patients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # process multiple patients
        # TODO: optimize this with parallel processing
        
        results = []
        for patient in patients:
            result = self.process_patient(patient)
            results.append(result)
        
        return results
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        # get dashboard data
        # TODO: add caching here
        
        summary = self.dashboard_tool._generate_dashboard_summary()
        summary['queue'] = self.dashboard_tool.get_sorted_patient_queue()
        return summary
    
    def get_surveillance_data(self) -> Dict[str, Any]:
        # get surveillance data
        return self.surveillance_system.get_dashboard_data()
    
    def get_agent_status(self) -> Dict[str, Any]:
        # get agent status
        # TODO: add more status information
        
        return {
            'agent_status': 'active',
            'tools_available': len(self.tools),
            'rag_system_status': 'active' if self.rag_system else 'inactive',
            'surveillance_system_status': 'active' if self.surveillance_system else 'inactive',
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_surveillance(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze case for surveillance patterns"""
        try:
            result = self.surveillance_system.process_new_cases([case_data])
            return {
                'case_id': case_data.get('patient_id'),
                'surveillance_result': result,
                'clusters_detected': result.get('clusters_detected', 0),
                'alerts_generated': result.get('alerts_generated', 0),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'case_id': case_data.get('patient_id'),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_dashboard(self, patient_data: Dict[str, Any], triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard with patient information"""
        try:
            timestamp = datetime.now().isoformat()
            result = self.dashboard_tool._run(
                patient_data.get('patient_id', ''),
                triage_result,
                timestamp
            )
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'patient_id': patient_data.get('patient_id', ''),
                'timestamp': datetime.now().isoformat()
            }

if __name__ == "__main__":
    # test the triage agent
    # TODO: add more comprehensive tests
    
    agent = TriageAgent()
    
    # sample patient data
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
    print("Agent Processing Result:")
    print(json.dumps(result, indent=2))
    
    # get dashboard data
    dashboard_data = agent.get_dashboard_data()
    print("\nDashboard Data:")
    print(json.dumps(dashboard_data, indent=2))
    
    # get surveillance data
    surveillance_data = agent.get_surveillance_data()
    print("\nSurveillance Data:")
    print(json.dumps(surveillance_data, indent=2))
