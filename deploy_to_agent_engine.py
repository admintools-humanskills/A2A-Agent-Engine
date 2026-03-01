"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv
import os
from purchasing_concierge.agent import root_agent

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

AGENT_ENGINE_RESOURCE = os.getenv("AGENT_ENGINE_RESOURCE_NAME")

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
)

DEPLOY_CONFIG = dict(
    agent_engine=adk_app,
    display_name="travel-concierge",
    requirements=[
        "google-cloud-aiplatform[agent_engines]",
        "google-adk==1.15.1",
        "a2a-sdk==0.2.16",
    ],
    extra_packages=[
        "./purchasing_concierge",
    ],
    env_vars={
        "GOOGLE_GENAI_USE_VERTEXAI": os.environ["GOOGLE_GENAI_USE_VERTEXAI"],
        "HOTEL_AGENT_URL": os.environ["HOTEL_AGENT_URL"],
        "FLIGHT_AGENT_URL": os.environ["FLIGHT_AGENT_URL"],
        "TRAIN_AGENT_URL": os.environ["TRAIN_AGENT_URL"],
        "TICKET_AGENT_URL": os.environ["TICKET_AGENT_URL"],
        "RESTAURANT_AGENT_URL": os.environ["RESTAURANT_AGENT_URL"],
        "MERCHANDISE_AGENT_URL": os.environ["MERCHANDISE_AGENT_URL"],
    },
)

if AGENT_ENGINE_RESOURCE:
    print(f"Updating existing agent engine: {AGENT_ENGINE_RESOURCE}")
    remote_app = agent_engines.update(
        resource_name=AGENT_ENGINE_RESOURCE,
        **DEPLOY_CONFIG,
    )
    print(f"Updated agent engine: {remote_app.resource_name}")
else:
    print("No AGENT_ENGINE_RESOURCE_NAME found, creating new agent engine...")
    remote_app = agent_engines.create(**DEPLOY_CONFIG)
    print(f"Created new agent engine: {remote_app.resource_name}")
    print("Add this to your .env: AGENT_ENGINE_RESOURCE_NAME=" + remote_app.resource_name)
