# Doctor Intelligent Tool for Clinical Help (Dr. Itch)
A Conversational AI Framework for Medical Education: Integrating Literature, Clinical Data, and Real-Time Research

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- MySQL database access

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dr_itch
```

### 2. Environment Setup

Create a `.env` file in the root directory with your database configuration:

```env
DB_HOST=your_mysql_host
DB_PORT=3306
DB_NAME=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### 3. Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or install individual packages:

```bash
pip install mysql-connector-python pandas sqlalchemy python-dotenv passlib
```

### 4. Docker Network Setup

Create the required external Docker network:

```bash
docker network create shared-net
```

### 5. Database Preparation

Ensure your MySQL database contains the required `doctors_registration` table in the `PRD01` schema with the following columns:
- `EmailId`
- `password`
- `Fname`
- `Lname`

### 6. Initial Data Sync

#### prior to run the script. please locate the pre-created database webui.db 
default username/password for Adminin

- username: admin@test.ca
- password: dti6302

Run the hospital data synchronization script:

```bash
python ehospital_sync.py
```

This script will:
- Connect to your MySQL database
- Extract doctor registration data
- Hash passwords using bcrypt
- Create/update SQLite database (`webui.db`)
- Sync user data for the application

### 7. Start Services

Launch the Docker services:

```bash
docker-compose up -d
```

This will start:
- **N8n Workflow Automation** on port 5678
- **Open WebUI** on port 3200

### 8. Access the Application

- **Open WebUI**: http://localhost:3200
- **N8n**: http://localhost:5678  
You can configure your custom domain.

### Configuration Notes

#### N8n Configuration
- Host: `n8n.parainsight.com`
- Protocol: HTTPS
- Timezone: Asia/Ho_Chi_Minh
- Max payload size: 50MB
- Community packages enabled

#### Open WebUI Configuration
- Runs on port 8080 inside container (mapped to 3200 on host)
- SQLite database mounted from host at `/root/openwebui-docker/webui.db`
- Connected to host network for internal services access

### Troubleshooting

1. **Database Connection Issues**: Verify your `.env` file contains correct database credentials
2. **Docker Network Error**: Ensure the `shared-net` network exists: `docker network create shared-net`
3. **Permission Issues**: Check that the SQLite database file path is accessible
4. **Port Conflicts**: Ensure ports 3200 and 5678 are available on your system

### File Structure

```
dr_itch/
├── README.md
├── ehospital_sync.py       # Data synchronization script
├── docker-compose.yml     # Docker services configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
└── webui.db              # SQLite database (generated)
```
