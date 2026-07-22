# Reddit Recruiter

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-6.0.7-0C4B33)
![Celery](https://img.shields.io/badge/Celery-Task%20Queue-37814A)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Broker-FF6600)
![OpenAI](https://img.shields.io/badge/OpenAI-AI%20Lead%20Analysis-412991)
![License](https://img.shields.io/badge/License-Not%20Specified-lightgrey)

**Reddit Recruiter** is an AI-assisted client-acquisition system built with Django. It monitors selected Reddit communities, collects recent text posts, evaluates each post as a potential software-development lead, and stores structured sales intelligence in a searchable Django admin dashboard.

The project combines Reddit data collection through PRAW, structured lead analysis through the OpenAI API, background task execution with Celery, scheduled jobs with Django Celery Beat, and a customized Jazzmin administration interface.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Lead Analysis](#lead-analysis)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Running Celery](#running-celery)
- [Scheduling Tasks](#scheduling-tasks)
- [Using the Admin Dashboard](#using-the-admin-dashboard)
- [Current Collection Behavior](#current-collection-behavior)
- [Security Notes](#security-notes)
- [Suggested Improvements](#suggested-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Finding qualified software-development clients on Reddit manually can be slow and inconsistent. Reddit Recruiter automates the early stages of this process.

The application:

1. Reads the configured subreddit list from the Django database.
2. Fetches recent text-based Reddit submissions.
3. Saves new posts while preventing duplicate records.
4. Sends uncategorized posts to an OpenAI model.
5. Converts the AI response into structured lead data.
6. Stores the analysis in the database.
7. Makes the resulting leads available through Django Admin.

The system is designed for businesses offering services such as:

- Business website development
- Shopify development
- Custom bot development
- Workflow automation
- AI chatbots
- Backend and API development
- E-commerce development
- Mobile and AI solutions

---

## Key Features

- **Reddit post monitoring** using PRAW.
- **Configurable subreddit list** stored in Django.
- **Duplicate prevention** using Reddit submission IDs.
- **AI-powered lead scoring** from 0 to 100.
- **Service categorization** based on the requested work.
- **Estimated project value** in USD.
- **Buying-intent and urgency detection**.
- **Competition assessment**.
- **Recommended next action** such as reply, watch, or ignore.
- **Matched keyword extraction**.
- **Concise AI lead review**.
- **Up to two personalized reply suggestions** for each post.
- **Lead pipeline statuses** from New to Won or Lost.
- **Asynchronous processing** with Celery.
- **Scheduled task management** with Django Celery Beat.
- **RabbitMQ message broker**.
- **Jazzmin-powered admin dashboard**.
- **CSV/import-export support** through Django Import Export.
- **Environment-based configuration** using Python Decouple.
- **Fast and reproducible dependency management** using `uv`.

---

## How It Works

```text
Configured Subreddits
         |
         v
     Reddit API
       (PRAW)
         |
         v
   Fetch New Posts
         |
         v
  Save Unique Posts
     to SQLite
         |
         v
 OpenAI Lead Analysis
         |
         v
 Save Score, Category,
 Review and Replies
         |
         v
 Django/Jazzmin Admin
```

### Post collection

The fetch task creates a read-only Reddit client using credentials from the `.env` file. It loops through the saved `Subreddit` records and requests up to three recent submissions from each eligible subreddit.

Only submissions containing `selftext` are stored. Link-only posts or posts without text content are skipped.

Each Reddit submission is saved as a `PostLead` record with information such as:

- Reddit post ID
- Subreddit
- Author username
- Post content
- Number of comments
- Post URL
- Human-readable posting time

### AI categorization

Posts with `categorized=False` are sent to the OpenAI API. The model returns a JSON response that follows a predefined schema. The returned analysis is saved directly to the corresponding `PostLead` record.

### Background processing

Celery exposes two background tasks:

- `fetch_new_posts`
- `categorize_fetched_posts`

These tasks can be triggered manually, scheduled through Django Celery Beat, or called from other parts of the application.

---

## Lead Analysis

Every analyzed Reddit post can receive the following structured information:

| Field | Description |
|---|---|
| `service_category` | The service that best matches the post |
| `score` | Lead quality score from 0 to 100 |
| `estimated_value` | Estimated commercial value in USD |
| `is_good_lead` | Whether the post is considered a strong opportunity |
| `buying_intent` | High, medium, low, or none |
| `urgency` | High, medium, low, or none |
| `competition` | High, medium, low, or unknown |
| `recommended_action` | Reply, watch, or ignore |
| `matched_keywords` | Keywords that influenced the categorization |
| `ai_review` | A concise explanation of the opportunity |
| `suggested_replies` | Up to two tailored Reddit reply drafts |

The current OpenAI implementation uses structured JSON output to make the response predictable and safe to save into Django model fields.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Django 6.0.7 | Web framework, ORM, admin, and project structure |
| SQLite | Development database |
| PRAW | Reddit API client |
| OpenAI API | Lead classification and reply generation |
| Celery | Background task processing |
| RabbitMQ | Celery message broker |
| Django Celery Beat | Database-managed scheduled tasks |
| Jazzmin | Customized Django admin interface |
| Django Import Export | Admin import and export functionality |
| Python Decouple | Environment variable management |
| uv | Dependency and virtual-environment management |

---

## Project Structure

```text
.
├── .venv/                  # Local virtual environment managed by uv
├── bot/                    # Reddit collection and AI analysis logic
│   ├── main.py             # Fetching, reset, and categorization functions
│   └── utils.py            # OpenAI prompt, schema, formatting, and persistence
├── clientacquisition/      # Django project configuration
│   ├── settings.py         # Django, Celery, RabbitMQ, and Jazzmin settings
│   ├── urls.py             # Project URL configuration
│   ├── celery.py           # Celery application configuration
│   ├── wsgi.py             # WSGI entry point
│   └── asgi.py             # ASGI entry point
├── core/                   # Main Django application
│   ├── models.py           # Subreddit, PostLead, and Tracker models
│   ├── admin.py            # Django admin configuration
│   ├── tasks.py            # Celery task definitions
│   └── migrations/         # Database migrations
├── .env                    # Local secrets and configuration; never commit
├── .gitignore              # Git exclusions
├── db.sqlite3              # Local SQLite database
├── manage.py               # Django management command entry point
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Locked dependency versions
└── README.md               # Project documentation
```

> The exact contents of some Django-generated files may differ depending on the local project state.

---

## Data Models

### `Subreddit`

Stores the Reddit communities monitored by the application.

| Field | Type | Description |
|---|---|---|
| `name` | CharField | Subreddit name, for example `r/webdev` |

### `PostLead`

Stores the Reddit submission and all generated lead intelligence.

Important fields include:

- Reddit post ID
- Related subreddit
- Author username
- Original post content
- Comment count
- URL
- Posting time
- Categorization status
- Service category
- Lead score
- Estimated project value
- Lead quality flag
- Buying intent
- Urgency
- Competition level
- Recommended action
- Matched keywords
- AI review
- Suggested replies
- Sales pipeline status
- Creation timestamp

Available sales statuses:

```text
New
Ignored
Waiting
Replied
Dm
Call booked
Proposal sent
Won
Lost
```

### `Tracker`

Stores basic information about the latest collection run.

| Field | Type | Description |
|---|---|---|
| `last_fetched_subreddit` | CharField | Last subreddit processed by the fetcher |
| `total_fetched_posts` | IntegerField | Number of posts saved during the latest run |

---

## Requirements

Before starting, install:

- Python compatible with the project's `pyproject.toml`
- [`uv`](https://docs.astral.sh/uv/)
- RabbitMQ
- A Reddit API application
- An OpenAI API key

You will also need Reddit API credentials with permission to read public Reddit content.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/reddit-recruiter.git
cd reddit-recruiter
```

Replace the example repository URL with your actual GitHub repository URL.

### 2. Install the project with uv

Because the project already contains `pyproject.toml` and `uv.lock`, install the locked dependencies with:

```bash
uv sync
```

This creates or updates the local `.venv` environment and installs the dependency versions recorded in `uv.lock`.

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

#### macOS or Linux

```bash
source .venv/bin/activate
```

Activation is optional when commands are run with `uv run`.

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=replace-with-a-secure-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Reddit API
READ_ACCOUNT_CLIENT_ID=your-reddit-client-id
READ_ACCOUNT_CLIENT_SECRET=your-reddit-client-secret
READ_ACCOUNT_USER_AGENT=reddit-recruiter/1.0 by your-reddit-username

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

### Important

- Do not commit `.env` to Git.
- Do not expose Reddit or OpenAI credentials in screenshots, logs, or documentation.
- Use `DEBUG=False` in production.
- Configure a secure and explicit `ALLOWED_HOSTS` value in production.

---

## Database Setup

Apply the Django migrations:

```bash
uv run python manage.py migrate
```

Create an administrator account:

```bash
uv run python manage.py createsuperuser
```

The project uses SQLite by default:

```text
db.sqlite3
```

For a production deployment, PostgreSQL is recommended.

### Create the initial tracker

The current fetching and reset functions expect a `Tracker` object to exist. Create one before running the tasks.

You can create it through Django Admin or the Django shell:

```bash
uv run python manage.py shell
```

```python
from core.models import Tracker

Tracker.objects.get_or_create(
    id=1,
    defaults={
        "last_fetched_subreddit": "",
        "total_fetched_posts": 0,
    },
)
```

---

## Running the Application

Start the Django development server:

```bash
uv run python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

Sign in with the superuser account created during setup.

---

## Running Celery

RabbitMQ must be installed and running before the Celery worker starts.

The configured broker is:

```text
amqp://guest:guest@localhost:5672//
```

### Start RabbitMQ

Use the appropriate RabbitMQ command or operating-system service manager for your environment. Confirm that RabbitMQ is listening on port `5672`.

### Start the Celery worker

#### macOS or Linux

```bash
uv run celery -A clientacquisition worker -l info
```

#### Windows

Celery commonly requires the solo execution pool during local Windows development:

```powershell
uv run celery -A clientacquisition worker -l info --pool=solo
```

---

## Scheduling Tasks

Start Django Celery Beat with the database scheduler:

```bash
uv run celery -A clientacquisition beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

For a complete local setup, run the following processes in separate terminals:

### Terminal 1: Django

```bash
uv run python manage.py runserver
```

### Terminal 2: Celery worker

```bash
uv run celery -A clientacquisition worker -l info
```

On Windows, add `--pool=solo`.

### Terminal 3: Celery Beat

```bash
uv run celery -A clientacquisition beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Recommended task order

Schedule post fetching before post categorization. For example:

```text
1. fetch_new_posts
2. categorize_fetched_posts
```

Allow enough time between the two schedules for Reddit posts to be collected before categorization begins.

Periodic tasks can be configured from Django Admin under the Django Celery Beat section.

---

## Using the Admin Dashboard

The Jazzmin-powered admin dashboard is the main interface for managing the system.

From the dashboard, an administrator can:

1. Add or remove monitored subreddits.
2. Review collected Reddit posts.
3. Filter posts by status, category, score, or lead quality.
4. Read the AI-generated analysis.
5. Review suggested replies.
6. Move leads through the sales pipeline.
7. Manage Celery Beat schedules.
8. Import or export supported model data.

### Adding a subreddit

Add a `Subreddit` record using either of these formats:

```text
r/webdev
```

or:

```text
webdev
```

The fetcher removes the `r/` prefix before making the Reddit API request.

---

## Manual Task Execution

Tasks can be queued from the Django shell while the Celery worker is running.

```bash
uv run python manage.py shell
```

```python
from core.tasks import fetch_new_posts, categorize_fetched_posts

fetch_new_posts.delay()
categorize_fetched_posts.delay()
```

The underlying functions can also be executed synchronously for local debugging:

```python
from bot.main import fetch_posts_from_subredits, categorize_posts

fetch_posts_from_subredits()
categorize_posts()
```

---

## Current Collection Behavior

The current implementation has several intentional or implementation-specific behaviors that developers should understand:

- It requests a maximum of three recent posts per subreddit.
- It stores only submissions with non-empty `selftext`.
- It skips link-only submissions.
- It prevents duplicates using the Reddit submission ID.
- It currently fetches a subreddit only when that subreddit has no saved related posts.
- It saves the number of posts collected during the latest execution in `Tracker.total_fetched_posts`.
- It expects at least one `Tracker` record to exist.
- Reddit redirects and missing subreddits are skipped.
- AI results are saved only when they match an existing `PostLead.post_id`.
- OpenAI connection, rate-limit, timeout, authentication, quota, and server errors are handled by the categorization utility.

These behaviors should be reviewed before using the application as a continuous production monitor.

---

## Configuration Notes

### Time zones

Django is configured with:

```python
TIME_ZONE = "UTC"
USE_TZ = True
```

Celery is configured with:

```python
CELERY_TIMEZONE = "Africa/Lagos"
CELERY_ENABLE_UTC = False
```

For predictable scheduling, consider using the same timezone policy for both Django and Celery.

### Task limits

Celery tasks have a configured time limit of 30 minutes:

```python
CELERY_TASK_TIME_LIMIT = 30 * 60
```

### Result backend

Celery uses RabbitMQ RPC results:

```python
CELERY_RESULT_BACKEND = "rpc://"
```

---

## Security Notes

This repository processes external content and uses third-party APIs. Before deploying it publicly:

- Set `DEBUG=False`.
- Replace the development secret key.
- Restrict `ALLOWED_HOSTS`.
- Use environment variables or a secrets manager.
- Use a dedicated RabbitMQ user instead of the default guest account.
- Restrict access to the Django admin.
- Add HTTPS.
- Use PostgreSQL instead of SQLite for production workloads.
- Add structured logging and monitoring.
- Add request and task retry policies.
- Review Reddit's API terms and platform rules.
- Review generated replies before posting them.
- Do not automatically publish AI-generated messages without human approval.

---

## Suggested Improvements

Potential next steps for the project include:

- Fetch posts continuously instead of only when a subreddit has no stored posts.
- Add a uniqueness constraint to `PostLead.post_id`.
- Store `posted_when` as a `DateTimeField` instead of formatted text.
- Add indexes for score, status, category, and timestamp.
- Improve batching so AI requests consistently process the intended chunk size.
- Add automatic retries with exponential backoff.
- Add detailed Celery task logging.
- Add tests for Reddit fetching, AI schema validation, and model persistence.
- Add a public-facing lead dashboard separate from Django Admin.
- Add filters for post age, minimum score, keywords, and excluded communities.
- Add support for comments as well as submissions.
- Add lead notifications through email, Slack, or Telegram.
- Add PostgreSQL and Docker support.
- Add CI checks with GitHub Actions.
- Add human approval before suggested replies are published.

---

## Development Commands

```bash
# Install locked dependencies
uv sync

# Run Django checks
uv run python manage.py check

# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Create admin user
uv run python manage.py createsuperuser

# Start Django
uv run python manage.py runserver

# Start Celery worker
uv run celery -A clientacquisition worker -l info

# Start Celery Beat
uv run celery -A clientacquisition beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## Contributing

Contributions are welcome.

A recommended workflow is:

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Run Django checks.
5. Commit with a clear message.
6. Open a pull request describing the change.

Example:

```bash
git checkout -b feature/improve-post-fetching
uv run python manage.py check
git commit -m "Improve continuous Reddit post fetching"
git push origin feature/improve-post-fetching
```

---

## License

No license has been specified yet.

Before publishing or accepting external contributions, add a license file such as MIT, Apache 2.0, or another license appropriate for the project.

---

## Disclaimer

This project is intended to assist with lead research and prioritization. AI-generated scores, estimates, reviews, and suggested replies may be inaccurate and should be reviewed by a human.

Use the Reddit API and any collected data in accordance with Reddit's terms, applicable privacy requirements, and relevant platform policies.
