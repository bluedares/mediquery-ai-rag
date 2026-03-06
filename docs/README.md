# MediQuery AI - Documentation Index

Complete documentation for the MediQuery AI RAG system.

---

## 📚 **Documentation Structure**

### **01-setup/** - Setup & Configuration
Complete guides for setting up the development environment and services.

- **QUICK_START.md** - Get started in 5 minutes
- **COMPLETE_SETUP_GUIDE.md** - Comprehensive setup instructions
- **AWS_SETUP_GUIDE.md** - AWS account and service setup
- **AWS_CREDENTIALS_SETUP.md** - AWS credentials configuration
- **AWS_BEDROCK_SETUP.md** - AWS Bedrock setup and configuration
- **ANTHROPIC_DIRECT_SETUP.md** - Direct Anthropic API setup (temporary)
- **CHROMADB_SETUP.md** - ChromaDB vector database setup
- **OPENSEARCH_SETUP.md** - OpenSearch setup (production)

### **02-architecture/** - System Architecture
Technical architecture and design documentation.

- **03-ARCHITECTURE.md** - Complete system architecture
- **RAG_FLOW_EXPLAINED.md** - RAG system flow and implementation
- **PDF_UPLOAD_FLOW.md** - Document upload and processing flow
- **VECTOR_DB_COMPARISON.md** - Vector database options comparison
- **DOCUMENT_ISOLATION_ANALYSIS.md** - Document isolation design
- **OPENSEARCH_ARCHITECTURE.md** - OpenSearch architecture details

### **03-deployment/** - Deployment & Demo
Deployment guides and demo instructions.

- **DEPLOYMENT_GUIDE.md** - Production deployment guide
- **DEMO_GUIDE.md** - Demo preparation and execution
- **FINAL_DEMO_GUIDE.md** - Final demo checklist

### **04-troubleshooting/** - Troubleshooting
Common issues and solutions.

- **AWS_SUPPORT_REQUEST.md** - AWS support request tracking
- **BEDROCK_ANALYSIS.md** - Bedrock access analysis
- **BEDROCK_STATUS.md** - Current Bedrock status
- **PAYMENT_TROUBLESHOOTING.md** - AWS payment issues

### **05-guides/** - User Guides
End-user and developer guides.

- **GET_TEST_DOCUMENTS.md** - Test document resources

### **06-analysis/** - Development Analysis
Development progress and technical analysis.

- **CURRENT_STATUS.md** - Current project status
- **PROGRESS.md** - Development progress tracking
- **IMPLEMENTATION_ANALYSIS.md** - Implementation analysis
- **IMPLEMENTATION_PLAN.md** - Implementation planning
- **DYNAMIC_HEALTH_METRICS.md** - Health metrics implementation
- **UI_CHANGES_PLAN.md** - UI changes and improvements

### **Root Documentation**
- **01-PROJECT_OVERVIEW.md** - Project overview and goals
- **02-TECH_STACK.md** - Technology stack details
- **04-REQUIREMENTS.md** - System requirements
- **05-IMPLEMENTATION_PLAN.md** - Phased implementation plan
- **06-DEBUG_TRACING_SYSTEM.md** - Debug and tracing system
- **07-PHASED_IMPLEMENTATION.md** - Implementation phases
- **08-SCALABILITY_ARCHITECTURE.md** - Scalability design

---

## 🚀 **Quick Navigation**

**Getting Started:**
1. [Quick Start](01-setup/QUICK_START.md) - 5-minute setup
2. [Complete Setup](01-setup/COMPLETE_SETUP_GUIDE.md) - Full setup guide
3. [Demo Guide](03-deployment/DEMO_GUIDE.md) - Run a demo

**Understanding the System:**
1. [Architecture](03-ARCHITECTURE.md) - System design
2. [RAG Flow](02-architecture/RAG_FLOW_EXPLAINED.md) - How RAG works
3. [Tech Stack](02-TECH_STACK.md) - Technologies used

**Troubleshooting:**
1. [Bedrock Issues](04-troubleshooting/BEDROCK_STATUS.md)
2. [AWS Setup](04-troubleshooting/AWS_SUPPORT_REQUEST.md)
3. [Payment Issues](04-troubleshooting/PAYMENT_TROUBLESHOOTING.md)

---

## 📖 **Documentation Categories**

### **For Developers:**
- Setup guides (01-setup/)
- Architecture docs (02-architecture/)
- Analysis docs (06-analysis/)

### **For DevOps:**
- Deployment guides (03-deployment/)
- Troubleshooting (04-troubleshooting/)

### **For End Users:**
- User guides (05-guides/)
- Demo guides (03-deployment/)

---

## 🔧 **Key Technologies**

- **Frontend:** React + Vite + TailwindCSS
- **Backend:** FastAPI + Python 3.9+
- **LLM:** AWS Bedrock (Claude) / Direct Anthropic API
- **Vector DB:** ChromaDB (dev) / OpenSearch (prod)
- **Embeddings:** BGE-large-en-v1.5 (1024 dimensions)
- **Storage:** AWS S3
- **Infrastructure:** AWS (Bedrock, S3, OpenSearch)

---

## 📝 **Contributing**

When adding new documentation:
1. Place in appropriate category folder
2. Update this README.md index
3. Follow naming convention: `DESCRIPTIVE_NAME.md`
4. Include clear headers and sections
5. Add to relevant quick navigation section

---

**Last Updated:** March 6, 2026  
**Version:** 1.0.0
