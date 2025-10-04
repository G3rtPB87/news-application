<a id="top"></a>
# News Application Platform

A comprehensive Django-based news platform that enables independent journalists, publishers, and readers to connect through a robust content management and subscription system.

![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MariaDB](https://img.shields.io/badge/MariaDB-Database-orange.svg)

## Table of Contents

* [About The Project](#about-the-project)
* [Features](#features)
* [Built With](#built-with)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
* [Environment Variables](#environment-variables)
* [Usage](#usage)
* [API Documentation](#api-documentation)
* [Testing](#testing)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

---

## About The Project

The News Application Platform is designed to democratize news distribution by providing a complete ecosystem where:

* **Independent Journalists** can publish their work
* **Publishers** can manage their brand and content
* **Readers** can discover and subscribe to quality content
* **Editors** can maintain content quality through approval workflows

### Features [Back to Top](#top)

#### Multi-role User System

* Readers: Subscribe to content, personalized feeds
* Journalists: Create and manage articles/newsletters
* Editors: Content approval and quality control
* Publishers: Brand management and team coordination

#### Content Management

* Article and newsletter creation
* Draft, review, and publish workflows
* Automated content distribution

#### Subscription Engine

* Follow publishers and journalists
* Personalized content recommendations
* Email notifications for new content

#### RESTful API

* Complete API for third-party integrations
* Role-based access control
* Subscription-based content delivery

---

## Built With [Back to Top](#top)

* [Django](https://www.djangoproject.com/) - Web Framework
* [Django REST Framework](https://www.django-rest-framework.org/) - API Development
* [MariaDB](https://mariadb.org/) - Database
* [Tailwind CSS](https://tailwindcss.com/) - Styling
* [Docker](https://www.docker.com/) - Containerization

---

## Getting Started [Back to Top](#top)

### Prerequisites

* Python 3.8+
* MariaDB/MySQL Server
* pip (Python package manager)

### Installation

1. **Clone the repository**
Bash
git clone [https://github.com/yourusername/news-application.git](https://github.com/g3rtpb87/news-application.git)
cd news-application

2. **Set up virtual environment**
Bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. **Install dependencies**
Bash
pip install -r requirements.txt

4. **Configure environment variables**
Bash
cp .env.example .env
# Edit .env with your actual credentials

5. **Run migrations**
Bash
python manage.py migrate

6. **Create superuser**
Bash
python manage.py createsuperuser

7. **Start development server**
Bash
python manage.py runserver

### **Docker Installation**
Bash
# Build the image
docker build -t news-application .
# Run the container
docker run -p 8000:8000 news-application

---

## **Environment Variables** [Back to Top](#top)

Create a .env file in the project root with the following variables:

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_NAME=news_application_db
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# X/Twitter API Configuration (Optional)
X_API_KEY=your-x-api-key
X_API_SECRET=your-x-api-secret
X_ACCESS_TOKEN=your-x-access-token
X_ACCESS_SECRET=your-x-access-secret

Copy .env.example to .env and fill in your actual credentials.

### **Database Setup**

**Create MariaDB Database:**

SQL
CREATE DATABASE news_application_db;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON news_application_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;

**Configure environment variables in .env file**
Database settings are automatically loaded from environment variables
Usage

**User Roles and Workflows**

**Readers**
- Register/Login with reader role
- Browse publishers and journalists on homepage
- Subscribe to preferred content creators
- Access personalized dashboard with subscribed content

**Journalists**
- Register/Login with journalist role
- Create articles and newsletters
- Submit content for editorial review
- Manage published content portfolio

**Editors**
- Login with editor role
- Review pending submissions in editor dashboard
- Approve/reject content with feedback
- Manage content quality and standards

**Publishers**
- Currently: Created through admin panel by administrators
- Planned Enhancement: Self-service publisher registration portal
- Manage editorial team and content strategy
- Build subscriber base and brand presence

**Access Points**
- Home Page: http://localhost:8000/ - Public content discovery
- Reader Dashboard: http://localhost:8000/dashboard/ - Personalized feed
- Journalist Dashboard: http://localhost:8000/journalist/dashboard/
- Editor Dashboard: http://localhost:8000/editor/dashboard/
- Admin Panel: http://localhost:8000/admin/

---

## **API Documentation** [Back to Top](#top)

### **Authentication Required Endpoints**

| Endpoint | Method | Description | Required Role |
| :---- | :---- | :---- | :---- |
| `/api/articles/subscribed/` | `GET` | Get a subscriber's articles | Reader |
| `/api/newsletters/subscribed/` | `GET` | Get a subscriber's newsletters | Reader |
| `/api/articles/approve/<id>/` | `POST` | Approve an article | Editor |
| `/api/newsletters/approve/<id>/` | `POST` | Approve a newsletter | Editor |

Full API documentation available in the docs/ folder.

### **Example API Usage**

JavaScript  
// Get subscribed articles  
fetch('/api/articles/subscribed/', {  
    headers: {  
        'Content-Type': 'application/json',  
    },  
    credentials: 'include'  
}).then(response \=\> response.json())  
  .then(data \=\> console.log(data));

---

## **Testing** [Back to Top](#top)

### **Run the Complete Test Suite**

Bash  
python manage.py test news

### **Run Specific Test Modules**

Bash  
\# Test models  
python manage.py test news.tests.test\_models

\# Test views  
python manage.py test news.tests.test\_views

\# Test API endpoints  
python manage.py test news.tests.test\_api

\# Test authentication  
python manage.py test news.tests.test\_auth

### 

### **Test Coverage Report**

Bash  
pip install coverage  
coverage run manage.py test news  
coverage report  
coverage html

---

## **Roadmap** [Back to Top](#top)

* Publisher Self-Registration Portal
* Allow publishing houses to register directly
* Onboarding workflow for new publishers
* Brand customization options
* Enhanced Analytics
* Content performance metrics
* Reader engagement analytics
* Subscription growth tracking
* Mobile Application
* React Native mobile app
* Push notifications
* Offline reading capability

---

## **Contributing** [Back to Top](#top)

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

---

## **License** [Back to Top](#top)

This project is licensed under the **Unlicense License** \- see the ‘License file for details.’

---

## **Contact** [Back to Top](#top)

Gert Bester - gert.bester@icloud.com
Project Link: https://github.com/g3rtpb87news-application

