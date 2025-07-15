# PDFQA-Streamlit-LangChain-K8s

## Project Overview
This project implements a sophisticated PDF question-answering (QA) chatbot utilizing Retrieval-Augmented Generation (RAG) techniques. The application is developed with Streamlit for an interactive user interface, leverages LangChain for natural language processing and retrieval, and integrates FAISS for vector storage, Sentence-Transformers for embeddings, and Ollama for model support (e.g., LLaMA). The solution is deployed on Kubernetes Minikube, a lightweight local Kubernetes environment, with MongoDB serving as the persistent storage for chat history. This setup enables efficient processing of PDF uploads, accurate query responses, and scalable deployment for development and testing purposes.

## Key Features
- Efficient extraction and processing of textual data from PDF files using PyPDF2.
- Accurate query response generation utilizing LangChain, Sentence-Transformers, and Ollama.
- Persistent storage of chat interactions within a MongoDB database via PyMongo.
- Vector-based search capabilities provided by FAISS-CPU.
- Interactive user interface developed with Streamlit.
- Scalable deployment and management facilitated through Kubernetes Minikube with horizontal pod autoscaling.

## System Requirements
- **Kubernetes Minikube**: Installation and active operation are mandatory.
- **kubectl**: Essential for Kubernetes cluster management.
- **MongoDB**: A functional MongoDB instance, either local or remote, is required.
- **Docker**: Necessary for containerizing the application.
- **Python**: Required environment (version specified in `requirements.txt`).
- **Git**: Essential for version control and repository synchronization.
- **Dependencies**: Ensure the following Python packages are installed via `requirements.txt`:
  - Streamlit
  - PyPDF2
  - LangChain
  - LangChain-Community
  - Faiss-CPU
  - Sentence-Transformers
  - Ollama
  - PyMongo

## Installation Procedure
1. Retrieve the project repository:
   ```
   git clone https://github.com/rvmeesa/PDFQA-Streamlit-LangChain-K8s.git
   cd PDFQA-Streamlit-LangChain-K8s
   ```
2. Install requisite dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Initiate Minikube:
   ```
   minikube start --driver=docker
   ```
4. Construct and deploy Docker images:
   ```
   docker build -t rag-chatbot:latest .
   kubectl apply -f .
   ```
5. Confirm deployment status:
   ```
   kubectl get pods
   ```

## Configuration Guidelines
- Update the `serviceAccountKey` file with valid credentials if required (recommended to use environment variables for security).
- Configure `mongodb-deployment.yaml` and `mongodb-service.yaml` with appropriate MongoDB connection parameters.
- Adjust `web-deployment.yaml`, `web-service.yaml`, and `web-hpa.yaml` to align with application service and autoscaling requirements.

## Operational Instructions
1. Upload PDF documents to the designated `uploaded` directory or as specified by the application.
2. Access the service endpoint provided by Minikube (e.g., via `minikube service web-service --url`).
3. Submit queries via the Streamlit interface and review responses, with data stored in MongoDB.

## Directory Structure
- `.git/`: Repository metadata managed by Git.
- `faiss_index/`: Storage for FAISS-CPU index files used in vector search.
- `uploaded/`: Repository for uploaded PDF documents.
- `.gitignore`: Defines exclusions from version control (e.g., `serviceAccountKey.json`).
- `app/`: Contains core application source code (Python files, including Streamlit and LangChain implementations).
- `Dockerfile`: Specification for the Docker image.
- `kubectl/`: Additional Kubernetes configuration files (if applicable).
- `mongodb-deployment.yaml`, `mongodb-service.yaml`, `pv-mongodb.yaml`, `pvc-mongodb.yaml`: Configuration files for MongoDB deployment and persistence.
- `README.md`: This documentation.
- `requirements.txt`: Enumeration of Python dependencies, including Streamlit, PyPDF2, LangChain, LangChain-Community, Faiss-CPU, Sentence-Transformers, Ollama, and PyMongo.
- `web-deployment.yaml`, `web-hpa.yaml`, `web-service.yaml`: Configuration files for web application deployment and autoscaling.

## Docker Image
- Image: `rag-chatbot:latest` (or `yourdockerhubusername/rag-chatbot:latest` if pushed to Docker Hub).
- Build the image locally using the provided `Dockerfile` and push to Docker Hub if required for remote deployment.

## Deployment Instructions
1. Start Minikube:
   ```
   minikube start --driver=docker
   ```
2. Apply Kubernetes configurations:
   ```
   kubectl apply -f pv-mongodb.yaml
   kubectl apply -f pvc-mongodb.yaml
   kubectl apply -f mongodb-deployment.yaml
   kubectl apply -f mongodb-service.yaml
   kubectl apply -f web-deployment.yaml
   kubectl apply -f web-service.yaml
   kubectl apply -f web-hpa.yaml
   ```
3. Build and deploy the Docker image:
   ```
   docker build -t rag-chatbot:latest .
   kubectl set image deployment/web-deployment web=rag-chatbot:latest
   ```
4. Verify deployment:
   ```
   kubectl get pods
   kubectl get services
   ```

