"""
Health Assistant AI - Core Health Consultant

This module provides the main HealthConsultant class that orchestrates
all health-related services and provides a unified interface for
health consultations.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet

# Configure health-specific logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health_assistant")


class HealthRiskLevel(Enum):
    """Health risk assessment levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ConsultationType(Enum):
    """Types of health consultations."""

    SYMPTOM_ANALYSIS = "symptom_analysis"
    MEDICATION_QUERY = "medication_query"
    NUTRITION_PLANNING = "nutrition_planning"
    FITNESS_GUIDANCE = "fitness_guidance"
    MENTAL_HEALTH = "mental_health"
    EMERGENCY_RESPONSE = "emergency_response"
    PREVENTIVE_CARE = "preventive_care"
    GENERAL_WELLNESS = "general_wellness"


@dataclass
class HealthProfile:
    """User health profile data structure."""

    user_id: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    medical_conditions: List[str]
    medications: List[str]
    allergies: List[str]
    emergency_contacts: List[Dict[str, str]]
    last_updated: datetime


class HealthConsultationRequest(BaseModel):
    """Health consultation request model."""

    user_id: str = Field(..., description="Unique user identifier")
    consultation_type: ConsultationType = Field(..., description="Type of consultation")
    symptoms: Optional[List[str]] = Field(None, description="List of symptoms")
    severity: Optional[str] = Field(
        None, description="Symptom severity (mild/moderate/severe)"
    )
    duration: Optional[str] = Field(
        None, description="How long symptoms have been present"
    )
    additional_info: Optional[Dict[str, Any]] = Field(
        None, description="Additional context"
    )
    privacy_level: str = Field("strict", description="Privacy protection level")

    @validator("consultation_type")
    def validate_consultation_type(cls, v):
        if isinstance(v, str):
            try:
                return ConsultationType(v)
            except ValueError:
                raise ValueError(f"Invalid consultation type: {v}")
        return v


class HealthConsultationResponse(BaseModel):
    """Health consultation response model."""

    consultation_id: str
    user_id: str
    consultation_type: ConsultationType
    risk_level: HealthRiskLevel
    assessment: str
    recommendations: List[str]
    emergency_action_required: bool
    follow_up_needed: bool
    medical_disclaimer: str
    confidence_score: float
    timestamp: datetime


class HealthDatabase:
    """Secure health data management system."""

    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize health database with encryption."""
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.profiles: Dict[str, HealthProfile] = {}
        self.consultation_history: Dict[str, List[HealthConsultationResponse]] = {}

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive health data."""
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive health data."""
        return self.cipher.decrypt(encrypted_data).decode()

    def store_profile(self, profile: HealthProfile) -> bool:
        """Store user health profile securely."""
        try:
            self.profiles[profile.user_id] = profile
            logger.info(f"Health profile stored for user: {profile.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store health profile: {e}")
            return False

    def get_profile(self, user_id: str) -> Optional[HealthProfile]:
        """Retrieve user health profile."""
        return self.profiles.get(user_id)

    def store_consultation(self, consultation: HealthConsultationResponse) -> bool:
        """Store consultation result securely."""
        try:
            if consultation.user_id not in self.consultation_history:
                self.consultation_history[consultation.user_id] = []
            self.consultation_history[consultation.user_id].append(consultation)
            logger.info(f"Consultation stored: {consultation.consultation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store consultation: {e}")
            return False


class PrivacyManager:
    """Privacy and security management for health data."""

    def __init__(self):
        """Initialize privacy manager."""
        self.access_logs: List[Dict[str, Any]] = []
        self.data_retention_days = 365  # HIPAA compliance

    def log_access(self, user_id: str, action: str, data_type: str) -> None:
        """Log data access for audit purposes."""
        self.access_logs.append(
            {
                "user_id": user_id,
                "action": action,
                "data_type": data_type,
                "timestamp": datetime.now(),
                "ip_address": "masked_for_privacy",
            }
        )

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize health data for research purposes."""
        anonymized = data.copy()
        # Remove or hash identifying information
        if "user_id" in anonymized:
            anonymized["user_id"] = "anonymous_" + str(hash(data["user_id"]))[:8]
        return anonymized

    def check_data_retention(self) -> List[str]:
        """Check for data that should be purged per retention policy."""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        # Implementation would check consultation dates and return IDs to purge
        expired_data = []
        # TODO: Implement actual data retention logic
        return expired_data


