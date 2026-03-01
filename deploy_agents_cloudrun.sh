#!/bin/bash
# Deploy all 5 travel agents to Cloud Run
# Usage: ./deploy_agents_cloudrun.sh

set -e

PROJECT_ID="a2a-agent-engine-488515"
REGION="us-central1"

echo "=== Enabling required APIs ==="
gcloud services enable aiplatform.googleapis.com \
                       run.googleapis.com \
                       cloudbuild.googleapis.com \
                       cloudresourcemanager.googleapis.com \
                       --project=$PROJECT_ID

echo ""
echo "=== Deploying Hotel Agent (LangGraph) ==="
gcloud run deploy hotel-agent \
    --source remote_travel_agents/hotel_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

HOTEL_URL=$(gcloud run services describe hotel-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Hotel Agent deployed at: $HOTEL_URL"

# Update HOST_OVERRIDE so the AgentCard returns the correct public URL
gcloud run services update hotel-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$HOTEL_URL

echo ""
echo "=== Deploying Flight Agent (CrewAI) ==="
gcloud run deploy flight-agent \
    --source remote_travel_agents/flight_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

FLIGHT_URL=$(gcloud run services describe flight-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Flight Agent deployed at: $FLIGHT_URL"

gcloud run services update flight-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$FLIGHT_URL

echo ""
echo "=== Deploying Train Agent (LangGraph) ==="
gcloud run deploy train-agent \
    --source remote_travel_agents/train_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

TRAIN_URL=$(gcloud run services describe train-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Train Agent deployed at: $TRAIN_URL"

gcloud run services update train-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$TRAIN_URL

echo ""
echo "=== Deploying Ticket Agent (CrewAI) ==="
gcloud run deploy ticket-agent \
    --source remote_travel_agents/ticket_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

TICKET_URL=$(gcloud run services describe ticket-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Ticket Agent deployed at: $TICKET_URL"

gcloud run services update ticket-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$TICKET_URL

echo ""
echo "=== Deploying Restaurant Agent (Google GenAI SDK) ==="
gcloud run deploy restaurant-agent \
    --source remote_travel_agents/restaurant_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE

RESTAURANT_URL=$(gcloud run services describe restaurant-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Restaurant Agent deployed at: $RESTAURANT_URL"

gcloud run services update restaurant-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$RESTAURANT_URL

echo ""
echo "=== Deploying Merchandise Agent (Google GenAI SDK) ==="
gcloud run deploy merchandise-agent \
    --source remote_travel_agents/merchandise_agent \
    --port=8080 \
    --allow-unauthenticated \
    --min-instances 1 \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID

MERCHANDISE_URL=$(gcloud run services describe merchandise-agent --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "Merchandise Agent deployed at: $MERCHANDISE_URL"

gcloud run services update merchandise-agent \
    --region $REGION \
    --project $PROJECT_ID \
    --update-env-vars HOST_OVERRIDE=$MERCHANDISE_URL

echo ""
echo "=========================================="
echo "All agents deployed successfully!"
echo "=========================================="
echo ""
echo "Agent URLs:"
echo "  HOTEL_AGENT_URL=$HOTEL_URL"
echo "  FLIGHT_AGENT_URL=$FLIGHT_URL"
echo "  TRAIN_AGENT_URL=$TRAIN_URL"
echo "  TICKET_AGENT_URL=$TICKET_URL"
echo "  RESTAURANT_AGENT_URL=$RESTAURANT_URL"
echo "  MERCHANDISE_AGENT_URL=$MERCHANDISE_URL"
echo ""
echo "Verify agent cards:"
echo "  curl $HOTEL_URL/.well-known/agent.json"
echo "  curl $FLIGHT_URL/.well-known/agent.json"
echo "  curl $TRAIN_URL/.well-known/agent.json"
echo "  curl $TICKET_URL/.well-known/agent.json"
echo "  curl $RESTAURANT_URL/.well-known/agent.json"
echo "  curl $MERCHANDISE_URL/.well-known/agent.json"
echo ""
echo "Add these URLs to your .env file for the concierge deployment."
