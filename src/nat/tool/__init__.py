"""
Health Assistant AI - Tool Module

This module provides specialized health-focused tools for medical analysis,
symptom checking, medication guidance, wellness tracking, and emergency response.
All tools are designed with medical safety and compliance in mind.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0
"""

from .symptom_analyzer import SymptomAnalyzerTool
from .medication_checker import MedicationCheckerTool
from .nutrition_planner import NutritionPlannerTool
from .fitness_tracker import FitnessTrackerTool
from .emergency_response import EmergencyResponseTool
from .health_monitor import HealthMonitorTool
from .mental_wellness import MentalWellnessTool
from .medical_knowledge import MedicalKnowledgeTool
from .vital_signs import VitalSignsTool
from .telemedicine import TelemedicineTool
from .register import register_health_tools

# Legacy imports for backward compatibility
from .document_search import DocumentSearchTool
from .datetime_tools import DateTimeTool
from .retriever import RetrieverTool
from .nvidia_rag import NvidiaRAGTool

__all__ = [
    # Primary health tools
    "SymptomAnalyzerTool",
    "MedicationCheckerTool", 
    "NutritionPlannerTool",
    "FitnessTrackerTool",
    "EmergencyResponseTool",
    "HealthMonitorTool",
    "MentalWellnessTool",
    "MedicalKnowledgeTool",
    "VitalSignsTool",
    "TelemedicineTool",
    # Tool registration
    "register_health_tools",
    # Legacy tools
    "DocumentSearchTool",
    "DateTimeTool", 
    "RetrieverTool",
    "NvidiaRAGTool",
]