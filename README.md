# WhatsApp Campaign Automation System

## 🎯 Project Overview

A comprehensive WhatsApp automation platform built for BorderPlus to streamline international nursing career lead outreach. This system automates personalized messaging, tracks delivery status, manages follow-ups, and provides real-time analytics through an intuitive dashboard.

**Assignment Context**: At BorderPlus, we receive dozens of candidate leads daily who are interested in international nursing careers. This solution automates the first point of contact via WhatsApp to improve response rates and operational efficiency.

## 🌟 Key Features

### Core Functionality
- **Automated Lead Processing**: Bulk WhatsApp messaging from CSV lead lists
- **Personalized Messaging**: Dynamic message templates based on interest areas
- **Real-time Status Tracking**: Live delivery status monitoring and updates
- **Intelligent Follow-ups**: Automatic re-engagement after 10 minutes of no response
- **Retry Mechanism**: Up to 5 retry attempts for failed messages with exponential backoff
- **Reply Management**: Automatic reply detection and conversation tracking
- **Excel Logging**: Comprehensive audit trail with atomic write operations

### Advanced Features
- **Thread-safe Operations**: Concurrent message processing with proper synchronization
- **Mock API Integration**: Realistic WhatsApp API simulation for testing
- **Real-time Dashboard**: Live metrics and campaign monitoring
- **Status Automation**: Background monitoring with automatic status updates
- **Data Export**: Full campaign logs downloadable in Excel format

## 🏗️ Architecture

### System Components

