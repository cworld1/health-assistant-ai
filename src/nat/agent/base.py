# SPDX-FileCopyrightText: Copyright (c) 2025, Health Assistant AI Project. All rights reserved.
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

import asyncio
import json
import logging
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any

from colorama import Fore
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph.graph import CompiledGraph

logger = logging.getLogger(__name__)

# Health-specific error messages
TOOL_NOT_FOUND_ERROR_MESSAGE = (
    "There is no health tool named {tool_name}. Available health tools: {tools}."
)
INPUT_SCHEMA_MESSAGE = ". Health consultation arguments must be provided as a valid JSON object following this format: {schema}"
NO_INPUT_ERROR_MESSAGE = "No patient input received. Please provide your health symptoms or concerns for consultation."
MEDICAL_DISCLAIMER_MESSAGE = "MEDICAL DISCLAIMER: This AI provides health information only. Always consult healthcare professionals for medical advice."

# Health consultation logging
HEALTH_AGENT_LOG_PREFIX = "[HEALTH ASSISTANT]"
AGENT_LOG_PREFIX = "[HEALTH ASSISTANT]"  # Legacy compatibility

CONSULTATION_LOG_MESSAGE = (
    f"\n{'-' * 50}\n"
    + HEALTH_AGENT_LOG_PREFIX
    + "\n"
    + Fore.GREEN
    + "Patient consultation: %s\n"
    + Fore.CYAN
    + "Health analysis: \n%s\n"
    + Fore.YELLOW
    + MEDICAL_DISCLAIMER_MESSAGE
    + Fore.RESET
    + f"\n{'-' * 50}"
)

HEALTH_TOOL_LOG_MESSAGE = (
    f"\n{'-' * 50}\n"
    + HEALTH_AGENT_LOG_PREFIX
    + "\n"
    + Fore.WHITE
    + "Using health tools: %s\n"
    + Fore.YELLOW
    + "Health data input: %s\n"
    + Fore.CYAN
    + "Health analysis result: \n%s"
    + Fore.RESET
    + f"\n{'-' * 50}"
)

TOOL_CALL_LOG_MESSAGE = HEALTH_TOOL_LOG_MESSAGE  # Legacy compatibility


class HealthDecision(Enum):
    """Health consultation decision types."""

    ANALYZE_SYMPTOMS = "analyze_symptoms"
    CHECK_MEDICATION = "check_medication"
    EMERGENCY_ASSESSMENT = "emergency_assessment"
    WELLNESS_GUIDANCE = "wellness_guidance"
    TOOL = "tool"
    END = "finished"


