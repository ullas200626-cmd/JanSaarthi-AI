# JanSaarthi AI

### Your Language. Your Voice. Your Government.

**JanSaarthi AI** is a multilingual civic assistance prototype designed to help citizens describe common local problems, identify the type of issue, register a demonstration complaint, and track its status.

The project explores how accessible digital technology can make civic issue reporting easier for people who may face language or digital-literacy barriers.

> **Important:** This is a student prototype. Complaints are stored locally in a demonstration database and are NOT submitted to any real government department.

## 1. Problem Statement

Citizens may find it difficult to identify the correct channel for reporting local issues such as water supply problems, damaged roads, streetlight failures, sanitation concerns, and electricity issues. Language barriers and complicated reporting processes can make the experience more difficult.

JanSaarthi AI explores a simple, multilingual interface for describing these issues and managing demonstration complaint records.

## 2. Proposed Solution

The prototype provides:

* A text-based civic assistance chatbot.
* Language detection and responses in five configured languages.
* Rule-based classification of supported civic issues.
* Demonstration complaint registration with a unique complaint ID.
* Complaint status tracking.
* An admin dashboard for viewing complaint records.
* Status management for Submitted, In Progress, and Resolved.
* Basic analytics showing complaint counts by category.

## 3. Supported Languages

The current configured languages are:

* English
* Hindi
* Tamil
* Telugu
* Marathi

Kannada support and additional accessibility features are future development goals, not features claimed as completed in this version.

## 4. Supported Issue Categories

The current prototype recognises these categories:

* Water supply
* Roads
* Streetlights
* Sanitation
* Electricity

Classification is based on implemented rules and should be evaluated with varied test messages. It is not a guarantee that every citizen message will be classified correctly.

## 5. Technology Stack

| Component               | Technology               |
| ----------------------- | ------------------------ |
| Backend                 | Python and Flask         |
| Frontend                | HTML, CSS, JavaScript    |
| Language detection      | Lingua language detector |
| Database                | SQLite                   |
| API communication       | HTTP and JSON            |
| Development environment | Visual Studio Code       |

## 6. Project Structure

```text
JanSaarthi-AI/
├── app.py
├── admin_dashboard.py
├── database.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   └── admin.html
├── static/
│   ├── script.js
│   └── style.css
├── data/
│   └── services.json
└── database/
    └── jansaarthi.db
```

The SQLite database file is created or used locally by the application. Do not commit real citizens' personal information or sensitive complaint records to a public repository.

## 7. Installation and Setup

### Prerequisites

* Python installed on your computer.
* Visual Studio Code or another code editor.
* A terminal such as Windows PowerShell.

### Install dependencies

Open the terminal in the project folder and run:

```powershell
python -m pip install -r requirements.txt
```

### Start the citizen chatbot

Run:

```powershell
python app.py
```

Open the local address shown in the terminal. In the usual Flask development configuration, this is `http://127.0.0.1:5000`.

### Start the admin dashboard

Open a second terminal in the same project folder and run:

```powershell
python admin_dashboard.py
```

Open `http://127.0.0.1:5001` in your browser.

Keep both development servers running while testing the complete workflow.

## 8. Demonstration Workflow

1. Enter a civic problem in a supported language.
2. Review the chatbot response and detected issue category.
3. Register a demonstration complaint when the option is available.
4. Save the generated complaint ID.
5. Track the complaint using that ID.
6. Open the admin dashboard to view the record.
7. Change its status and save the update.
8. Track the complaint again to verify the new status.

All steps operate on local demonstration records.

## 9. API Overview

The current prototype includes these application endpoints:

| Endpoint                                     | Purpose                                   |
| -------------------------------------------- | ----------------------------------------- |
| `GET /api/health`                            | Check application health                  |
| `POST /api/chat`                             | Process a citizen message                 |
| `POST /api/complaints`                       | Register a demonstration complaint        |
| `GET /api/complaints/<complaint_id>`         | Track a complaint                         |
| `GET /api/admin/dashboard`                   | Retrieve dashboard records and counts     |
| `PATCH /api/admin/complaints/<complaint_id>` | Update a demonstration complaint's status |

The chatbot and complaint endpoints are provided by the main Flask application. The admin endpoints are provided by the separate dashboard application, so run the appropriate server when testing them.

## 10. Testing and Evidence

The prototype has been manually tested for:

* Responses to sample messages in the five configured languages.
* Demonstration complaint registration.
* Complaint ID generation and tracking.
* Display of records in the admin dashboard.
* Complaint status updates reflected in the tracking workflow.

For a competition submission, add dated screenshots, reproducible test cases, expected results, and actual results. Do not claim automated testing, real-world deployment, or official government integration unless those have actually been completed and verified.

## 11. Responsible AI and Limitations

* Language detection and issue classification can make mistakes.
* The current classifier uses implemented rules; it should not be described as a fully trained AI model.
* The system does not contact government departments.
* Complaint statuses are demonstration statuses, not official service updates.
* The local admin dashboard does not yet have administrator authentication.
* The application has not been established as production-ready.
* Public deployment would require security controls, access management, privacy protections, validation, error handling, and further testing.

### AI usage disclosure

The prototype uses a language-detection library and rule-based issue classification. Generative AI may be used during development for coding assistance or documentation. The team should disclose the actual tools used and verify generated code before submission.

## 12. Future Development

Potential next steps include:

* Kannada language support.
* Voice input and improved accessibility.
* More robust multilingual issue classification.
* Configurable routing information for civic services.
* Secure administrator login and role-based access.
* Better analytics and downloadable reports.
* Testing with diverse, anonymised sample messages.
* Official integrations only after proper authorisation and technical validation.

## 13. Open-Source and Contribution

This project is being developed as a student prototype for civic technology and social impact.

Before publishing, select an appropriate open-source licence, add the licence file, review dependencies, and remove secrets or private data. Contributions should include clear documentation and reproducible testing instructions.

## 14. Project Status

**Current status:** Local working prototype with multilingual text interaction, demonstration complaint registration and tracking, and a local admin dashboard.

**Project goal:** Explore a more accessible way for citizens to describe civic issues in their preferred language.

**Tagline:** Your Language. Your Voice. Your Government.
