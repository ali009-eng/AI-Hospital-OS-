# surveillance system - learned from scikit docs
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime, timedelta
import sqlite3
from config import Config
from utils.db_pool import get_db_connection

class SyndromicSurveillanceSystem:
    def __init__(self):
        """Initialize syndromic surveillance system"""
        self.db_path = "triage_surveillance.db"
        self.vectorizer = TfidfVectorizer(max_features=Config.TFIDF_MAX_FEATURES)
        self.clusterer = DBSCAN(eps=0.5, min_samples=Config.CLUSTER_MIN_SIZE)
    
    def process_new_cases(self, cases):
        """
        Process new cases for surveillance analysis
        
        Args:
            cases: List of case dictionaries
            
        Returns:
            Dictionary with clusters and alerts
        """
        if not cases:
            return {'clusters_detected': 0, 'alerts_generated': 0, 'clusters': [], 'alerts': []}
        
        if not isinstance(cases, list):
            cases = [cases] if isinstance(cases, dict) else []
        
        try:
            # store cases
            stored_count = self._store_cases(cases)
            
            # analyze for clusters
            clusters = self._detect_clusters()
            
            # check for outbreaks
            alerts = self._check_outbreaks()
            
            return {
                'processed_cases': stored_count,
                'clusters_detected': len(clusters),
                'alerts_generated': len(alerts),
                'clusters': clusters,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error processing cases: {e}")
            return {
                'processed_cases': 0,
                'clusters_detected': 0,
                'alerts_generated': 0,
                'clusters': [],
                'alerts': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _store_cases(self, cases) -> int:
        """
        Store cases in database
        
        Returns:
            Number of cases successfully stored
        """
        if not cases:
            return 0
        
        stored_count = 0
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # create table if not exists (with extended schema)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    symptoms TEXT,
                    timestamp TEXT,
                    triage_level INTEGER,
                    age INTEGER,
                    gender TEXT,
                    chief_complaint TEXT
                )
            ''')
            
            for case in cases:
                if not isinstance(case, dict):
                    continue
                
                try:
                    cursor.execute('''
                        INSERT INTO cases (patient_id, symptoms, timestamp, triage_level, age, gender, chief_complaint)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        case.get('patient_id', ''),
                        case.get('chief_complaint', '') or case.get('symptoms', ''),
                        case.get('timestamp') or datetime.now().isoformat(),
                        case.get('triage_level', 3),
                        case.get('age'),
                        case.get('gender', ''),
                        case.get('chief_complaint', '')
                    ))
                    stored_count += 1
                except Exception as e:
                    print(f"Error storing case {case.get('patient_id', 'unknown')}: {e}")
                    continue
                # Commit handled by context manager
        except Exception as e:
            print(f"Error in _store_cases: {e}")
        
        return stored_count
    
    def _detect_clusters(self):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # get recent cases
                recent_time = datetime.now() - timedelta(hours=Config.SURVEILLANCE_WINDOW_HOURS)
                cursor.execute('''
                    SELECT symptoms FROM cases 
                    WHERE timestamp > ?
                ''', (recent_time.isoformat(),))
                
                symptoms = [row[0] for row in cursor.fetchall()]
            
            if len(symptoms) < 2:
                return []
            
            # vectorize symptoms
            X = self.vectorizer.fit_transform(symptoms)
            
            # cluster
            clusters = self.clusterer.fit_predict(X)
            
            # return cluster info
            unique_clusters = set(clusters)
            cluster_info = []
            for cluster_id in unique_clusters:
                if cluster_id != -1:  # ignore noise
                    cluster_cases = [symptoms[i] for i, c in enumerate(clusters) if c == cluster_id]
                    cluster_info.append({
                        'cluster_id': cluster_id,
                        'size': len(cluster_cases),
                        'symptoms': cluster_cases[:5]  # first 5 symptoms
                    })
            
            return cluster_info
        except:
            return []
    
    def _check_outbreaks(self):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # get recent high-priority cases
                recent_time = datetime.now() - timedelta(hours=Config.SURVEILLANCE_WINDOW_HOURS)
                cursor.execute('''
                    SELECT COUNT(*) FROM cases 
                    WHERE timestamp > ? AND triage_level <= 2
                ''', (recent_time.isoformat(),))
                
                high_priority_count = cursor.fetchone()[0]
            
            alerts = []
            if high_priority_count > Config.OUTBREAK_THRESHOLD * 10:  # threshold check
                alerts.append({
                    'alert_type': 'High Priority Spike',
                    'description': f'{high_priority_count} high priority cases in last {Config.SURVEILLANCE_WINDOW_HOURS} hours',
                    'severity': 'High',
                    'affected_patients': high_priority_count,
                    'recommendations': ['Increase staffing', 'Review triage protocols']
                })
            
            return alerts
        except:
            return []
    
    def get_active_alerts(self):
        return self._check_outbreaks()
    
    def initialize(self):
        """Initialize surveillance system and database"""
        try:
            # Ensure database exists with proper schema
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id TEXT,
                        symptoms TEXT,
                        timestamp TEXT,
                        triage_level INTEGER,
                        age INTEGER,
                        gender TEXT,
                        chief_complaint TEXT
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON cases(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_triage_level ON cases(triage_level)
                ''')
                # Commit handled by context manager
            return True
        except Exception as e:
            print(f"Error initializing surveillance system: {e}")
            return False
    
    def get_symptom_trends(self):
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # get daily counts for last 7 days
                trends = []
                for i in range(7):
                    date = datetime.now() - timedelta(days=i)
                    start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_time = start_time + timedelta(days=1)
                    
                    cursor.execute('''
                        SELECT COUNT(*) FROM cases 
                        WHERE timestamp BETWEEN ? AND ?
                    ''', (start_time.isoformat(), end_time.isoformat()))
                    
                    daily_cases = cursor.fetchone()[0]
                    
                    # Get high priority cases
                    cursor.execute('''
                        SELECT COUNT(*) FROM cases 
                        WHERE timestamp BETWEEN ? AND ? AND triage_level <= 2
                    ''', (start_time.isoformat(), end_time.isoformat()))
                    
                    high_priority_cases = cursor.fetchone()[0]
                    
                    trends.append({
                        'date': date.isoformat(),
                        'daily_cases': daily_cases,
                        'high_priority_cases': high_priority_cases
                    })
            return trends
        except Exception as e:
            print(f"Error getting symptom trends: {e}")
            return []
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive surveillance data for dashboard"""
        try:
            alerts = self.get_active_alerts()
            trends = self.get_symptom_trends()
            clusters = self._detect_clusters()
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get recent statistics
                recent_time = datetime.now() - timedelta(hours=Config.SURVEILLANCE_WINDOW_HOURS)
                
                # Total cases in window
                cursor.execute('''
                    SELECT COUNT(*) FROM cases 
                    WHERE timestamp > ?
                ''', (recent_time.isoformat(),))
                total_recent = cursor.fetchone()[0]
                
                # High priority cases
                cursor.execute('''
                    SELECT COUNT(*) FROM cases 
                    WHERE timestamp > ? AND triage_level <= 2
                ''', (recent_time.isoformat(),))
                high_priority_recent = cursor.fetchone()[0]
                
                # Average triage level
                cursor.execute('''
                    SELECT AVG(triage_level) FROM cases 
                    WHERE timestamp > ?
                ''', (recent_time.isoformat(),))
                avg_triage_result = cursor.fetchone()[0]
                avg_triage = float(avg_triage_result) if avg_triage_result else 3.0
            
            return {
                'alerts': alerts,
                'trends': trends,
                'clusters': clusters,
                'recent_stats': {
                    'total_cases': total_recent,
                    'high_priority_cases': high_priority_recent,
                    'average_triage_level': round(avg_triage, 2),
                    'window_hours': Config.SURVEILLANCE_WINDOW_HOURS
                },
                'clusters_detected': len(clusters),
                'active_alerts_count': len(alerts),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return {
                'alerts': [],
                'trends': [],
                'clusters': [],
                'recent_stats': {
                    'total_cases': 0,
                    'high_priority_cases': 0,
                    'average_triage_level': 3.0,
                    'window_hours': Config.SURVEILLANCE_WINDOW_HOURS
                },
                'clusters_detected': 0,
                'active_alerts_count': 0,
                'timestamp': datetime.now().isoformat()
            }