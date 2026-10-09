# JanSaarthi AI

### Your Language. Your Voice. Your Government.

**JanSaarthi AI** is a multilingual civic-issue assistance prototype designed to help citizens describe common civic problems, identify an issue category, register a demo complaint, and check its status.

The project explores how accessible digital tools can make civic issue reporting easier to understand and use.

> **Important:** This is an educational prototype. Complaints are stored locally for demonstration and are not submitted to any government department or official portal.

## 1. Problem Statement

Citizens may face difficulties understanding digital services, describing civic problems through online systems, or following the status of a complaint. Language barriers can make these processes more difficult.

JanSaarthi AI explores a simple, language-aware interface for reporting and tracking common civic issues.

These are the problems the prototype aims to address; their scale and impact have not yet been measured through a formal user study.

## 2. Proposed Solution

The prototype provides a basic workflow:

1. A citizen enters a civic issue as text.
2. The application attempts to detect the language.
3. Keyword-based rules identify a supported issue category.
4. The citizen can register a demo complaint and receive a complaint ID.
5. The complaint can be looked up using its ID.
6. A separate local admin dashboard can view records and update their demo status.

## 3. Implemented Features

* Text-based civic issue input.
* Language detection and localized responses for the five configured languages: English, Hindi, Tamil, Telugu, and Marathi.
* Keyword-based classification for water, roads, streetlights, sanitation, and electricity issues.
* Demo complaint registration with a generated complaint ID.
* Complaint tracking through a local API.
* SQLite database for local complaint records.
* Separate admin dashboard with complaint listings, status counts, category counts, and local status updates.
* Automated tests covering core application and dashboard behaviour.

**Classification note:** Issue categories are identified using keyword rules, not a trained machine-learning model.

## 4. Technology Stack

* **Language:** Python
* **Web framework:** Flask
* **Language detection:** Lingua
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript
* **Testing:** Python automated tests

## 5. System Architecture

Citizen web interface
→ Flask application and API
→ Language detection and keyword-based issue classification
→ Local SQLite database
→ Complaint tracking and separate admin dashboard

The citizen application and admin dashboard use the same local database.

## 6. Supported Issue Categories

| Category     | Example topic                  |
| ------------ | ------------------------------ |
| Water        | Water supply problems          |
| Roads        | Damaged roads                  |
| Streetlights | Streetlight problems           |
| Sanitation   | Waste and cleanliness issues   |
| Electricity  | Electricity-related complaints |

The examples illustrate the categories. Actual classification depends on the keywords implemented in the code.

## 7. Configured Languages

* English
* Hindi
* Tamil
* Telugu
* Marathi

Kannada support is a future development goal and is not claimed as implemented in the current version.

## 8. Project Setup

### Prerequisites

* Python installed
* Git (optional, for cloning the repository)

### Install and run

Clone the repository:

```bash
git clone https://github.com/ullas200626-cmd/JanSaarthi-AI.git
cd JanSaarthi-AI
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the citizen application:

```bash
python app.py
```

Open the local address printed in the terminal, normally `http://127.0.0.1:5000`.

### Run the admin dashboard

Open a second terminal in the project folder and run:

```bash
python admin_dashboard.py
```

Open `http://127.0.0.1:5001` in your browser.

**Security warning:** The prototype admin dashboard does not have authentication. Run it locally for demonstration only; do not expose it publicly or use it for real citizen data.

## 9. API Overview

| Endpoint                                     | Purpose                                                       |
| -------------------------------------------- | ------------------------------------------------------------- |
| `GET /`                                      | Opens the citizen interface                                   |
| `GET /api/health`                            | Checks application health and reports configured languages    |
| `POST /api/chat`                             | Detects language and returns a keyword-based issue suggestion |
| `POST /api/complaints`                       | Registers a demo complaint                                    |
| `GET /api/complaints/<complaint_id>`         | Looks up a complaint by ID                                    |
| `GET /api/admin/dashboard`                   | Retrieves dashboard records and summary counts                |
| `PATCH /api/admin/complaints/<complaint_id>` | Updates a complaint's local demo status                       |

The admin endpoints belong to the separate application running on port 5001.

## 10. Testing

The project has seven automated tests reported as passing during development. They cover:

* Application health endpoint
* Water-issue recognition
* Complaint registration and tracking
* Unknown complaint handling
* Rejection of an invalid status
* Visibility of a changed status
* Admin dashboard counts

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

Test results describe the tested prototype behaviour. They do not establish real-world accuracy, government acceptance, or measurable social impact.

## 11. Future Scope — Not Yet Implemented

The following are development goals, not existing features:

* Kannada support and validation of language detection across all target languages.
* Voice input and speech-based interaction.
* More robust AI-assisted issue classification and priority analysis.
* Location extraction and verified department/service routing.
* Real-time notifications and escalation reminders.
* Admin authentication, authorization, and audit logs.
* Integration with official government portals or department APIs, subject to permission and technical availability.
* User testing, accessibility evaluation, privacy safeguards, and impact measurement.

## 12. Responsible AI and Privacy

* The current classifier uses keywords and can misunderstand unclear or multilingual messages.
* Language detection may be inaccurate, especially for short messages.
* Complaint records are demonstration data stored in a local SQLite database.
* Do not enter sensitive personal information or real citizens' private data.
* No official government submission or external department integration is implemented.
* Human review and proper authorization would be needed before any real-world deployment.

## 13. AI Usage Disclosure

AI assistance was used during project development and documentation. The repository's code, feature descriptions, setup instructions, and test claims should be reviewed by the project team before submission. The team is responsible for understanding, testing, and presenting the submitted work accurately.

## 14. Project Status

**Status:** Working educational prototype

**Repository:** https://github.com/ullas200626-cmd/JanSaarthi-AI

JanSaarthi AI is an exploration of how multilingual digital tools could help citizens communicate civic issues more easily. Its current implementation is a foundation for future testing and responsible development, not a live government service.
