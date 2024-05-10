
# Health Management System (HMS)

This repository contains a Flask web application for a Health Management System designed to facilitate various operations in a healthcare environment. The application supports features like user registration, role management, appointment scheduling, file uploading, and much more.

## Features

- **User Authentication**: Secure login and session management.
- **Role-Based Access Control**: Different interfaces and permissions based on user roles.
- **Appointment Management**: Schedule and manage appointments.
- **File Uploads**: Securely upload and manage files.
- **User and Role Management**: Admin functionalities to manage users and their roles.
- **Patient and Medical Device Management**: Assign devices to patients and manage them.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flask
- PyODBC
- SQL Server

### Installation

1. Clone the repository:
   ```bash
   https://github.com/atharvamk14/project2_ec530.git
   ```
2. Navigate to the project directory:
   ```bash
   cd project_ec530.git
   ```
3. Install required Python packages:
   ```bash
   pip install flask pyodbc
   ```

### Configuration

Configure your database connection by setting environment variables or directly in the code:

- `DB_SERVER`: The server name or IP address of your database server.
- `DB_NAME`: The name of your database.

You can set these directly in your operating system, or modify them in `project.py` under the database connection setup.

### Running the Application

To run the application locally:
```bash
python project.py
```

Access the application via web browser:
```
http://localhost:5000
```

## Endpoints Overview

- `/login` - Log in to the system.
- `/add_user` - Add new users to the system.
- `/upload_media` - Upload media files.
- `/book_appointment` - Book new appointments.
- `/manage_users` - Admin feature to manage all system users.
- Additional endpoints for device management, setting alerts, and more are detailed within the application's routing.



## Contact

Your Name - Atharva Khandekar [amk14@bu.edu]

Project Link: https://github.com/atharvamk14/project2_ec530

