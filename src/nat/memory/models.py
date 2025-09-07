# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class HealthMemoryItem(BaseModel):
    """
    Represents a single health consultation memory item consisting of structured medical content and associated metadata.

    Attributes
    ----------
    conversation : list[dict[str, str]]
        A list of dictionaries containing health consultation exchanges.
    patient_id : str
        Unique identifier for this HealthMemoryItem's patient.
    health_tags : list[str]
        A list of strings representing health-related tags (symptoms, conditions, medications).
    metadata : dict[str, typing.Any]
        Health metadata providing medical context and consultation management.
    health_summary : str or None
        Optional health consultation summary. Helpful when returning patient history.
    medical_category : str or None
        Medical category such as 'symptoms', 'treatment', 'medication', 'follow_up'.
    consultation_date : str or None
        Date of the health consultation.
    severity_level : str or None
        Severity level: 'low', 'medium', 'high', 'critical'.
    """
    # yapf: disable
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "conversation": [
                        {
                            "role": "patient",
                            "content": "Hi, I'm experiencing headaches and fatigue for the past 3 days."
                        },
                        {
                            "role": "health_assistant",
                            "content": "I understand you're experiencing headaches and fatigue. Can you describe the severity and any triggers?"
                        }
                    ],
                    "patient_id": "patient_abc123",
                    "health_tags": ["headache", "fatigue", "symptoms"],
                    "metadata": {
                        "key_value_pairs": {
                            "type": "symptom_consultation",
                            "relevance": "high",
                            "consultation_duration": "15min"
                        }
                    },
                    "medical_category": "symptoms",
                    "consultation_date": "2025-09-07",
                    "severity_level": "medium"
                },
                {
                    "health_summary": "Patient has history of migraines and takes ibuprofen as needed.",
                    "patient_id": "patient_abc123",
                    "health_tags": ["migraine", "ibuprofen", "medication_history"],
                    "medical_category": "medication",
                    "severity_level": "low"
                }
            ]
        },
        # Allow population of models from arbitrary types (e.g., ORM objects)
        arbitrary_types_allowed=True,
        # Enable aliasing if needed
        populate_by_name=True
    )
    # yapf: enable
    conversation: list[dict[str, str]] | None = Field(
        description="List of health consultation messages. Each message must have a \"role\" "
        "key (patient or health_assistant) and a \"content\" key with medical information.",
        default=None)
    health_tags: list[str] = Field(default_factory=list, description="List of health-related tags applied to the consultation.")
    metadata: dict[str, typing.Any] = Field(description="Health metadata about the consultation.", default={})
    patient_id: str = Field(description="The patient's unique ID.")
    health_summary: str | None = Field(default=None, description="Summary of the health consultation.")
    medical_category: str | None = Field(default=None, description="Medical category: symptoms, treatment, medication, follow_up.")
    consultation_date: str | None = Field(default=None, description="Date of the health consultation.")
    severity_level: str | None = Field(default=None, description="Severity level: low, medium, high, critical.")


class SearchHealthMemoryInput(BaseModel):
    """
    Represents a search health memory input structure.
    """
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "query": "What medications is the patient currently taking?",
            "top_k": 5,
            "patient_id": "patient_abc123",
            "medical_category": "medication"
        }
    })

    query: str = Field(description="Health search query for which to retrieve medical history.")
    top_k: int = Field(description="Maximum number of health memories to return")
    patient_id: str = Field(description="ID of the patient to search for.")
    medical_category: str | None = Field(default=None, description="Optional medical category filter.")


class DeleteHealthMemoryInput(BaseModel):
    """
    Represents a delete health memory input structure.
    """
    model_config = ConfigDict(json_schema_extra={"example": {"patient_id": "patient_abc123", }})

    patient_id: str = Field(description="ID of the patient to delete health memory for. Careful when using "
                         "this tool; make sure you use the "
                         "patient ID present in the consultation.")


# Compatibility aliases
MemoryItem = HealthMemoryItem
SearchMemoryInput = SearchHealthMemoryInput
DeleteMemoryInput = DeleteHealthMemoryInput
