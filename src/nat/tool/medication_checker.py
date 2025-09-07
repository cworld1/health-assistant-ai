"""
Health Assistant AI - Medication Checker Tool

Comprehensive medication information and interaction checking tool that provides
detailed drug information, interaction warnings, and dosage guidance.

Copyright (c) 2024-2025, Health Assistant AI Project. All rights reserved.
Licensed under the Apache License, Version 2.0

MEDICAL DISCLAIMER: This tool provides medication information only and is not
intended to replace professional pharmaceutical or medical advice.
"""

import logging
from typing import List, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger("health_assistant.medication_checker_tool")


class MedicationInput(BaseModel):
    """Input schema for medication checking."""
    
    medication_name: str = Field(
        description="Name of the medication to check",
        min_length=1
    )
    current_medications: Optional[List[str]] = Field(
        default=[],
        description="List of current medications for interaction checking"
    )
    patient_age: Optional[int] = Field(
        description="Patient's age in years for age-appropriate dosing",
        ge=0,
        le=120
    )
    patient_weight: Optional[float] = Field(
        description="Patient's weight in kg for weight-based dosing",
        gt=0
    )
    medical_conditions: Optional[List[str]] = Field(
        default=[],
        description="List of medical conditions for contraindication checking"
    )
    allergies: Optional[List[str]] = Field(
        default=[],
        description="List of known allergies"
    )
    
    @validator('medication_name')
    def validate_medication_name(cls, v):
        return v.strip().lower()


class MedicationResult(BaseModel):
    """Result schema for medication analysis."""
    
    medication_info: str = Field(description="Basic medication information")
    interactions: List[str] = Field(description="Drug interaction warnings")
    contraindications: List[str] = Field(description="Medical contraindications")
    dosage_info: str = Field(description="Dosage information and guidelines")
    side_effects: List[str] = Field(description="Common side effects")
    precautions: List[str] = Field(description="Important precautions")
    monitoring: str = Field(description="Monitoring recommendations")
    disclaimer: str = Field(description="Pharmaceutical disclaimer")


