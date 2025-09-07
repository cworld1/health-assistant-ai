"""
Health Assistant AI - Core Module

This module provides the main entry point for the Health Assistant AI system,
offering intelligent health consultation, symptom analysis, medication guidance,
and wellness management services.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0
"""

from .medical import SymptomAnalyzer, MedicationChecker, EmergencyResponse
from .wellness import NutritionPlanner, FitnessTracker, MentalWellness
from .core import HealthConsultant, HealthDatabase, PrivacyManager
from .utils import HealthLogger, DataValidator, SecurityUtils

__version__ = "1.0.0"
__author__ = "Health Assistant AI Team"
__email__ = "team@health-assistant-ai.org"
__license__ = "Apache-2.0"

# Core health services
__all__ = [
    # Medical services
    "SymptomAnalyzer",
    "MedicationChecker", 
    "EmergencyResponse",
    
    # Wellness services
    "NutritionPlanner",
    "FitnessTracker",
    "MentalWellness",
    
    # Core systems
    "HealthConsultant",
    "HealthDatabase",
    "PrivacyManager",
    
    # Utilities
    "HealthLogger",
    "DataValidator",
    "SecurityUtils",
]

# Medical disclaimer
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
    """Get the current version of Health Assistant AI."""
    return __version__

def show_disclaimer():
    """Display the medical disclaimer."""
    print(MEDICAL_DISCLAIMER)

def get_health_consultant():
    """Get a configured Health Consultant instance."""
    return HealthConsultant()
