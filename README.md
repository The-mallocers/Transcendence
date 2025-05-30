# Transcendence

A comprehensive web application featuring a Pong game with tournaments, user profiles, chat, and more. Built with Django, PostgreSQL, Redis, and Docker.

## 📋 Table of Contents

- [Overview](#overview)
- [Implemented Modules](#-implemented-modules)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Monitoring](#monitoring)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

Transcendence is a full-featured web application centered around the classic Pong game. It provides user authentication, profiles, real-time chat, matchmaking, tournaments, and more. The application is containerized using Docker for easy deployment and includes a comprehensive monitoring stack.

## 🏆 Implemented Modules

This project implements the following modules as part of the 42 curriculum requirements:

### Web
- **Framework back** (Major): Django framework for backend development
- **Bootstrap** (Minor): Frontend toolkit for responsive design
- **DB** (Minor): PostgreSQL database for data storage

### User Management
- **Standard User management** (Major): Complete user registration, authentication, and profile management
- **Remote auth 42** (Major): OAuth2 authentication with 42 intranet

### Gameplay
- **Remote Players** (Major): Real-time multiplayer functionality
- **Live chat** (Major): Real-time chat system between users

### Cybersecurity
- **2FA** (Major): Two-Factor Authentication and JWT (JSON Web Tokens) for secure authentication

### DevOps
- **Monitoring system** (Minor): Prometheus and Grafana for system monitoring and visualization

### Accessibility
- **Browser compatibility** (Minor): Support for multiple browsers including Firefox and Chrome

### Server-Side Pong
- **Server-side** (Major): Server-side Pong implementation with API

## ✨ Features

- **User Authentication**: OAuth integration with 42 API and Two-Factor Authentication
- **User Profiles**: Customizable user profiles with statistics
- **Pong Game**: Real-time multiplayer Pong game
- **Matchmaking**: Find opponents to play against
- **Tournaments**: Create and participate in Pong tournaments
- **Real-time Chat**: Chat with other users
- **Notifications**: Real-time notifications for game invites, tournament updates, etc.
- **Admin Interface**: Manage users, games, tournaments, etc.
- **Monitoring**: Comprehensive monitoring with Prometheus and Grafana

## 🔧 Prerequisites

- Docker and Docker Compose
- Make
- Python 3.x (for local development)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Transcendence
   ```
2. Start the application:
   ```bash
   make up
   ```
   Notes: We will install Django as part of the build process, but its just to generate the env.
   This will build and start all containers. The application will be available at http://localhost:8000.

##### Make up will execute the following commands if it's the first time you run it:
1. Create the necessary secret files:
   ```bash
   make secrets
   ```
   You will be prompted to enter your 42 API client ID and secret, if you arent a 42 student, feel free to skip this.

2. Generate the environment file:
   ```bash
   make env
   ```
   This will create a `.env` file with all necessary configuration.

3. (Optional) Update passwords:
   ```bash
   make passwords
   ```
   This allows you to set custom passwords for the admin user, database, and Grafana.


## 🎮 Usage

### Starting and Stopping

- **Start the application**:
  ```bash
  make up
  ```

- **Start in detached mode** (no logs):
  ```bash
  make detach
  ```

- **Stop the application**:
  ```bash
  make down
  ```

- **Restart the application**:
  ```bash
  make restart
  ```

### Accessing Services

- **Web Application**: http://localhost:8000
- **Grafana**: http://localhost:3000
  - Username: admin
  - Password: (set during installation, default: admin)
- **Prometheus**: http://localhost:9090
- **MailHog** (for email testing): http://localhost:8025

### Monitoring

- **View logs**:
  ```bash
  make logs
  ```

- **Check status**:
  ```bash
  make status
  ```

## 📁 Project Structure

- **apps/**: Django applications
  - **admin/**: Admin interface customizations
  - **auth/**: Authentication system
  - **chat/**: Chat functionality
  - **client/**: Client-side functionality
  - **core/**: Core application functionality
  - **error/**: Error handling
  - **game/**: Game functionality
  - **index/**: Main index/homepage
  - **notifications/**: User notifications system
  - **player/**: Player management
  - **profile/**: User profiles
  - **tournaments/**: Tournament system
- **config/**: Django project configuration
- **docker/**: Docker-related files
- **media/**: User-uploaded files
- **static/**: Static files (CSS, JS, images)
- **templates/**: HTML templates
- **utils/**: Utility functions

## 📊 Monitoring

The application includes a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Node Exporter**: System metrics
- **PostgreSQL Exporter**: Database metrics
- **Alertmanager**: Alerts based on metrics

Access Grafana at http://localhost:3000 to view dashboards and metrics.

## 🛠️ Development

### Running Tests

```bash
make test
```

### Running Tests with Coverage

```bash
make test-coverage
```

### Reloading Static Files

```bash
make reload
```

## 🔍 Troubleshooting

### Database Issues

If you encounter database issues, you can clean the database volumes:

```bash
make dbclean
```

### Complete Cleanup

To remove all containers, images, and volumes:

```bash
make clean
```

### Environment File

If your environment file is missing or corrupted:

```bash
make env
```

### SSL Certificates

SSL certificates are automatically generated during the environment setup. If you need to regenerate them, delete the files in the `secrets` directory and run:

```bash
make env
```
