# ShopFlow Lite

A modern, DevOps-powered e-commerce storefront built with Flask, Supabase, and Kubernetes.

## 🏗️ Architecture

- **Frontend**: Flask web application with Jinja2 templates
- **Backend**: Supabase (PostgreSQL + Auth)
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins Pipeline

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   https://github.com/naman-shah1/devops
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r app/requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp app/.env.example app/.env
   # Edit app/.env with your Supabase credentials
   ```

4. **Run locally**
   ```bash
   cd app
   python app.py
   ```
   Visit: http://localhost:5000

### Docker Deployment

```bash
# Build and run with Docker
docker build -t shopflow-lite .
docker run -p 5000:5000 --env-file app/.env shopflow-lite
```

## 🚢 Jenkins CI/CD Pipeline

### Pipeline Features

- **Automated Testing**: Python environment setup and basic health checks
- **Security Scanning**: Dependency vulnerability checks with `safety`
- **Docker Build**: Multi-stage container builds
- **Kubernetes Deployment**: Rolling updates with health checks
- **Verification**: Post-deployment health checks and monitoring

### Jenkins Setup

1. **Prerequisites**
   - Jenkins with Kubernetes plugin
   - Docker registry access
   - Kubernetes cluster access

2. **Configure Jenkins**
   ```bash
   # Run the setup script
   chmod +x setup-jenkins.sh
   ./setup-jenkins.sh
   ```

3. **Update Jenkinsfile**
   - Replace `your-registry.com` with your Docker registry URL
   - Update Git repository URL if needed

4. **Pipeline Stages**
   - **Checkout**: Pull latest code from Git
   - **Setup**: Install Python dependencies
   - **Test**: Run basic application tests
   - **Security**: Scan for vulnerabilities
   - **Build**: Create Docker image
   - **Deploy**: Update Kubernetes deployment
   - **Verify**: Health checks and monitoring

### Kubernetes Resources

- **Deployment**: `k8s/deployment.yaml` - Application pods with health checks
- **Service**: `k8s/service.yaml` - NodePort service on port 30007
- **Secret**: `k8s/secret.yaml` - Supabase credentials

## 🔧 Configuration

### Environment Variables

Create `app/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Supabase Setup

1. Create a new Supabase project
2. Create a `products` table:
   ```sql
   CREATE TABLE products (
     id SERIAL PRIMARY KEY,
     name TEXT NOT NULL,
     price DECIMAL(10,2) NOT NULL,
     image_url TEXT
   );
   ```
3. Insert sample data and update the environment variables

## 📊 Monitoring

- Health check endpoint: `GET /health`
- Application logs: `kubectl logs -l app=shopflow-lite`
- Pod status: `kubectl get pods -l app=shopflow-lite`

## 🧪 Testing

```bash
cd app
python -m pytest  # If pytest is configured
# Or basic import test
python -c "import app; print('✅ App loads successfully')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure pipeline passes
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework for the web application
- Supabase for backend services
- Kubernetes for container orchestration
- Jenkins for CI/CD automation
