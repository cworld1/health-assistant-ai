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

import json
import logging

from pydantic import Field

from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.component_ref import LLMRef
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class HealthDocumentSearchToolConfig(FunctionBaseConfig, name="health_document_search"):
    """
    This tool retrieves relevant health and medical documents for a given user query. The input query is mapped to the most appropriate
    health knowledge collection database. This will return relevant medical documents from the selected collection.
    """

    base_url: str = Field(
        description="The base url used to connect to the health knowledge database."
    )
    top_k: int = Field(
        default=4,
        description="The number of health documents to return from the database.",
    )
    timeout: int = Field(
        default=60,
        description="The timeout configuration to use when sending requests.",
    )
    llm_name: LLMRef = Field(
        description=(
            "The name of the llm client to instantiate to determine most appropriate "
            "health knowledge collection."
        )
    )
    collection_names: list = Field(
        default=[
            "health_symptoms",
            "health_treatments",
            "health_drugs",
            "health_conditions",
        ],
        description="The list of available health knowledge collection names.",
    )
    collection_descriptions: list = Field(
        default=[
            "Medical symptoms and diagnostic information",
            "Treatment protocols and medical procedures",
            "Drug information, interactions and dosages",
            "Medical conditions and disease information",
        ],
        description=(
            "Health collection descriptions that map to collection names by "
            "index position."
        ),
    )


@register_function(config_type=HealthDocumentSearchToolConfig)
async def health_document_search(
    config: HealthDocumentSearchToolConfig, builder: Builder
):
    import httpx
    from langchain_core.messages import HumanMessage
    from langchain_core.messages import SystemMessage
    from langchain_core.pydantic_v1 import BaseModel
    from langchain_core.pydantic_v1 import Field

    # define collection store
    # create a list of tuples using enumerate()
    tuples = [
        (key, value)
        for i, (key, value) in enumerate(
            zip(config.collection_names, config.collection_descriptions)
        )
    ]

    # convert list of tuples to dictionary using dict()
    collection_store = dict(tuples)

    # define collection class and force it to accept only valid collection names
    class HealthCollectionName(BaseModel):
        collection_name: str = Field(
            description="The appropriate health knowledge collection name for the medical question."
        )

    class HealthDocumentSearchOutput(BaseModel):
        collection_name: str
        documents: str

    # define prompt template
    prompt_template = f"""You are a health assistant agent that helps users find the right medical knowledge collection based on the health question.
Here are the available list of health collections (formatted as collection_name: collection_description): \n
({collection_store})
\nFirst, analyze the available health collections and their descriptions.
Then, select the most appropriate medical collection for the user's health query.
Return only the name of the predicted health collection."""

    async with httpx.AsyncClient(
        headers={"accept": "application/json", "Content-Type": "application/json"},
        timeout=config.timeout,
    ) as client:

        async def _health_document_search(query: str) -> HealthDocumentSearchOutput:
            """
            This tool retrieve relevant health and medical context for the given question
            Args:
                query (str): The health question for which we need to search medical knowledge collections.
            """
            # log query
            logger.debug("Q: %s", query)

            # Set Template
            sys_message = SystemMessage(content=prompt_template)

            # define LLM and generate response
            llm = await builder.get_llm(
                llm_name=config.llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN
            )
            structured_llm = llm.with_structured_output(HealthCollectionName)
            query_string = (
                f"Get relevant health information for this medical query: {query}"
            )
            llm_pred = await structured_llm.ainvoke(
                [sys_message] + [HumanMessage(content=query_string)]
            )

            logger.info("Predicted LLM Collection: %s", llm_pred)

            # configure params for RAG endpoint and doc search
            url = f"{config.base_url}/search"
            payload = {
                "query": query,
                "top_k": config.top_k,
                "collection_name": llm_pred.collection_name,
            }

            # send configured payload to running chain server
            logger.debug("Sending request to the RAG endpoint %s", url)
            response = await client.post(url, content=json.dumps(payload))

            response.raise_for_status()
            results = response.json()

            if len(results["chunks"]) == 0:
                return HealthDocumentSearchOutput(
                    collection_name=llm_pred.collection_name, documents=""
                )

            # parse docs from Langchain Document object to string
            parsed_docs = []

            # iterate over results and store parsed content
            for doc in results["chunks"]:
                source = doc["filename"]
                page = doc.get("page", "")
                page_content = doc["content"]
                parsed_document = f'<Document source="{source}" page="{page}"/>\n{page_content}\n</Document>'
                parsed_docs.append(parsed_document)

            # combine parsed documents into a single string
            internal_search_docs = "\n\n---\n\n".join(parsed_docs)
            return HealthDocumentSearchOutput(
                collection_name=llm_pred.collection_name, documents=internal_search_docs
            )

        yield FunctionInfo.from_fn(
            _health_document_search,
            description=(
                "This tool retrieves relevant health and medical documents for a given user query."
                "The input query is mapped to the most appropriate health knowledge collection database"
                "This will return relevant medical documents from the selected collection."
            ),
        )


# Compatibility aliases
MilvusDocumentSearchToolConfig = HealthDocumentSearchToolConfig
document_search = health_document_search