class HealthAgent(ABC):
    """
    Base class for health-focused AI agents.

    Provides core functionality for health consultations with built-in
    medical safety measures and compliance features.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        tools: list[BaseTool],
        callbacks: list[AsyncCallbackHandler] | None = None,
        detailed_logs: bool = False,
        log_response_max_chars: int = 1000,
        enable_medical_disclaimer: bool = True,
    ) -> None:
        logger.debug("Initializing Health Agent")
        self.llm = llm
        self.tools = tools
        self.callbacks = callbacks or []
        self.detailed_logs = detailed_logs
        self.log_response_max_chars = log_response_max_chars
        self.enable_medical_disclaimer = enable_medical_disclaimer
        self.graph = None

        # Health-specific initialization
        self._initialize_health_features()

    def _initialize_health_features(self):
        """Initialize health-specific features and safety measures."""
        if self.enable_medical_disclaimer:
            logger.info("Health Agent initialized with medical disclaimer enabled")

        # Add health-specific safety validations
        self._validate_health_tools()

    def _validate_health_tools(self):
        """Validate that tools are appropriate for health use."""
        for tool in self.tools:
            if hasattr(tool, "medical_approved") and not tool.medical_approved:
                logger.warning(
                    f"Tool {tool.name} not medically approved for health consultations"
                )


# Alias for backward compatibility
BaseAgent = HealthAgent


class AgentDecision(Enum):
    """Legacy decision types for backward compatibility."""

    TOOL = "tool"
    END = "finished"

    async def _stream_llm(
        self,
        runnable: Any,
        inputs: dict[str, Any],
        config: RunnableConfig | None = None,
    ) -> AIMessage:
        """
        Stream from LLM runnable. Retry logic is handled automatically by the underlying LLM client.

        Parameters
        ----------
        runnable : Any
            The LLM runnable (prompt | llm or similar)
        inputs : Dict[str, Any]
            The inputs to pass to the runnable
        config : RunnableConfig | None
            The config to pass to the runnable (should include callbacks)

        Returns
        -------
        AIMessage
            The LLM response
        """
        output_message = ""
        async for event in runnable.astream(inputs, config=config):
            output_message += event.content

        return AIMessage(content=output_message)

    async def _call_llm(self, messages: list[BaseMessage]) -> AIMessage:
        """
        Call the LLM directly. Retry logic is handled automatically by the underlying LLM client.

        Parameters
        ----------
        messages : list[BaseMessage]
            The messages to send to the LLM

        Returns
        -------
        AIMessage
            The LLM response
        """
        response = await self.llm.ainvoke(messages)
        return AIMessage(content=str(response.content))

    async def _call_tool(
        self,
        tool: BaseTool,
        tool_input: dict[str, Any] | str,
        config: RunnableConfig | None = None,
        max_retries: int = 3,
    ) -> ToolMessage:
        """
        Call a tool with retry logic and error handling.

        Parameters
        ----------
        tool : BaseTool
            The tool to call
        tool_input : Union[Dict[str, Any], str]
            The input to pass to the tool
        config : RunnableConfig | None
            The config to pass to the tool
        max_retries : int
            Maximum number of retry attempts (default: 3)

        Returns
        -------
        ToolMessage
            The tool response
        """
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                response = await tool.ainvoke(tool_input, config=config)

                # Handle empty responses
                if response is None or (isinstance(response, str) and response == ""):
                    return ToolMessage(
                        name=tool.name,
                        tool_call_id=tool.name,
                        content=f"The tool {tool.name} provided an empty response.",
                    )

                # ToolMessage only accepts str or list[str | dict] as content.
                # Convert into list if the response is a dict.
                if isinstance(response, dict):
                    response = [response]

                return ToolMessage(
                    name=tool.name, tool_call_id=tool.name, content=response
                )

            except Exception as e:
                last_exception = e

                # If this was the last attempt, don't sleep
                if attempt == max_retries:
                    break

                logger.warning(
                    "%s Tool call attempt %d/%d failed for tool %s: %s",
                    AGENT_LOG_PREFIX,
                    attempt,
                    max_retries,
                    tool.name,
                    str(e),
                )

                # Exponential backoff: 2^attempt seconds
                sleep_time = 2**attempt
                logger.debug(
                    "%s Retrying tool call for %s in %d seconds...",
                    AGENT_LOG_PREFIX,
                    tool.name,
                    sleep_time,
                )
                await asyncio.sleep(sleep_time)

        # All retries exhausted, return error message
        error_content = (
            "Tool call failed after all retry attempts. Last error: %s"
            % str(last_exception)
        )
        logger.error("%s %s", AGENT_LOG_PREFIX, error_content, exc_info=True)
        return ToolMessage(
            name=tool.name,
            tool_call_id=tool.name,
            content=error_content,
            status="error",
        )

    def _log_tool_response(
        self, tool_name: str, tool_input: Any, tool_response: str
    ) -> None:
        """
        Log tool response with consistent formatting and length limits.

        Parameters
        ----------
        tool_name : str
            The name of the tool that was called
        tool_input : Any
            The input that was passed to the tool
        tool_response : str
            The response from the tool
        """
        if self.detailed_logs:
            # Truncate tool response if too long
            display_response = (
                tool_response[: self.log_response_max_chars]
                + "...(rest of response truncated)"
                if len(tool_response) > self.log_response_max_chars
                else tool_response
            )

            # Format the tool input for display
            tool_input_str = str(tool_input)

            tool_response_log_message = TOOL_CALL_LOG_MESSAGE % (
                tool_name,
                tool_input_str,
                display_response,
            )
            logger.info(tool_response_log_message)

    def _parse_json(self, json_string: str) -> dict[str, Any]:
        """
        Safely parse JSON with graceful error handling.
        If JSON parsing fails, returns an empty dict or error info.

        Parameters
        ----------
        json_string : str
            The JSON string to parse

        Returns
        -------
        Dict[str, Any]
            The parsed JSON or error information
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.warning(
                "%s JSON parsing failed, returning the original string: %s",
                AGENT_LOG_PREFIX,
                str(e),
            )
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "original_string": json_string,
            }
        except Exception as e:
            logger.warning(
                "%s Unexpected error during JSON parsing: %s", AGENT_LOG_PREFIX, str(e)
            )
            return {
                "error": f"Unexpected parsing error: {str(e)}",
                "original_string": json_string,
            }

    def _get_chat_history(self, messages: list[BaseMessage]) -> str:
        """
        Get the chat history excluding the last message.

        Parameters
        ----------
        messages : list[BaseMessage]
            The messages to get the chat history from

        Returns
        -------
        str
            The chat history excluding the last message
        """
        return "\n".join(
            [f"{message.type}: {message.content}" for message in messages[:-1]]
        )

    @abstractmethod
    async def _build_graph(self, state_schema: type) -> CompiledGraph:
        pass
