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

from abc import ABC
from abc import abstractmethod

from .models import HealthMemoryItem


class HealthMemoryEditor(ABC):
    """
    Abstract interface for editing and retrieving health-related memory items.

    A HealthMemoryEditor is responsible for adding, searching, and
    removing health consultation memories and patient interaction history.

    Implementations may integrate with healthcare-focused vector stores 
    or other specialized medical indexing backends.
    """

    @abstractmethod
    async def add_health_items(self, items: list[HealthMemoryItem]) -> None:
        """
        Insert multiple health-related MemoryItems into the patient memory.

        Args:
            items (list[HealthMemoryItem]): The health consultation items to be added.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_health_history(self, query: str, top_k: int = 5, **kwargs) -> list[HealthMemoryItem]:
        """
        Retrieve health consultation items relevant to the given medical query.
        Relevance criteria depend on medical context and patient history.

        Args:
            query (str): The health query string to match.
            top_k (int): Maximum number of health items to return.
            kwargs (dict): Keyword arguments for medical search filtering.

        Returns:
            list[HealthMemoryItem]: The most relevant health consultation items.
        """
        raise NotImplementedError

    @abstractmethod
    async def remove_health_items(self, **kwargs) -> None:
        """
        Remove health consultation items. Additional parameters
        needed for deletion can be specified in keyword arguments.

        Args:
            kwargs (dict): Keyword arguments for specifying deletion criteria.
        """
        raise NotImplementedError

    # Compatibility aliases for backward compatibility
    async def add_items(self, items: list[HealthMemoryItem]) -> None:
        """Legacy method name for backward compatibility."""
        return await self.add_health_items(items)

    async def search(self, query: str, top_k: int = 5, **kwargs) -> list[HealthMemoryItem]:
        """Legacy method name for backward compatibility."""
        return await self.search_health_history(query, top_k, **kwargs)

    async def remove_items(self, **kwargs) -> None:
        """Legacy method name for backward compatibility."""
        return await self.remove_health_items(**kwargs)


# Compatibility aliases for backward compatibility
MemoryEditor = HealthMemoryEditor
