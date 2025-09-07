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
"""
Health Assistant Memory Module

This package provides foundational classes and interfaces
for managing health consultation memory and patient history
in the Health Assistant's AI-powered medical consultation system.
"""

from .models import HealthMemoryItem, SearchHealthMemoryInput, DeleteHealthMemoryInput
from .interfaces import HealthMemoryEditor

# Compatibility aliases
from .models import MemoryItem, SearchMemoryInput, DeleteMemoryInput
from .interfaces import MemoryEditor

__all__ = [
    "HealthMemoryItem",
    "SearchHealthMemoryInput",
    "DeleteHealthMemoryInput",
    "HealthMemoryEditor",
    # Compatibility aliases
    "MemoryItem",
    "SearchMemoryInput",
    "DeleteMemoryInput",
    "MemoryEditor",
]
