# RAG PDF Question Answer Chatbot Kubernetes Deployment

## Overview
This project deploys a Streamlit-based RAG chatbot using FAISS, LLaMA, and MongoDB on a Minikube cluster. The chatbot processes PDF uploads and answers questions, storing conversation history in MongoDB.

## Docker Image
- Image: `rag-chatbot:latest` (or `yourdockerhubusername/rag-chatbot:latest` if pushed to Docker Hub).

## Files
- `app.py`: Streamlit application code.
- `Dockerfile`: Docker configuration for the web server.
- `requirements.txt`: Python dependencies.
- `pv-mongodb.yaml`: Persistent Volume for MongoDB.
- `pvc-mongodb.yaml`: Persistent Volume Claim for MongoDB.
- `mongodb-deployment.yaml`: MongoDB Deployment (1 replica).
- `mongodb-service.yaml`: MongoDB NodePort Service.
- `web-deployment.yaml`: Web Server Deployment (3 replicas).
- `web-service.yaml`: Web Server LoadBalancer Service.
- `web-hpa.yaml`: HorizontalPodAutoscaler for web server.

## Deployment Instructions
1. Start Minikube:
   ```bash
   minikube start --driver=docker