class MedicationCheckerTool(BaseTool):
    """
    Comprehensive medication information and interaction checker.
    
    This tool provides:
    - Detailed medication information
    - Drug interaction analysis
    - Contraindication checking
    - Dosage guidance
    - Side effect information
    - Safety precautions
    """
    
    name: str = "medication_checker"
    description: str = """
    Provides comprehensive medication information and safety analysis.
    
    Input should include:
    - medication_name: Name of the medication to check
    - current_medications: List of current medications (optional)
    - patient_age: Patient's age for dosing (optional)
    - patient_weight: Patient's weight for dosing (optional)
    - medical_conditions: Known medical conditions (optional)
    - allergies: Known allergies (optional)
    
    Returns detailed medication information, interactions, and safety guidance.
    """
    
    args_schema = MedicationInput
    medical_approved: bool = True
    
    # Common high-risk medication interactions
    HIGH_RISK_INTERACTIONS = {
        "warfarin": ["aspirin", "ibuprofen", "amiodarone", "simvastatin"],
        "digoxin": ["amiodarone", "verapamil", "quinidine"],
        "metformin": ["contrast dye", "alcohol"],
        "lithium": ["nsaids", "ace inhibitors", "diuretics"],
        "phenytoin": ["warfarin", "carbamazepine", "valproic acid"]
    }
    
    # Medications requiring special monitoring
    MONITORING_REQUIRED = {
        "warfarin": "Regular INR monitoring required",
        "digoxin": "Monitor serum levels and renal function",
        "lithium": "Monitor serum levels and kidney function",
        "phenytoin": "Monitor serum levels",
        "metformin": "Monitor kidney function"
    }
    
    def _run(self, **kwargs) -> str:
        """Execute medication checking (synchronous version)."""
        try:
            input_data = MedicationInput(**kwargs)
            result = self._check_medication(input_data)
            return self._format_result(result)
        except Exception as e:
            logger.error(f"Error in medication checking: {str(e)}")
            return self._format_error_response(str(e))
    
    async def _arun(self, **kwargs) -> str:
        """Execute medication checking (asynchronous version)."""
        return self._run(**kwargs)
    
    def _check_medication(self, input_data: MedicationInput) -> MedicationResult:
        """Perform comprehensive medication analysis."""
        
        # Get basic medication information
        medication_info = self._get_medication_info(input_data.medication_name)
        
        # Check for drug interactions
        interactions = self._check_interactions(input_data.medication_name, input_data.current_medications)
        
        # Check contraindications
        contraindications = self._check_contraindications(input_data.medication_name, input_data.medical_conditions)
        
        # Get dosage information
        dosage_info = self._get_dosage_info(input_data.medication_name, input_data.patient_age, input_data.patient_weight)
        
        # Get side effects
        side_effects = self._get_side_effects(input_data.medication_name)
        
        # Get precautions
        precautions = self._get_precautions(input_data.medication_name, input_data.allergies)
        
        # Get monitoring requirements
        monitoring = self._get_monitoring_requirements(input_data.medication_name)
        
        return MedicationResult(
            medication_info=medication_info,
            interactions=interactions,
            contraindications=contraindications,
            dosage_info=dosage_info,
            side_effects=side_effects,
            precautions=precautions,
            monitoring=monitoring,
            disclaimer=self._get_pharmaceutical_disclaimer()
        )
    
    def _get_medication_info(self, medication_name: str) -> str:
        """Get basic medication information."""
        
        # This would typically query a medical database
        # For demonstration, providing sample information for common medications
        
        medication_db = {
            "ibuprofen": "Nonsteroidal anti-inflammatory drug (NSAID) used for pain relief and inflammation reduction.",
            "acetaminophen": "Analgesic and antipyretic medication used for pain and fever relief.",
            "lisinopril": "ACE inhibitor used to treat high blood pressure and heart failure.",
            "metformin": "Antidiabetic medication used to treat type 2 diabetes.",
            "simvastatin": "Statin medication used to lower cholesterol levels.",
            "omeprazole": "Proton pump inhibitor used to reduce stomach acid production.",
            "metoprolol": "Beta-blocker used to treat high blood pressure and heart conditions.",
            "levothyroxine": "Synthetic thyroid hormone used to treat hypothyroidism."
        }
        
        return medication_db.get(medication_name, 
            f"Medication information for {medication_name} not found in database. Please consult a pharmacist or healthcare provider for detailed information.")
    
    def _check_interactions(self, medication_name: str, current_medications: List[str]) -> List[str]:
        """Check for drug interactions."""
        
        interactions = []
        
        if not current_medications:
            return ["No current medications provided for interaction checking."]
        
        # Check against known high-risk interactions
        if medication_name in self.HIGH_RISK_INTERACTIONS:
            for current_med in current_medications:
                current_med_lower = current_med.lower().strip()
                if current_med_lower in self.HIGH_RISK_INTERACTIONS[medication_name]:
                    interactions.append(f"⚠️ HIGH RISK: {medication_name} may interact with {current_med}")
        
        # Check if current medications have interactions with the new medication
        for current_med in current_medications:
            current_med_lower = current_med.lower().strip()
            if current_med_lower in self.HIGH_RISK_INTERACTIONS:
                if medication_name in self.HIGH_RISK_INTERACTIONS[current_med_lower]:
                    interactions.append(f"⚠️ HIGH RISK: {current_med} may interact with {medication_name}")
        
        if not interactions:
            interactions.append("✅ No known high-risk interactions identified with provided medications.")
        
        interactions.append("Note: This is not a complete interaction check. Consult your pharmacist for comprehensive screening.")
        
        return interactions
    
    def _check_contraindications(self, medication_name: str, medical_conditions: List[str]) -> List[str]:
        """Check for medical contraindications."""
        
        contraindications = []
        
        if not medical_conditions:
            return ["No medical conditions provided for contraindication checking."]
        
        # Common contraindications
        contraindication_db = {
            "ibuprofen": ["kidney disease", "heart failure", "stomach ulcers"],
            "metformin": ["kidney disease", "liver disease", "heart failure"],
            "lisinopril": ["kidney disease", "hyperkalemia", "angioedema history"],
            "simvastatin": ["liver disease", "active liver disease", "pregnancy"],
            "metoprolol": ["asthma", "severe heart block", "cardiogenic shock"]
        }
        
        if medication_name in contraindication_db:
            for condition in medical_conditions:
                condition_lower = condition.lower().strip()
                if condition_lower in contraindication_db[medication_name]:
                    contraindications.append(f"⚠️ CONTRAINDICATION: {medication_name} may be contraindicated with {condition}")
        
        if not contraindications:
            contraindications.append("✅ No known contraindications identified with provided medical conditions.")
        
        contraindications.append("Note: Always inform your healthcare provider of all medical conditions.")
        
        return contraindications
    
    def _get_dosage_info(self, medication_name: str, age: Optional[int], weight: Optional[float]) -> str:
        """Get dosage information."""
        
        base_dosage = f"Standard adult dosage information for {medication_name}:"
        
        dosage_db = {
            "ibuprofen": "200-400 mg every 4-6 hours, maximum 1200 mg/day for OTC use",
            "acetaminophen": "325-650 mg every 4-6 hours, maximum 3000 mg/day",
            "lisinopril": "Starting dose 10 mg once daily, may adjust based on response",
            "metformin": "Starting dose 500 mg twice daily with meals",
            "simvastatin": "Starting dose 20-40 mg once daily in the evening"
        }
        
        standard_dose = dosage_db.get(medication_name, "Dosage information not available in database.")
        
        dosage_info = f"{base_dosage}\n{standard_dose}"
        
        if age and age < 18:
            dosage_info += "\n⚠️ PEDIATRIC: Pediatric dosing may differ significantly. Consult pediatrician."
        elif age and age > 65:
            dosage_info += "\n⚠️ GERIATRIC: Elderly patients may require dose adjustments. Consult physician."
        
        if weight:
            dosage_info += f"\n📏 Weight-based considerations: Patient weight {weight} kg noted for dosing calculations."
        
        dosage_info += "\n\n🔸 IMPORTANT: This is general information only. Always follow your healthcare provider's specific dosing instructions."
        
        return dosage_info
    
    def _get_side_effects(self, medication_name: str) -> List[str]:
        """Get common side effects."""
        
        side_effects_db = {
            "ibuprofen": ["stomach upset", "nausea", "dizziness", "headache"],
            "acetaminophen": ["generally well tolerated", "rare: liver toxicity with overdose"],
            "lisinopril": ["dry cough", "dizziness", "hyperkalemia", "angioedema (rare)"],
            "metformin": ["nausea", "diarrhea", "stomach upset", "metallic taste"],
            "simvastatin": ["muscle pain", "headache", "nausea", "liver enzyme elevation"]
        }
        
        return side_effects_db.get(medication_name, 
            ["Side effect information not available in database. Consult medication leaflet or pharmacist."])
    
    def _get_precautions(self, medication_name: str, allergies: List[str]) -> List[str]:
        """Get important precautions."""
        
        precautions = []
        
        # Check for allergies
        if allergies:
            for allergy in allergies:
                if medication_name.lower() in allergy.lower() or allergy.lower() in medication_name.lower():
                    precautions.append(f"🚨 ALLERGY ALERT: Patient reports allergy to {allergy}")
        
        # General precautions
        general_precautions = {
            "ibuprofen": ["Take with food", "Avoid alcohol", "Monitor for stomach bleeding"],
            "metformin": ["Take with meals", "Stay hydrated", "Monitor kidney function"],
            "lisinopril": ["Monitor blood pressure", "Check potassium levels", "Avoid salt substitutes"],
            "simvastatin": ["Take in evening", "Avoid grapefruit juice", "Report muscle pain"]
        }
        
        if medication_name in general_precautions:
            precautions.extend(general_precautions[medication_name])
        
        if not precautions:
            precautions.append("Follow general medication safety guidelines.")
        
        return precautions
    
    def _get_monitoring_requirements(self, medication_name: str) -> str:
        """Get monitoring requirements."""
        
        if medication_name in self.MONITORING_REQUIRED:
            return self.MONITORING_REQUIRED[medication_name]
        else:
            return "Regular follow-up with healthcare provider recommended."
    
    def _get_pharmaceutical_disclaimer(self) -> str:
        """Get pharmaceutical disclaimer."""
        return """
        IMPORTANT: This medication information is for educational purposes only and does not 
        constitute pharmaceutical or medical advice. Always consult with your pharmacist or 
        healthcare provider before starting, stopping, or changing medications. Report any 
        adverse effects to your healthcare provider immediately.
        """
    
    def _format_result(self, result: MedicationResult) -> str:
        """Format the medication result for output."""
        
        output = f"""
        💊 MEDICATION ANALYSIS RESULT
        ============================
        
        📋 Medication Information:
        {result.medication_info}
        
        ⚠️  Drug Interactions:
        """
        
        for interaction in result.interactions:
            output += f"\n• {interaction}"
        
        output += "\n\n🚫 Contraindications:"
        for contraindication in result.contraindications:
            output += f"\n• {contraindication}"
        
        output += f"\n\n💉 Dosage Information:\n{result.dosage_info}"
        
        output += "\n\n🔍 Common Side Effects:"
        for side_effect in result.side_effects:
            output += f"\n• {side_effect}"
        
        output += "\n\n⚡ Important Precautions:"
        for precaution in result.precautions:
            output += f"\n• {precaution}"
        
        output += f"\n\n📊 Monitoring: {result.monitoring}"
        
        output += f"\n\n⚖️  Pharmaceutical Disclaimer:\n{result.disclaimer}"
        
        return output
    
    def _format_error_response(self, error: str) -> str:
        """Format error response."""
        return f"""
        ❌ MEDICATION CHECK ERROR
        ========================
        
        An error occurred during medication analysis: {error}
        
        Please ensure you provide:
        - A valid medication name
        
        For medication questions, please consult your pharmacist or healthcare provider directly.
        """
