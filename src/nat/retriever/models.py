# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from nat.utils.type_converter import GlobalTypeConverter


class HealthDocument(BaseModel):
    """
    Object representing a retrieved health document/knowledge from a health knowledge retriever.
    """

    page_content: str = Field(
        description="Primary health content including symptoms, treatments, or medical information"
    )
    metadata: dict[str, Any] = Field(
        description="Health-related metadata including source, credibility, medical category"
    )
    document_id: str | None = Field(
        description="Unique ID for the health document, if supported by the configured datastore",
        default=None,
    )
    medical_category: str | None = Field(
        description="Medical category such as 'symptoms', 'treatments', 'drugs', 'conditions'",
        default=None,
    )
    credibility_score: float | None = Field(
        description="Credibility score of the medical information (0.0-1.0)",
        default=None,
    )
    source_type: str | None = Field(
        description="Type of medical source: 'peer_reviewed', 'clinical_trial', 'guideline', 'database'",
        default=None,
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthDocument:
        """
        Deserialize a HealthDocument from a dictionary representation.

        Args:
            data (dict): A dictionary containing health document information.

        Returns:
            HealthDocument: A reconstructed HealthDocument instance.
        """
        return cls(**data)


class HealthRetrieverOutput(BaseModel):
    results: list[HealthDocument] = Field(
        description="A list of retrieved health documents"
    )

    def __len__(self):
        return len(self.results)

    def __str__(self):
        return json.dumps(self.model_dump())


class HealthRetrieverError(Exception):
    pass


def health_retriever_output_to_dict(obj: HealthRetrieverOutput) -> dict:
    return obj.model_dump()


def health_retriever_output_to_str(obj: HealthRetrieverOutput) -> str:
    return str(obj)


GlobalTypeConverter.register_converter(health_retriever_output_to_dict)
GlobalTypeConverter.register_converter(health_retriever_output_to_str)

# Compatibility aliases with previous releases
Document = HealthDocument
RetrieverOutput = HealthRetrieverOutput
RetrieverError = HealthRetrieverError
AIQDocument = HealthDocument
