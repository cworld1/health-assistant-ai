"""
Health Assistant AI - Agent Module

This module provides specialized AI agents for health consultation, medical analysis,
and wellness management. Each agent is designed for specific health-related tasks
with appropriate safety measures and medical compliance features.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0
"""

from .base import HealthAgent
from .react_agent import MedicalReactAgent, WellnessReactAgent
from .reasoning_agent import MedicalReasoningAgent, DiagnosticAgent
from .tool_calling_agent import SymptomAnalysisAgent, MedicationAgent
from .register import register_health_agents

# Core health agents
__all__ = [
    "HealthAgent",
    "MedicalAgent",
    "WellnessAgent",
    "MedicalReactAgent",
    "WellnessReactAgent",
    "MedicalReasoningAgent",
    "DiagnosticAgent",
    "SymptomAnalysisAgent",
    "MedicationAgent",
    "register_health_agents",
]

# Alias for convenience
MedicalAgent = MedicalReactAgent
WellnessAgent = WellnessReactAgent
