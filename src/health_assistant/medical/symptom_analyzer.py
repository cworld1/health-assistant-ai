"""
Health Assistant AI - Symptom Analyzer

Advanced AI-powered symptom analysis engine that helps users understand
their health conditions and provides guidance on appropriate care levels.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger("health_assistant.symptom_analyzer")


class SymptomSeverity(Enum):
    """Symptom severity levels."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class BodySystem(Enum):
    """Body systems for symptom categorization."""

    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORY = "respiratory"
    NEUROLOGICAL = "neurological"
    GASTROINTESTINAL = "gastrointestinal"
    MUSCULOSKELETAL = "musculoskeletal"
    DERMATOLOGICAL = "dermatological"
    ENDOCRINE = "endocrine"
    REPRODUCTIVE = "reproductive"
    PSYCHOLOGICAL = "psychological"
    GENERAL = "general"


@dataclass
class Symptom:
    """Individual symptom data structure."""

    name: str
    severity: SymptomSeverity
    duration: str  # e.g., "2 days", "1 week"
    frequency: str  # e.g., "constant", "intermittent"
    body_system: BodySystem
    associated_factors: List[str]  # triggers, relieving factors


class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis."""

    symptoms: List[Dict[str, str]] = Field(
        ..., description="List of symptoms with details"
    )
    patient_age: int = Field(..., description="Patient age")
    patient_gender: str = Field(..., description="Patient gender")
    medical_history: Optional[List[str]] = Field(
        None, description="Relevant medical history"
    )
    current_medications: Optional[List[str]] = Field(
        None, description="Current medications"
    )
    lifestyle_factors: Optional[Dict[str, str]] = Field(
        None, description="Lifestyle information"
    )


class SymptomAnalysisResult(BaseModel):
    """Result model for symptom analysis."""

    analysis_id: str
    risk_assessment: str
    possible_conditions: List[Dict[str, float]]  # condition name and probability
    urgency_level: str
    recommended_actions: List[str]
    red_flags: List[str]  # Warning signs requiring immediate attention
    follow_up_timeframe: str
    confidence_score: float
    timestamp: datetime


class SymptomAnalyzer:
    """Advanced AI-powered symptom analysis engine."""

    def __init__(self):
        """Initialize the symptom analyzer."""
        self.emergency_symptoms = {
            "chest_pain": ["chest pain", "chest pressure", "crushing chest pain"],
            "breathing": [
                "difficulty breathing",
                "shortness of breath",
                "cannot breathe",
            ],
            "neurological": [
                "sudden weakness",
                "facial drooping",
                "slurred speech",
                "severe headache",
            ],
            "bleeding": [
                "severe bleeding",
                "uncontrolled bleeding",
                "massive bleeding",
            ],
            "consciousness": ["unconscious", "loss of consciousness", "fainting"],
            "allergic": [
                "severe allergic reaction",
                "anaphylaxis",
                "swelling of face/throat",
            ],
            "trauma": ["severe injury", "broken bones", "head injury"],
            "poisoning": ["poisoning", "overdose", "toxic ingestion"],
        }

        # Common symptom patterns and their implications
        self.symptom_patterns = {
            "flu_like": {
                "symptoms": ["fever", "body aches", "fatigue", "headache"],
                "conditions": ["viral infection", "influenza", "common cold"],
                "urgency": "low",
            },
            "cardiac": {
                "symptoms": ["chest pain", "shortness of breath", "sweating", "nausea"],
                "conditions": ["heart attack", "angina", "cardiac arrhythmia"],
                "urgency": "emergency",
            },
            "stroke": {
                "symptoms": [
                    "sudden weakness",
                    "facial drooping",
                    "speech problems",
                    "severe headache",
                ],
                "conditions": ["stroke", "transient ischemic attack"],
                "urgency": "emergency",
            },
            "digestive": {
                "symptoms": ["nausea", "vomiting", "diarrhea", "abdominal pain"],
                "conditions": [
                    "gastroenteritis",
                    "food poisoning",
                    "inflammatory bowel disease",
                ],
                "urgency": "moderate",
            },
        }

    async def analyze_symptoms(
        self, request: SymptomAnalysisRequest
    ) -> SymptomAnalysisResult:
        """Perform comprehensive symptom analysis."""
        try:
            logger.info(
                f"Starting symptom analysis for patient age {request.patient_age}"
            )

            # Parse and categorize symptoms
            parsed_symptoms = self._parse_symptoms(request.symptoms)

            # Check for emergency conditions
            emergency_detected, red_flags = self._check_emergency_conditions(
                parsed_symptoms
            )

            # Assess risk level
            risk_level = self._assess_risk_level(
                parsed_symptoms, request.medical_history
            )

            # Identify possible conditions
            possible_conditions = self._identify_conditions(parsed_symptoms, request)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_level, emergency_detected, parsed_symptoms, request
            )

            # Determine follow-up timeframe
            follow_up = self._determine_follow_up(risk_level, emergency_detected)

            result = SymptomAnalysisResult(
                analysis_id=f"symptom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                risk_assessment=risk_level,
                possible_conditions=possible_conditions,
                urgency_level="emergency" if emergency_detected else risk_level,
                recommended_actions=recommendations,
                red_flags=red_flags,
                follow_up_timeframe=follow_up,
                confidence_score=self._calculate_confidence(parsed_symptoms),
                timestamp=datetime.now(),
            )

            logger.info(f"Symptom analysis completed: {result.analysis_id}")
            return result

        except Exception as e:
            logger.error(f"Symptom analysis failed: {e}")
            raise

    def _parse_symptoms(self, symptoms: List[Dict[str, str]]) -> List[Symptom]:
        """Parse and structure symptom data."""
        parsed_symptoms = []

        for symptom_data in symptoms:
            try:
                # Extract symptom information
                name = symptom_data.get("name", "").lower()
                severity_str = symptom_data.get("severity", "mild").lower()
                duration = symptom_data.get("duration", "unknown")
                frequency = symptom_data.get("frequency", "unknown")

                # Map severity
                severity = SymptomSeverity.MILD
                if severity_str in ["moderate"]:
                    severity = SymptomSeverity.MODERATE
                elif severity_str in ["severe"]:
                    severity = SymptomSeverity.SEVERE
                elif severity_str in ["critical"]:
                    severity = SymptomSeverity.CRITICAL

                # Categorize body system
                body_system = self._categorize_body_system(name)

                symptom = Symptom(
                    name=name,
                    severity=severity,
                    duration=duration,
                    frequency=frequency,
                    body_system=body_system,
                    associated_factors=symptom_data.get("factors", []),
                )

                parsed_symptoms.append(symptom)

            except Exception as e:
                logger.warning(f"Failed to parse symptom: {symptom_data}, error: {e}")
                continue

        return parsed_symptoms

    def _categorize_body_system(self, symptom_name: str) -> BodySystem:
        """Categorize symptom by body system."""
        symptom_name = symptom_name.lower()

        # Cardiovascular
        if any(
            word in symptom_name
            for word in ["chest pain", "heart", "palpitation", "cardiac"]
        ):
            return BodySystem.CARDIOVASCULAR

        # Respiratory
        if any(
            word in symptom_name
            for word in ["breathing", "cough", "lung", "respiratory"]
        ):
            return BodySystem.RESPIRATORY

        # Neurological
        if any(
            word in symptom_name
            for word in ["headache", "dizziness", "weakness", "numbness", "seizure"]
        ):
            return BodySystem.NEUROLOGICAL

        # Gastrointestinal
        if any(
            word in symptom_name
            for word in ["nausea", "vomiting", "diarrhea", "stomach", "abdominal"]
        ):
            return BodySystem.GASTROINTESTINAL

        # Musculoskeletal
        if any(
            word in symptom_name for word in ["pain", "ache", "joint", "muscle", "bone"]
        ):
            return BodySystem.MUSCULOSKELETAL

        # Dermatological
        if any(word in symptom_name for word in ["rash", "skin", "itch", "burn"]):
            return BodySystem.DERMATOLOGICAL

        return BodySystem.GENERAL

    def _check_emergency_conditions(
        self, symptoms: List[Symptom]
    ) -> Tuple[bool, List[str]]:
        """Check for emergency conditions requiring immediate attention."""
        emergency_detected = False
        red_flags = []

        for symptom in symptoms:
            symptom_name = symptom.name.lower()

            # Check against emergency symptom database
            for category, emergency_terms in self.emergency_symptoms.items():
                for term in emergency_terms:
                    if term in symptom_name:
                        emergency_detected = True
                        red_flags.append(
                            f"🚨 {term.title()} - requires immediate medical attention"
                        )

            # Check severity levels
            if symptom.severity in [SymptomSeverity.SEVERE, SymptomSeverity.CRITICAL]:
                if symptom.body_system in [
                    BodySystem.CARDIOVASCULAR,
                    BodySystem.NEUROLOGICAL,
                ]:
                    emergency_detected = True
                    red_flags.append(
                        f"🚨 Severe {symptom.body_system.value} symptoms detected"
                    )

        return emergency_detected, red_flags

    def _assess_risk_level(
        self, symptoms: List[Symptom], medical_history: Optional[List[str]]
    ) -> str:
        """Assess overall risk level based on symptoms and history."""

        # Count severe symptoms
        severe_count = sum(
            1
            for s in symptoms
            if s.severity in [SymptomSeverity.SEVERE, SymptomSeverity.CRITICAL]
        )

        # Check for high-risk body systems
        high_risk_systems = [
            BodySystem.CARDIOVASCULAR,
            BodySystem.NEUROLOGICAL,
            BodySystem.RESPIRATORY,
        ]
        high_risk_symptoms = [s for s in symptoms if s.body_system in high_risk_systems]

        # Consider medical history
        high_risk_conditions = (
            ["heart disease", "diabetes", "stroke", "cancer"] if medical_history else []
        )
        has_high_risk_history = any(
            condition in " ".join(medical_history or []).lower()
            for condition in high_risk_conditions
        )

        if severe_count > 0 or len(high_risk_symptoms) > 1:
            return "high"
        elif len(high_risk_symptoms) > 0 or has_high_risk_history:
            return "moderate"
        else:
            return "low"

    def _identify_conditions(
        self, symptoms: List[Symptom], request: SymptomAnalysisRequest
    ) -> List[Dict[str, float]]:
        """Identify possible medical conditions based on symptoms."""
        possible_conditions = []

        # Extract symptom names for pattern matching
        symptom_names = [s.name for s in symptoms]

        # Check against known patterns
        for pattern_name, pattern_data in self.symptom_patterns.items():
            pattern_symptoms = pattern_data["symptoms"]
            matches = sum(
                1 for ps in pattern_symptoms if any(ps in sn for sn in symptom_names)
            )

            if matches > 0:
                # Calculate probability based on symptom matches
                probability = min(0.9, matches / len(pattern_symptoms) + 0.2)

                for condition in pattern_data["conditions"]:
                    possible_conditions.append(
                        {
                            "condition": condition,
                            "probability": probability,
                            "pattern": pattern_name,
                        }
                    )

        # Sort by probability
        possible_conditions.sort(key=lambda x: x["probability"], reverse=True)

        # Return top 5 conditions
        return possible_conditions[:5]

    def _generate_recommendations(
        self,
        risk_level: str,
        emergency_detected: bool,
        symptoms: List[Symptom],
        request: SymptomAnalysisRequest,
    ) -> List[str]:
        """Generate personalized recommendations based on analysis."""
        recommendations = []

        if emergency_detected:
            recommendations.extend(
                [
                    "🚨 SEEK IMMEDIATE MEDICAL ATTENTION",
                    "📞 Call emergency services (911) or go to nearest ER",
                    "🚫 Do not drive yourself - call ambulance or have someone drive you",
                    "📋 Bring list of current medications and medical conditions",
                ]
            )
        elif risk_level == "high":
            recommendations.extend(
                [
                    "👨‍⚕️ Contact your healthcare provider immediately",
                    "🏥 Consider urgent care or ER if doctor unavailable",
                    "📊 Monitor symptoms closely for any changes",
                    "💊 Continue prescribed medications as directed",
                ]
            )
        elif risk_level == "moderate":
            recommendations.extend(
                [
                    "👨‍⚕️ Schedule appointment with healthcare provider within 24-48 hours",
                    "📋 Keep symptom diary noting changes and triggers",
                    "💧 Stay hydrated and get adequate rest",
                    "📞 Call doctor if symptoms worsen",
                ]
            )
        else:  # low risk
            recommendations.extend(
                [
                    "🏠 Self-care measures may help manage symptoms",
                    "💧 Stay hydrated and maintain good nutrition",
                    "😴 Ensure adequate sleep and stress management",
                    "📞 Contact healthcare provider if symptoms persist beyond a few days",
                ]
            )

        # Add specific recommendations based on symptoms
        for symptom in symptoms:
            if symptom.body_system == BodySystem.RESPIRATORY:
                recommendations.append("💨 Avoid irritants and allergens")
            elif symptom.body_system == BodySystem.GASTROINTESTINAL:
                recommendations.append(
                    "🍽️ Consider bland diet (BRAT: bananas, rice, applesauce, toast)"
                )
            elif symptom.body_system == BodySystem.MUSCULOSKELETAL:
                recommendations.append(
                    "🧊 Apply ice for acute injuries, heat for muscle tension"
                )

        return recommendations

    def _determine_follow_up(self, risk_level: str, emergency_detected: bool) -> str:
        """Determine appropriate follow-up timeframe."""
        if emergency_detected:
            return "Immediate - do not delay"
        elif risk_level == "high":
            return "Within 24 hours"
        elif risk_level == "moderate":
            return "Within 1-3 days"
        else:
            return "Within 1 week if symptoms persist"

    def _calculate_confidence(self, symptoms: List[Symptom]) -> float:
        """Calculate confidence score for the analysis."""
        # Base confidence
        confidence = 0.7

        # Increase confidence with more detailed symptoms
        for symptom in symptoms:
            if symptom.duration != "unknown":
                confidence += 0.05
            if symptom.frequency != "unknown":
                confidence += 0.05
            if symptom.associated_factors:
                confidence += 0.05

        # Cap at 0.95
        return min(0.95, confidence)

    def get_symptom_suggestions(self, partial_symptom: str) -> List[str]:
        """Get symptom suggestions for autocomplete."""
        common_symptoms = [
            "fever",
            "headache",
            "cough",
            "sore throat",
            "fatigue",
            "nausea",
            "vomiting",
            "diarrhea",
            "abdominal pain",
            "chest pain",
            "shortness of breath",
            "dizziness",
            "weakness",
            "joint pain",
            "muscle aches",
            "rash",
            "insomnia",
        ]

        partial_lower = partial_symptom.lower()
        return [s for s in common_symptoms if partial_lower in s]
