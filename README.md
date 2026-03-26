# Secure Gateway System

The **Secure Gateway System** is a high-performance, software-based middleware security layer designed to provide end-to-end AES encryption and decryption for legacy applications without requiring hardware or software modifications.

It features a robust TCP proxy, comprehensive key management, real-time audit logging, and a premium web dashboard for centralized monitoring and configuration.

## Features

- **End-to-End Encryption**: Transparent AES encryption and decryption for TCP traffic using a built-in proxy.
- **Role-Based Access Control (RBAC)**: Supports distinct user roles: `admin`, `analyst`, and `operator`.
- **Advanced Key Management**: Generate, rotate, and manage cryptographic keys securely.
- **Audit Logging**: Comprehensive real-time tracking of system events, login attempts, and gateway activity.
- **Web Dashboard**: A centralized, premium dark-themed interface for live monitoring and configuration.
- **Zero-Modification Integration**: Works as an intermediary for legacy systems without altering their codebase.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite (managed with Flask-SQLAlchemy)
- **Cryptography**: `cryptography` library (AES-128-CBC / Fernet)
- **Frontend**: HTML templates with premium CSS styling

## Prerequisites

- Python 3.8+
- PIP

## Installation & Setup

1. **Clone the repository** (or navigate to the project folder):
   ```bash
   cd "Deva Project"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Required packages include: `Flask`, `Flask-SQLAlchemy`, `cryptography`, `Werkzeug`.*

3. **Initialize the application**:
   The application uses an SQLite database (`gateway.db`). This database will be automatically created and seeded during the first run.

4. **Run the server**:
   ```bash
   python app.py
   ```

## Usage

Once the server is running, access the web dashboard via your browser:

**URL**: [http://localhost:5000](http://localhost:5000)

### Default Credentials
Upon initialization, the system creates the following default accounts. *Please change these passwords immediately upon first login for security purposes.*

- **Admin**: `admin` / `admin123`
- **Analyst**: `analyst` / `analyst123`
- **Operator**: `operator` / `operator123`

### Project Structure
- `app.py`: Main Flask application entry point.
- `models.py`: Database models and schema definition.
- `config.py`: Application configuration settings.
- `core/`: Core gateway logic including the TCP proxy and key management backend.
- `routes/`: Flask blueprints for authentication, dashboard, keys, logs, settings, and gateway API.
- `templates/`: HTML views for the dashboard and pages.
- `static/`: Static assets (CSS, JS, images).

## Security Note

This software is designed as a secure communication gateway. Ensure you manage your encryption keys safely and use a strong password for all accounts, particularly the internal dashboard access.

## License

This project is proprietary and intended for secure gateway operations.
