# 🧱 Monolith to Microservices – Product & Order Service

This project is a monolithic application structured with future microservice separation in mind. It contains two main domains:

🚀 Key Features
* **Modular Design:** Clear separation of concerns within service and API layers, promoting maintainability and scalability.
* **Containerized with Docker:** Utilizes multi-stage Docker builds optimized for production environments, ensuring consistent deployments.
* **Automated Integration Testing:** Comprehensive integration tests are executed as part of the Docker build process, guaranteeing component interoperability.
* **Flexible Database Abstraction:** Designed for easy integration with various relational databases such as PostgreSQL and MySQL.
* **Cloud-Native Ready:** Prepared for seamless deployment on major cloud platforms like AWS, GCP, and Azure leveraging Docker containerization.
* **Dedicated Service Domains:**
    * **Product Service:** Manages the lifecycle of products, including creation, retrieval, updating, deletion (CRUD), pricing strategies, and inventory management.
    * **Order Service:** Handles the entire order processing workflow, encompassing shopping cart logic, checkout procedures, and historical order management.

🧰 Prerequisites
* Python 3.11
* Docker
* Docker Compose (optional, for local development)

🧪 Running Tests
Integration tests are automatically executed during the Docker build process. To run tests manually:

```bash
pytest tests/
```

🐳 Docker Deployment
🛠️ Build the Docker Image
```bash
docker build -t ecommerce-app .
```
🚀 Run the Docker Container
```bash
docker run -d -p 8000:8000 --name ecommerce_container ecommerce-app
```

Access the application at http://localhost:8000.

🗄️ Configuring a New Database
To use a different database (e.g., PostgreSQL, MySQL):

Update Dependencies: Modify requirements.txt to include the appropriate database driver. 
For example, for PostgreSQL:psycopg2-binary.

☁️ Cloud Deployment
Deploy the Dockerized application to your preferred cloud platform. Here's a general approach:

Container Registry: Push your Docker image to a container registry (e.g., Docker Hub, AWS ECR, GCP Container Registry).

```bash
docker tag ecommerce-app your-registry/ecommerce-app
docker push your-registry/ecommerce-app
```

Provision Infrastructure: Set up the necessary infrastructure on your cloud provider (e.g., compute instances, networking, databases).

Deploy the Container: Utilize the cloud provider's container orchestration or management services to deploy the Docker container. Examples include:

AWS ECS (Elastic Container Service): For running containers at scale.
AWS EKS (Elastic Kubernetes Service): For Kubernetes-based container orchestration.
Google Cloud Run: For serverless container execution.
Azure Container Instances (ACI) / Azure Kubernetes Service (AKS): Microsoft Azure's container services.


Set Up Networking: Configure load balancers, security groups, and DNS settings to expose your application.

📄 License
This project is licensed under the MIT License.