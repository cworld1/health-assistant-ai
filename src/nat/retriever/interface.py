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

from abc import ABC
from abc import abstractmethod

from nat.retriever.models import RetrieverOutput


class HealthKnowledgeRetriever(ABC):
    """
    Abstract interface for interacting with health knowledge stores.

    A HealthKnowledgeRetriever is responsible for retrieving relevant medical information
    from configured health data stores including medical literature, drug databases,
    symptom databases, and treatment guidelines.

    Implementations may integrate with medical vector stores or other specialized
    indexing backends that allow for health-related text search.
    """

    @abstractmethod
    async def search_symptoms(self, symptoms: str, **kwargs) -> RetrieverOutput:
        """
        Retrieve relevant medical information based on symptom descriptions.

        Args:
            symptoms: Description of symptoms to search for
            **kwargs: Additional search parameters (top_k, filters, etc.)

        Returns:
            RetrieverOutput containing relevant medical information
        """
        raise NotImplementedError

    @abstractmethod
    async def search_treatments(self, condition: str, **kwargs) -> RetrieverOutput:
        """
        Retrieve treatment options for a given medical condition.

        Args:
            condition: Medical condition to find treatments for
            **kwargs: Additional search parameters

        Returns:
            RetrieverOutput containing treatment information
        """
        raise NotImplementedError

    @abstractmethod
    async def search_drug_info(self, drug_name: str, **kwargs) -> RetrieverOutput:
        """
        Retrieve drug information including interactions, side effects, dosage.

        Args:
            drug_name: Name of the drug to search for
            **kwargs: Additional search parameters

        Returns:
            RetrieverOutput containing drug information
        """
        raise NotImplementedError

    async def search(self, query: str, **kwargs) -> RetrieverOutput:
        """
        General health information search method.

        Args:
            query: Health-related query
            **kwargs: Additional search parameters

        Returns:
            RetrieverOutput containing relevant health information
        """
        return await self.search_symptoms(query, **kwargs)


# Compatibility aliases with previous releases
Retriever = HealthKnowledgeRetriever
AIQRetriever = HealthKnowledgeRetriever
