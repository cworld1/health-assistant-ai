"""
Health Assistant Toolkit (HAT) - Core Module

This module provides the main entry point for the Health Assistant Toolkit,
a comprehensive AI-powered health consultation platform offering intelligent
symptom analysis, medication guidance, and wellness management services.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0

MEDICAL DISCLAIMER: This system provides health information and educational
content only. It is not intended to replace professional medical advice,
diagnosis, or treatment. Always consult with qualified healthcare providers
for medical concerns.
"""

from .agent import HealthAgent, MedicalAgent, WellnessAgent
from .llm import HealthLLM, MedicalLLM
from .tool import (
    SymptomAnalyzerTool,
    MedicationCheckerTool,
    NutritionPlannerTool,
    FitnessTrackerTool,
    EmergencyResponseTool,
)
from .retriever import MedicalKnowledgeRetriever, HealthDataRetriever
from .embedder import MedicalEmbedder, HealthEmbedder
from .memory import HealthMemory, PatientHistoryMemory
from .observability import HealthMetrics, MedicalAuditLogger
from .runtime import HealthRuntime, ConsultationRuntime
from .settings import HealthSettings, MedicalSettings

__version__ = "1.0.0"
__author__ = "Health Assistant AI Team"
__email__ = "team@health-assistant-ai.org"
__license__ = "Apache-2.0"
__copyright__ = "Copyright (c) 2024-2025, Health Assistant AI Project"

# Core health services
__all__ = [
    # Core agents
    "HealthAgent",
    "MedicalAgent",
    "WellnessAgent",
    # LLM services
    "HealthLLM",
    "MedicalLLM",
    # Health tools
    "SymptomAnalyzerTool",
    "MedicationCheckerTool",
    "NutritionPlannerTool",
    "FitnessTrackerTool",
    "EmergencyResponseTool",
    # Data retrieval
    "MedicalKnowledgeRetriever",
    "HealthDataRetriever",
    # Embeddings
    "MedicalEmbedder",
    "HealthEmbedder",
    # Memory systems
    "HealthMemory",
    "PatientHistoryMemory",
    # Observability
    "HealthMetrics",
    "MedicalAuditLogger",
    # Runtime
    "HealthRuntime",
    "ConsultationRuntime",
    # Settings
    "HealthSettings",
    "MedicalSettings",
]

# Medical disclaimer for health services
MEDICAL_DISCLAIMER = """
IMPORTANT MEDICAL DISCLAIMER:

This Health Assistant AI system provides health information and educational content only.
It is not intended to replace professional medical advice, diagnosis, or treatment.

- Always consult with qualified healthcare providers for medical concerns
- Never ignore professional medical advice because of information from this system
- In case of emergency, contact your local emergency services immediately
- This system cannot diagnose medical conditions or prescribe treatments
- Individual health needs vary - personalized medical care is essential

By using this system, you acknowledge that you understand these limitations
and will seek appropriate professional medical care when needed.
"""


def get_version():
    """Get the current version of Health Assistant Toolkit."""
    return __version__


def show_medical_disclaimer():
    """Display the medical disclaimer."""
    print(MEDICAL_DISCLAIMER)


def get_health_agent():
    """Get a configured Health Agent instance."""
    return HealthAgent()


def get_medical_agent():
    """Get a configured Medical Agent instance."""
    return MedicalAgent()


def get_wellness_agent():
    """Get a configured Wellness Agent instance."""
    return WellnessAgent()
