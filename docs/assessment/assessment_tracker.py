#!/usr/bin/env python3
"""
AI Hospital OS - Project Assessment Tracker
Tracks progress through the 5-phase improvement process
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys

class AssessmentTracker:
    """Track progress through assessment phases"""
    
    PHASES = [
        "01_as_is_analysis",
        "02_gap_analysis",
        "03_root_cause_analysis",
        "04_solution_design",
        "05_roadmap"
    ]
    
    PHASE_NAMES = {
        "01_as_is_analysis": "As-Is Analysis",
        "02_gap_analysis": "Gap Analysis",
        "03_root_cause_analysis": "Root Cause Analysis",
        "04_solution_design": "Solution Design",
        "05_roadmap": "Roadmap & Execution Plan"
    }
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
        
        self.progress_file = self.base_path / "progress.json"
        self.load_progress()
    
    def load_progress(self):
        """Load progress from JSON file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "phases": {phase: {"status": "not_started", "completion": 0} for phase in self.PHASES},
                "milestones": {},
                "tasks": [],
                "risks": [],
                "last_updated": None
            }
    
    def save_progress(self):
        """Save progress to JSON file"""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def update_phase(self, phase: str, status: str, completion: int):
        """Update phase status and completion percentage"""
        if phase not in self.PHASES:
            print(f"❌ Invalid phase: {phase}")
            return
        
        self.progress["phases"][phase] = {
            "status": status,
            "completion": completion,
            "updated": datetime.now().isoformat()
        }
        self.save_progress()
        print(f"✅ Updated {self.PHASE_NAMES[phase]}: {status} ({completion}%)")
    
    def add_milestone(self, name: str, description: str, target_date: str, status: str = "pending"):
        """Add a project milestone"""
        milestone_id = f"M{len(self.progress['milestones']) + 1}"
        self.progress["milestones"][milestone_id] = {
            "name": name,
            "description": description,
            "target_date": target_date,
            "status": status,
            "created": datetime.now().isoformat()
        }
        self.save_progress()
        print(f"✅ Added milestone {milestone_id}: {name}")
    
    def add_task(self, title: str, phase: str, priority: str = "medium", assignee: str = ""):
        """Add a task to the tracker"""
        task = {
            "id": f"T{len(self.progress['tasks']) + 1}",
            "title": title,
            "phase": phase,
            "priority": priority,
            "assignee": assignee,
            "status": "todo",
            "created": datetime.now().isoformat()
        }
        self.progress["tasks"].append(task)
        self.save_progress()
        print(f"✅ Added task {task['id']}: {title}")
    
    def add_risk(self, title: str, severity: str, mitigation: str):
        """Add a risk to track"""
        risk = {
            "id": f"R{len(self.progress['risks']) + 1}",
            "title": title,
            "severity": severity,
            "mitigation": mitigation,
            "status": "open",
            "created": datetime.now().isoformat()
        }
        self.progress["risks"].append(risk)
        self.save_progress()
        print(f"✅ Added risk {risk['id']}: {title}")
    
    def show_status(self):
        """Display current project status"""
        print("\n" + "=" * 70)
        print("AI HOSPITAL OS - ASSESSMENT TRACKER")
        print("=" * 70)
        
        # Overall Progress
        total_completion = sum(p["completion"] for p in self.progress["phases"].values()) / len(self.PHASES)
        print(f"\n📊 Overall Progress: {total_completion:.1f}%")
        print(f"🕐 Last Updated: {self.progress['last_updated'] or 'Never'}")
        
        # Phase Status
        print("\n📋 PHASE STATUS:")
        print("-" * 70)
        for phase in self.PHASES:
            data = self.progress["phases"][phase]
            status_icon = {
                "not_started": "⚪",
                "in_progress": "🔵",
                "completed": "✅",
                "blocked": "🔴"
            }.get(data["status"], "❓")
            
            bar_length = 20
            filled = int(bar_length * data["completion"] / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"{status_icon} {self.PHASE_NAMES[phase]:<30} [{bar}] {data['completion']:3}%")
        
        # Milestones
        if self.progress["milestones"]:
            print("\n🎯 MILESTONES:")
            print("-" * 70)
            for mid, milestone in self.progress["milestones"].items():
                status_icon = {"pending": "⏳", "achieved": "✅", "missed": "❌"}.get(milestone["status"], "❓")
                print(f"{status_icon} {mid}: {milestone['name']}")
                print(f"   Target: {milestone['target_date']} | Status: {milestone['status']}")
        
        # Active Tasks
        active_tasks = [t for t in self.progress["tasks"] if t["status"] != "done"]
        if active_tasks:
            print(f"\n✅ ACTIVE TASKS ({len(active_tasks)}):")
            print("-" * 70)
            for task in active_tasks[:5]:  # Show top 5
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
                print(f"{priority_icon} {task['id']}: {task['title']}")
                print(f"   Phase: {self.PHASE_NAMES.get(task['phase'], 'General')} | Assignee: {task['assignee'] or 'Unassigned'}")
        
        # Open Risks
        open_risks = [r for r in self.progress["risks"] if r["status"] == "open"]
        if open_risks:
            print(f"\n⚠️  OPEN RISKS ({len(open_risks)}):")
            print("-" * 70)
            for risk in open_risks:
                severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(risk["severity"], "⚪")
                print(f"{severity_icon} {risk['id']}: {risk['title']}")
                print(f"   Mitigation: {risk['mitigation']}")
        
        print("\n" + "=" * 70 + "\n")
    
    def generate_report(self, output_file: Optional[str] = None):
        """Generate a detailed status report"""
        report_lines = []
        report_lines.append("# AI Hospital OS - Assessment Progress Report")
        report_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\n**Last Updated:** {self.progress['last_updated'] or 'Never'}")
        
        # Summary
        total_completion = sum(p["completion"] for p in self.progress["phases"].values()) / len(self.PHASES)
        report_lines.append(f"\n## Executive Summary\n")
        report_lines.append(f"- **Overall Progress:** {total_completion:.1f}%")
        report_lines.append(f"- **Phases Completed:** {sum(1 for p in self.progress['phases'].values() if p['status'] == 'completed')}/{len(self.PHASES)}")
        report_lines.append(f"- **Active Tasks:** {sum(1 for t in self.progress['tasks'] if t['status'] != 'done')}")
        report_lines.append(f"- **Open Risks:** {sum(1 for r in self.progress['risks'] if r['status'] == 'open')}")
        
        # Phase Details
        report_lines.append("\n## Phase Progress\n")
        for phase in self.PHASES:
            data = self.progress["phases"][phase]
            status_emoji = {
                "not_started": "⚪",
                "in_progress": "🔵",
                "completed": "✅",
                "blocked": "🔴"
            }.get(data["status"], "❓")
            
            report_lines.append(f"### {status_emoji} {self.PHASE_NAMES[phase]}")
            report_lines.append(f"- **Status:** {data['status']}")
            report_lines.append(f"- **Completion:** {data['completion']}%")
            report_lines.append("")
        
        # Milestones
        if self.progress["milestones"]:
            report_lines.append("\n## Milestones\n")
            for mid, milestone in self.progress["milestones"].items():
                status_emoji = {"pending": "⏳", "achieved": "✅", "missed": "❌"}.get(milestone["status"], "❓")
                report_lines.append(f"### {status_emoji} {mid}: {milestone['name']}")
                report_lines.append(f"- **Description:** {milestone['description']}")
                report_lines.append(f"- **Target Date:** {milestone['target_date']}")
                report_lines.append(f"- **Status:** {milestone['status']}")
                report_lines.append("")
        
        # Tasks
        if self.progress["tasks"]:
            report_lines.append("\n## Tasks\n")
            for status in ["todo", "in_progress", "done"]:
                tasks = [t for t in self.progress["tasks"] if t["status"] == status]
                if tasks:
                    report_lines.append(f"\n### {status.replace('_', ' ').title()} ({len(tasks)})\n")
                    for task in tasks:
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
                        report_lines.append(f"- {priority_emoji} **{task['id']}:** {task['title']}")
                        report_lines.append(f"  - Phase: {self.PHASE_NAMES.get(task['phase'], 'General')}")
                        report_lines.append(f"  - Assignee: {task['assignee'] or 'Unassigned'}")
        
        # Risks
        if self.progress["risks"]:
            report_lines.append("\n## Risks\n")
            for severity in ["critical", "high", "medium", "low"]:
                risks = [r for r in self.progress["risks"] if r["severity"] == severity and r["status"] == "open"]
                if risks:
                    report_lines.append(f"\n### {severity.title()} Severity ({len(risks)})\n")
                    for risk in risks:
                        report_lines.append(f"- **{risk['id']}:** {risk['title']}")
                        report_lines.append(f"  - Mitigation: {risk['mitigation']}")
                        report_lines.append(f"  - Status: {risk['status']}")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Report saved to {output_file}")
        else:
            print(report)
    
    def initialize_standard_milestones(self):
        """Initialize standard milestones from roadmap"""
        milestones = [
            ("M1: Code Runs", "All tests passing, API starts successfully", "Week 2"),
            ("M2: Pipeline Works", "End-to-end classification functional", "Week 4"),
            ("M3: Deployed Locally", "Docker deployment successful", "Week 6"),
            ("M4: Auth Works", "Authentication & authorization implemented", "Week 8"),
            ("M5: HIPAA Baseline", "Security controls in place", "Week 10"),
            ("M6: Production Deploy", "Cloud deployment complete", "Week 12"),
            ("M7: Production Ready", "All testing complete, ready to launch", "Week 14"),
            ("M8: Real Data", "MIMIC data integrated", "Week 17"),
            ("M9: Full Features", "All features complete", "Week 19"),
            ("M10: Production Live", "System live in production", "Week 20"),
        ]
        
        for name, desc, target in milestones:
            self.add_milestone(name, desc, target)


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Hospital OS Assessment Tracker")
    parser.add_argument("--init", action="store_true", help="Initialize tracker with standard milestones")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--report", type=str, help="Generate report (optional: output file)")
    parser.add_argument("--update-phase", nargs=3, metavar=("PHASE", "STATUS", "COMPLETION"), 
                       help="Update phase (e.g., 01_as_is_analysis in_progress 50)")
    parser.add_argument("--add-task", nargs="+", metavar="ARG",
                       help="Add task (e.g., 'Fix tests' 01_as_is_analysis high)")
    parser.add_argument("--add-risk", nargs="+", metavar="ARG",
                       help="Add risk (e.g., 'Model won\\'t load' critical 'Use smaller model')")
    
    args = parser.parse_args()
    
    tracker = AssessmentTracker()
    
    if args.init:
        print("🚀 Initializing assessment tracker...")
        tracker.initialize_standard_milestones()
        print("✅ Standard milestones added")
    
    if args.update_phase:
        phase, status, completion = args.update_phase
        tracker.update_phase(phase, status, int(completion))
    
    if args.add_task:
        title = " ".join(args.add_task[:-2])
        phase = args.add_task[-2]
        priority = args.add_task[-1]
        tracker.add_task(title, phase, priority)
    
    if args.add_risk:
        # Parse risk arguments (last two are severity and mitigation)
        title = " ".join(args.add_risk[:-2])
        severity = args.add_risk[-2]
        mitigation = args.add_risk[-1]
        tracker.add_risk(title, severity, mitigation)
    
    if args.report is not None:
        output_file = args.report if args.report else None
        tracker.generate_report(output_file)
    
    if args.status or len(sys.argv) == 1:
        tracker.show_status()


if __name__ == "__main__":
    main()