```
whatsapp-automation/
├── data/
│   ├── leads.csv                 # Lead data with names, phones, interests
│   └── delivery_log.xlsx         # Auto-generated campaign logs
├── templates/
│   └── message_templates.json    # Personalized message templates
├── src/
│   ├── mock_api_server.py        # FastAPI mock WhatsApp service
│   ├── mock_api_client.py        # API client wrapper
│   ├── logger.py                 # Excel-based logging system
│   └── app.py                    # Streamlit frontend dashboard
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

### Technology Stack

**Backend**
- **Python 3.8+**: Core programming language
- **FastAPI**: High-performance API framework for mock service
- **Pandas**: Data manipulation and Excel operations
- **Threading**: Concurrent background processing
- **Requests**: HTTP client for API communication

**Frontend**
- **Streamlit**: Interactive web dashboard
- **Real-time Updates**: Auto-refresh functionality
- **Data Visualization**: Metrics and status displays

**Data Storage**
- **Excel (XLSX)**: Structured logging with atomic operations
- **CSV**: Lead data import format
- **JSON**: Message template configuration

**Infrastructure**
- **Uvicorn**: ASGI server for FastAPI
- **Mock API**: Realistic WhatsApp API simulation
- **Thread Management**: Background monitoring and automation

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data files**
   - Ensure `data/leads.csv` contains your lead data
   - Template file `templates/message_templates.json` is pre-configured

4. **Start the mock API server**
   ```bash
   uvicorn src.mock_api_server:app --port 8000
   ```

5. **Launch the dashboard**
   ```bash
   streamlit run src/app.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:8501`
   - The dashboard should show "Mock API Connected" status

## 📊 Data Formats

### Lead Data Structure (`data/leads.csv`)
```csv
name,phone,interest_area
Priya Sharma,+919876543210,Nursing in Germany
Rajesh Kumar,+919876543211,Healthcare Training
Anita Patel,+919876543212,International Nursing
```

**Fields:**
- `name`: Lead's full name for personalization
- `phone`: WhatsApp number with country code (+91 for India)
- `interest_area`: Category for template selection

### Message Templates (`templates/message_templates.json`)
```json
{
    "Nursing in Germany": [
        "Hi {name}! 🌟 Ready to start your nursing career in Germany?",
        "Hello {name}! 👋 Interested in German nursing opportunities?"
    ],
    "default": [
        "Hi {name}! 👋 Thanks for your interest in international healthcare careers."
    ]
}
```

## 🎯 Usage Guide

### Running a Campaign

1. **Prepare Lead Data**: Upload your leads to `data/leads.csv`
2. **Customize Templates**: Modify `templates/message_templates.json` as needed
3. **Start Services**: Launch both mock API server and Streamlit app
4. **Monitor Connection**: Verify "Mock API Connected" status
5. **Launch Campaign**: Click "🚀 Send WhatsApp Campaign"
6. **Monitor Progress**: Watch real-time status updates and metrics

### Dashboard Features

**Campaign Control Panel:**
- Connection status indicator
- Lead count and preview
- Campaign launch button
- Progress tracking

**Real-time Analytics:**
- ✅ Delivered messages count
- ❌ Failed messages count
- ⏳ Queued messages count
- 💬 Replies received count
- 📞 Follow-ups sent count

**Manual Controls:**
- 🔄 Refresh Status: Update delivery status
- 🔄 Retry Failed Now: Force retry failed messages
- 📞 Send Follow-ups: Trigger follow-up messages

## 🔧 Technical Implementation

### Mock API Endpoints

**POST `/mock/send`**
- Simulates WhatsApp message sending
- Returns message ID and queued status
- Validates phone number format

**GET `/mock/status/{message_id}`**
- Checks delivery status
- 70% success rate simulation
- Status transitions: queued → sent/failed

**GET `/mock/reply/{message_id}`**
- Simulates user replies
- 30% reply rate for successful messages
- Suppressed replies for specific test numbers

### Background Automation

The system runs continuous background processes:

1. **Status Monitoring** (every 30 seconds):
   - Updates queued message status
   - Checks for new replies
   - Triggers follow-ups when appropriate

2. **Retry Logic**:
   - Attempts up to 5 retries for failed messages
   - Exponential backoff timing
   - Automatic status updates

3. **Follow-up Automation**:
   - Triggers after 10 minutes of no reply
   - Personalized follow-up messages
   - Status tracking for follow-ups

### Data Safety

- **Thread-safe operations** using locks
- **Atomic file writes** to prevent corruption
- **Error handling** with graceful degradation
- **Data validation** for phone numbers and templates

## 📈 Performance Characteristics

- **Concurrent Processing**: Thread-safe bulk messaging
- **Rate Limiting**: 0.5-second delays between messages
- **Memory Efficient**: Streaming data processing
- **Fault Tolerant**: Comprehensive error handling
- **Scalable Design**: Modular architecture for easy extension

## 🧪 Testing Strategy

### Mock API Benefits
- **Realistic Simulation**: Actual API behavior patterns
- **Controlled Testing**: Predictable success/failure rates
- **Cost-Effective**: No charges for testing
- **Rapid Iteration**: Immediate feedback loops

### Test Scenarios
- **Bulk messaging**: Multiple leads processing
- **Failure handling**: Network errors and retries
- **Reply simulation**: User engagement tracking
- **Follow-up logic**: Automated re-engagement

## 🚀 Areas for Enhancement (Next 2 Days)

### AI & Machine Learning Integration

**1. Intelligent Message Personalization**
- **ML-powered Content Generation**: Use GPT-4/Claude to generate contextually relevant messages based on lead profiles, previous interactions, and success patterns
- **Sentiment Analysis**: Analyze reply sentiment to trigger appropriate follow-up strategies
- **A/B Testing Framework**: ML-driven template optimization based on response rates
- **Dynamic Template Selection**: AI chooses best-performing templates for each lead segment

**2. Predictive Analytics**
- **Lead Scoring**: ML model to predict conversion probability based on demographics, engagement patterns, and response timing
- **Optimal Timing Prediction**: AI determines best send times for each lead based on historical engagement data
- **Churn Prediction**: Identify leads likely to disengage and trigger retention campaigns
- **Response Rate Forecasting**: Predict campaign performance before execution

**3. Natural Language Processing**
- **Intent Classification**: Automatically categorize replies (interested, not interested, needs info, etc.)
- **Auto-Response Generation**: AI-powered contextual responses to common queries
- **Language Detection**: Multi-language support with automatic translation
- **Conversation Summarization**: AI-generated summaries of lead interactions for sales teams

### MLOps & Automation Infrastructure

**4. Model Lifecycle Management**
- **MLflow Integration**: Track model experiments, versions, and performance metrics
- **Automated Model Training**: Scheduled retraining based on new interaction data
- **Model Deployment Pipeline**: CI/CD for ML models with A/B testing
- **Performance Monitoring**: Real-time model drift detection and alerting

**5. Advanced Automation Workflows**
- **Apache Airflow**: Orchestrate complex data pipelines and ML workflows
- **Event-Driven Architecture**: Kafka/RabbitMQ for real-time event processing
- **Webhook Integration**: Real-time status updates from actual WhatsApp APIs
- **Auto-scaling**: Kubernetes-based scaling based on campaign volume

**6. Data Engineering & Analytics**
- **Data Lake Architecture**: Store all interactions for historical analysis
- **Real-time Streaming**: Apache Kafka for live data processing
- **Feature Store**: Centralized feature management for ML models
- **Data Quality Monitoring**: Automated data validation and anomaly detection

### Smart Automation Features

**7. Intelligent Campaign Management**
- **Auto-Campaign Optimization**: AI adjusts send rates, timing, and content based on real-time performance
- **Smart Segmentation**: ML-based lead clustering for targeted messaging
- **Dynamic Follow-up Sequences**: AI-powered multi-step nurture campaigns
- **Conversion Attribution**: Track lead journey from first message to conversion

**8. Advanced Monitoring & Observability**
- **Prometheus/Grafana**: Comprehensive metrics and alerting
- **Distributed Tracing**: End-to-end request tracking with Jaeger
- **Log Aggregation**: ELK stack for centralized logging and analysis
- **Anomaly Detection**: ML-powered detection of unusual patterns

**9. Integration & Scalability**
- **Microservices Architecture**: Break system into scalable, independent services
- **API Gateway**: Centralized API management with rate limiting and authentication
- **Cloud-Native Deployment**: Docker containers with Kubernetes orchestration
- **Multi-Channel Support**: Extend to SMS, Email, and other communication channels

### Specific Implementation Roadmap

**Day 1: AI/ML Foundation**
- Implement basic sentiment analysis on replies
- Add lead scoring based on engagement patterns
- Create A/B testing framework for message templates
- Deploy MLflow for model tracking

**Day 2: Automation & Infrastructure**
- Set up Airflow for workflow orchestration
- Implement real-time streaming with Kafka
- Add comprehensive monitoring with Prometheus
- Create automated model retraining pipeline

## 🔐 Production Considerations

### Security
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Data Encryption**: Encrypt sensitive data at rest and in transit
- **API Security**: Rate limiting and input validation

### Scalability
- **Database Migration**: Move from Excel to PostgreSQL/MongoDB
- **Caching Layer**: Redis for frequently accessed data
- **Load Balancing**: Handle high-volume campaigns
- **Microservices**: Service-oriented architecture

### Monitoring
- **Health Checks**: System health monitoring
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging
- **Business Metrics**: Campaign performance analytics

## 🤝 Contributing

This project demonstrates proficiency in:
- **Full-stack Development**: Backend APIs, frontend dashboards
- **System Design**: Scalable, maintainable architecture
- **Data Engineering**: ETL pipelines and data processing
- **Automation**: Background processing and workflows
- **Testing**: Mock services and comprehensive error handling