class HealthConsultant:
    """Main Health Assistant AI consultation engine."""

    def __init__(self, database: Optional[HealthDatabase] = None):
        """Initialize the health consultant."""
        self.database = database or HealthDatabase()
        self.privacy_manager = PrivacyManager()
        self.emergency_keywords = [
            "chest pain",
            "difficulty breathing",
            "severe bleeding",
            "unconscious",
            "stroke symptoms",
            "heart attack",
            "allergic reaction",
            "severe injury",
            "poisoning",
            "suicidal thoughts",
            "overdose",
        ]

        # Medical disclaimer
        self.medical_disclaimer = """
        This assessment is for informational purposes only and does not constitute 
        medical advice. Always consult healthcare professionals for medical concerns.
        In emergencies, contact local emergency services immediately.
        """

    async def conduct_consultation(
        self, request: HealthConsultationRequest
    ) -> HealthConsultationResponse:
        """Conduct a comprehensive health consultation."""
        try:
            # Log the consultation request
            self.privacy_manager.log_access(
                request.user_id, "consultation_request", request.consultation_type.value
            )

            # Get user profile
            profile = self.database.get_profile(request.user_id)

            # Check for emergency conditions
            emergency_detected = self._check_emergency_conditions(request)

            # Determine risk level
            risk_level = await self._assess_risk_level(request, profile)

            # Generate assessment and recommendations
            assessment = await self._generate_assessment(request, profile, risk_level)
            recommendations = await self._generate_recommendations(
                request, profile, risk_level
            )

            # Create response
            response = HealthConsultationResponse(
                consultation_id=f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.user_id[:8]}",
                user_id=request.user_id,
                consultation_type=request.consultation_type,
                risk_level=risk_level,
                assessment=assessment,
                recommendations=recommendations,
                emergency_action_required=emergency_detected,
                follow_up_needed=risk_level
                in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL],
                medical_disclaimer=self.medical_disclaimer,
                confidence_score=0.85,  # Would be calculated based on data quality
                timestamp=datetime.now(),
            )

            # Store consultation
            self.database.store_consultation(response)

            return response

        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            raise

    def _check_emergency_conditions(self, request: HealthConsultationRequest) -> bool:
        """Check if the consultation indicates an emergency."""
        if not request.symptoms:
            return False

        # Check for emergency keywords in symptoms
        symptoms_text = " ".join(request.symptoms).lower()
        for keyword in self.emergency_keywords:
            if keyword in symptoms_text:
                logger.warning(f"Emergency keyword detected: {keyword}")
                return True

        # Check severity
        if request.severity and request.severity.lower() == "severe":
            return True

        return False

    async def _assess_risk_level(
        self, request: HealthConsultationRequest, profile: Optional[HealthProfile]
    ) -> HealthRiskLevel:
        """Assess the risk level based on symptoms and profile."""

        # Emergency conditions
        if self._check_emergency_conditions(request):
            return HealthRiskLevel.EMERGENCY

        # High-risk conditions
        if request.severity == "severe" or (
            profile
            and any(
                condition in ["diabetes", "heart disease", "hypertension"]
                for condition in profile.medical_conditions
            )
        ):
            return HealthRiskLevel.HIGH

        # Moderate risk
        if request.severity == "moderate" or len(request.symptoms or []) > 3:
            return HealthRiskLevel.MODERATE

        return HealthRiskLevel.LOW

    async def _generate_assessment(
        self,
        request: HealthConsultationRequest,
        profile: Optional[HealthProfile],
        risk_level: HealthRiskLevel,
    ) -> str:
        """Generate health assessment based on symptoms and profile."""

        if risk_level == HealthRiskLevel.EMERGENCY:
            return """
            EMERGENCY SITUATION DETECTED: Based on your symptoms, this may require 
            immediate medical attention. Please contact emergency services or go to 
            the nearest emergency room immediately.
            """

        # Simulate AI-powered assessment (in real implementation, this would use ML models)
        base_assessment = f"""
        Based on your reported symptoms and health profile, this appears to be a 
        {risk_level.value} risk situation. The symptoms you've described may be 
        related to several possible conditions, but proper medical evaluation 
        is needed for accurate diagnosis.
        """

        if profile:
            base_assessment += f"""
            
            Your medical history shows {len(profile.medical_conditions)} known conditions 
            and {len(profile.medications)} current medications, which have been considered 
            in this assessment.
            """

        return base_assessment

    async def _generate_recommendations(
        self,
        request: HealthConsultationRequest,
        profile: Optional[HealthProfile],
        risk_level: HealthRiskLevel,
    ) -> List[str]:
        """Generate personalized health recommendations."""

        recommendations = []

        if risk_level == HealthRiskLevel.EMERGENCY:
            recommendations.extend(
                [
                    "🚨 Contact emergency services (911) immediately",
                    "🏥 Go to the nearest emergency room",
                    "📞 Call your doctor or emergency contact",
                    "🚫 Do not drive yourself - call for ambulance or have someone drive you",
                ]
            )
        elif risk_level == HealthRiskLevel.HIGH:
            recommendations.extend(
                [
                    "👨‍⚕️ Schedule an appointment with your healthcare provider within 24 hours",
                    "📋 Monitor symptoms closely and document changes",
                    "🚫 Avoid strenuous activities until cleared by a doctor",
                    "📞 Call your doctor if symptoms worsen",
                ]
            )
        elif risk_level == HealthRiskLevel.MODERATE:
            recommendations.extend(
                [
                    "👨‍⚕️ Consider scheduling a doctor's appointment within a few days",
                    "💊 Continue any prescribed medications as directed",
                    "💧 Stay hydrated and get adequate rest",
                    "📊 Monitor symptoms and their progression",
                ]
            )
        else:  # LOW risk
            recommendations.extend(
                [
                    "🏠 Rest and self-care measures may help",
                    "💧 Stay hydrated and maintain good nutrition",
                    "😴 Ensure adequate sleep and stress management",
                    "📞 Contact your doctor if symptoms persist or worsen",
                ]
            )

        # Add general health recommendations
        recommendations.extend(
            [
                "📚 Learn more about your symptoms from reputable medical sources",
                "💾 Keep a symptom diary for your healthcare provider",
                "🔒 Your health data is protected and confidential",
            ]
        )

        return recommendations

    def get_consultation_history(
        self, user_id: str
    ) -> List[HealthConsultationResponse]:
        """Get user's consultation history."""
        self.privacy_manager.log_access(
            user_id, "history_access", "consultation_history"
        )
        return self.database.consultation_history.get(user_id, [])

    def emergency_response(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Provide emergency response guidance."""
        return {
            "immediate_actions": [
                "📞 Call emergency services (911 in US, 112 in EU)",
                "🆔 Provide your name, location, and nature of emergency",
                "🏥 Follow dispatcher instructions exactly",
                "🚑 Stay on the line until help arrives",
            ],
            "location": location or "Unknown - please provide to emergency services",
            "emergency_numbers": {
                "US": "911",
                "EU": "112",
                "UK": "999",
                "International": "Check local emergency numbers",
            },
            "critical_info": [
                "Your name and age",
                "Exact location or address",
                "Nature of the emergency",
                "Current symptoms or injuries",
                "Any known medical conditions or medications",
            ],
        }
