"""
Health Assistant AI - Symptom Analyzer Tool

Advanced AI-powered symptom analysis tool that helps evaluate patient symptoms
and provides preliminary health assessments with appropriate care recommendations.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0

MEDICAL DISCLAIMER: This tool provides health information only and is not
intended to replace professional medical advice, diagnosis, or treatment.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger("health_assistant.symptom_analyzer_tool")


class SymptomInput(BaseModel):
    """Input schema for symptom analysis."""
    
    symptoms: List[str] = Field(
        description="List of symptoms reported by the patient",
        min_items=1
    )
    duration: str = Field(
        description="How long the symptoms have been present (e.g., '2 days', '1 week')"
    )
    severity: str = Field(
        description="Severity level: 'mild', 'moderate', 'severe', or 'critical'",
        regex="^(mild|moderate|severe|critical)$"
    )
    patient_age: Optional[int] = Field(
        description="Patient's age in years",
        ge=0,
        le=120
    )
    patient_gender: Optional[str] = Field(
        description="Patient's gender: 'male', 'female', 'other', or 'prefer_not_to_say'",
        regex="^(male|female|other|prefer_not_to_say)$"
    )
    existing_conditions: Optional[List[str]] = Field(
        default=[],
        description="List of existing medical conditions"
    )
    current_medications: Optional[List[str]] = Field(
        default=[],
        description="List of current medications"
    )
    
    @validator('symptoms')
    def validate_symptoms(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one symptom must be provided")
        return [symptom.strip().lower() for symptom in v]


class SymptomAnalysisResult(BaseModel):
    """Result schema for symptom analysis."""
    
    risk_level: str = Field(description="Assessed risk level: low, moderate, high, emergency")
    assessment: str = Field(description="Detailed health assessment")
    recommendations: List[str] = Field(description="Care recommendations")
    emergency_indicators: List[str] = Field(description="Emergency warning signs identified")
    next_steps: str = Field(description="Recommended next steps for care")
    disclaimer: str = Field(description="Medical disclaimer")


class SymptomAnalyzerTool(BaseTool):
    """
    Advanced symptom analysis tool for preliminary health assessment.
    
    This tool analyzes patient-reported symptoms and provides:
    - Risk level assessment
    - Preliminary health evaluation
    - Care recommendations
    - Emergency situation detection
    - Next steps guidance
    """
    
    name: str = "symptom_analyzer"
    description: str = """
    Analyzes patient symptoms to provide preliminary health assessment and care guidance.
    
    Input should include:
    - symptoms: List of reported symptoms
    - duration: How long symptoms have been present
    - severity: mild/moderate/severe/critical
    - patient_age: Patient's age (optional)
    - patient_gender: Patient's gender (optional)
    - existing_conditions: Known medical conditions (optional)
    - current_medications: Current medications (optional)
    
    Returns comprehensive health assessment with risk level and recommendations.
    """
    
    args_schema = SymptomInput
    medical_approved: bool = True  # Marked as medically approved tool
    
    # Emergency keywords that require immediate attention
    EMERGENCY_KEYWORDS = [
        "chest pain", "difficulty breathing", "severe bleeding", "unconscious",
        "severe headache", "stroke symptoms", "heart attack", "severe abdominal pain",
        "high fever", "seizure", "severe allergic reaction", "poisoning",
        "severe burns", "broken bones", "head injury", "suicide thoughts"
    ]
    
    def _run(self, **kwargs) -> str:
        """Execute symptom analysis (synchronous version)."""
        try:
            input_data = SymptomInput(**kwargs)
            result = self._analyze_symptoms(input_data)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"Error in symptom analysis: {str(e)}")
            return self._format_error_response(str(e))
    
    async def _arun(self, **kwargs) -> str:
        """Execute symptom analysis (asynchronous version)."""
        return self._run(**kwargs)
    
    def _analyze_symptoms(self, input_data: SymptomInput) -> SymptomAnalysisResult:
        """Perform comprehensive symptom analysis."""
        
        # Check for emergency conditions
        emergency_indicators = self._check_emergency_symptoms(input_data.symptoms)
        
        # Assess risk level
        risk_level = self._assess_risk_level(input_data, emergency_indicators)
        
        # Generate assessment
        assessment = self._generate_assessment(input_data, risk_level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(input_data, risk_level)
        
        # Generate next steps
        next_steps = self._generate_next_steps(risk_level)
        
        return SymptomAnalysisResult(
            risk_level=risk_level,
            assessment=assessment,
            recommendations=recommendations,
            emergency_indicators=emergency_indicators,
            next_steps=next_steps,
            disclaimer=self._get_medical_disclaimer()
        )
    
    def _check_emergency_symptoms(self, symptoms: List[str]) -> List[str]:
        """Check for emergency warning signs."""
        emergency_indicators = []
        symptoms_text = " ".join(symptoms)
        
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in symptoms_text:
                emergency_indicators.append(keyword)
                logger.warning(f"Emergency symptom detected: {keyword}")
        
        return emergency_indicators
    
    def _assess_risk_level(self, input_data: SymptomInput, emergency_indicators: List[str]) -> str:
        """Assess the overall risk level."""
        
        if emergency_indicators or input_data.severity == "critical":
            return "emergency"
        
        if input_data.severity == "severe":
            return "high"
        
        if (input_data.severity == "moderate" or 
            len(input_data.symptoms) > 3 or
            input_data.existing_conditions):
            return "moderate"
        
        return "low"
    
    def _generate_assessment(self, input_data: SymptomInput, risk_level: str) -> str:
        """Generate health assessment based on symptoms."""
        
        if risk_level == "emergency":
            return """
            EMERGENCY SITUATION DETECTED: Based on your symptoms, this may require 
            immediate medical attention. Please contact emergency services or go to 
            the nearest emergency room immediately.
            """
        
        base_assessment = f"""
        Based on your reported symptoms and information provided, this appears to be a 
        {risk_level} risk situation. The symptoms you've described lasting {input_data.duration} 
        may be related to several possible conditions, but proper medical evaluation 
        is needed for accurate diagnosis.
        """
        
        if input_data.existing_conditions:
            base_assessment += f"""
            
            Given your medical history ({', '.join(input_data.existing_conditions)}), 
            it's particularly important to monitor these symptoms carefully.
            """
        
        return base_assessment.strip()
    
    def _generate_recommendations(self, input_data: SymptomInput, risk_level: str) -> List[str]:
        """Generate care recommendations."""
        
        if risk_level == "emergency":
            return [
                "Contact emergency services (911) immediately",
                "Go to the nearest emergency room",
                "Do not drive yourself - call for emergency transport",
                "Have someone stay with you until help arrives"
            ]
        
        recommendations = []
        
        if risk_level == "high":
            recommendations.extend([
                "Schedule an urgent appointment with your healthcare provider",
                "Consider visiting an urgent care center if your doctor is unavailable",
                "Monitor symptoms closely and seek immediate care if they worsen"
            ])
        elif risk_level == "moderate":
            recommendations.extend([
                "Schedule an appointment with your healthcare provider within 1-2 days",
                "Keep a symptom diary to track changes",
                "Rest and stay hydrated"
            ])
        else:  # low risk
            recommendations.extend([
                "Monitor symptoms for 24-48 hours",
                "Contact your healthcare provider if symptoms persist or worsen",
                "Get adequate rest and maintain good hydration"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "Avoid self-medication without professional guidance",
            "Follow up with your regular healthcare provider",
            "Keep a record of your symptoms for medical consultation"
        ])
        
        return recommendations
    
    def _generate_next_steps(self, risk_level: str) -> str:
        """Generate next steps guidance."""
        
        if risk_level == "emergency":
            return "Seek immediate emergency medical care - call 911 or go to the nearest ER."
        elif risk_level == "high":
            return "Contact your healthcare provider today for urgent evaluation."
        elif risk_level == "moderate":
            return "Schedule a medical appointment within 1-2 days for proper evaluation."
        else:
            return "Monitor symptoms and contact healthcare provider if they persist or worsen."
    
    def _get_medical_disclaimer(self) -> str:
        """Get the medical disclaimer."""
        return """
        IMPORTANT: This analysis is for informational purposes only and does not 
        constitute medical advice, diagnosis, or treatment. Always consult with 
        qualified healthcare professionals for medical concerns. In case of emergency, 
        contact local emergency services immediately.
        """
    
    def _format_result(self, result: SymptomAnalysisResult) -> str:
        """Format the analysis result for output."""
        
        output = f"""
        🏥 SYMPTOM ANALYSIS RESULT
        ========================
        
        🚨 Risk Level: {result.risk_level.upper()}
        
        📋 Assessment:
        {result.assessment}
        
        💡 Recommendations:
        """
        
        for i, rec in enumerate(result.recommendations, 1):
            output += f"\n{i}. {rec}"
        
        if result.emergency_indicators:
            output += f"\n\n⚠️  Emergency Indicators Detected: {', '.join(result.emergency_indicators)}"
        
        output += f"\n\n🏃 Next Steps: {result.next_steps}"
        
        output += f"\n\n⚖️  Medical Disclaimer:\n{result.disclaimer}"
        
        return output
    
    def _format_error_response(self, error: str) -> str:
        """Format error response."""
        return f"""
        ❌ SYMPTOM ANALYSIS ERROR
        ========================
        
        An error occurred during symptom analysis: {error}
        
        Please ensure you provide:
        - At least one symptom
        - Duration of symptoms
        - Severity level (mild/moderate/severe/critical)
        
        For immediate medical concerns, please contact your healthcare provider 
        or emergency services directly.
        """
