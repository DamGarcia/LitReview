# Literature Review Network

A web app where readers write reviews of books and articles, and follow other users to discover new literature.

> **Status:** MVP, local development only (no deployment configuration).

---

## Features

| # | Feature | Description |
| --- | --------- | ------------- |
| 1 | Write reviews | Logged-in users review a book with a headline, body text, and a required 1–5 star rating. Each user can review a given book once |
| 2 | Follow users | Users follow others to read their reviews and discover new literature |
| 3 | Browse books | Each book shows its description, author, optional cover image, and all its reviews |
| 4 | Accounts | Sign up, log in, log out (custom `users.User` model) |

<!-- TODO: reconcile this table with the Requirements Specification and wireframes -->

---

## Tech Stack

| Component | Version | Notes |
| ----------- | --------- | ------- |
| Python | **3.8 – 3.10** | Django 4.0 does not officially support 3.11+ |
| Django | 4.0.5 | Pinned in `requirements.txt` |
| Pillow | 9.1.1 | Required for the book cover `image` field |
| Database | SQLite | Django default, no setup needed |

Check your Python version before starting:

```bash
python3 --version   # Windows: python --version
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Your prompt should now start with `(venv)`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the database tables

```bash
python manage.py migrate
```

### 5. Load the example data

```bash
python manage.py loaddata fixtures/reviews_sample.json
```

This loads 3 users, 4 books, and 5 reviews, plus the follow relationships between users.

> Run this **after** `migrate`. The tables must exist before data can be loaded into them.

### 6. Start the server

```bash
python manage.py runserver
```

Open **<http://127.0.0.1:8000/>** in your browser.

---

## Test Accounts

All accounts come from `fixtures/reviews_sample.json` and share one password.

| Username | Password | Follows | Reviews written |
| ---------- | ---------- | --------- | ----------------- |
| `ann` | `testpass123` | `bob`, `cara` | 2 (Earthsea, Kindred) |
| `bob` | `testpass123` | `ann` | 2 (Earthsea, Dune) |
| `cara` | `testpass123` | nobody | 1 (Dune) |

None of these accounts has admin rights. To use the Django admin panel at `/admin/`, create a superuser:

```bash
python manage.py createsuperuser
```

---

## Example Data

**Books**

| ID | Title | Author | Reviews |
| ---- | ------- | -------- | --------- |
| 1 | A Wizard of Earthsea | Ursula K. Le Guin | 2 |
| 2 | Kindred | Octavia Butler | 1 |
| 3 | Dune | Frank Herbert | 2 |
| 4 | Untitled Field Notes | *(none)* | 0 |

Book 4 is deliberate edge-case data: it has no author, no description, and no reviews, so you can check how the site handles empty states.

**Follow graph**

```
ann ───▶ bob
ann ───▶ cara
bob ───▶ ann
cara  (follows nobody)
```

---

## Suggested Test Walkthrough

1. Log in as `ann`. Following `bob` and `cara`, you should be able to see their reviews of Earthsea and Dune.
2. Open **Dune**. It has two reviews with opposing views (`cara`: 2 stars, `bob`: 4 stars).
3. Still as `ann`, write a review of **Dune** (she hasn't reviewed it yet). It should appear on the book's page and on her profile.
4. Try to review **Dune** a second time, or review **Kindred**, which `ann` has already reviewed. The site should refuse and not create a duplicate.
5. Try submitting a review with no rating, then with a rating of 0 or 6. Both should be rejected. Ratings 1 through 5 should be accepted.
6. Log out and log in as `cara`. She follows nobody, so any follow-based feed should be empty. Follow `ann` and confirm `ann`'s reviews now appear.
7. Open **Untitled Field Notes** and confirm the page renders cleanly with no author and no reviews.
8. Log in as `bob` and confirm `ann`'s reviews appear (`bob` follows `ann`) but `cara`'s activity does not (`bob` does not follow her).

---

## Data Model

```
                ┌──────────┐ 1        * ┌──────────┐ *        1 ┌──────────┐
                │   User   │────────────│  Review  │────────────│   Book   │
                └──────────┘   writes   └──────────┘  is about  └──────────┘
                  │      ▲
                  │ *  * │
                  └──────┘
                  following (many-to-many, self-referencing)
```

| Model | Fields | Notes |
| ------- | -------- | ------- |
| `users.User` | username, first_name, last_name, email, password, `following` | Custom user model; `following` is a many-to-many field to other users |
| `reviews.Book` | title, author *(optional)*, description, image *(optional)*, created | Cover images need Pillow |
| `reviews.Review` | book, user, headline, body, rating, created, updated | `rating` is required, whole number from 1 to 5 |

**Review rules:**

- `rating` is required and must be a whole number from 1 to 5 (the example data uses 2 to 5).
- A user can review a given book only once. The pair (`user`, `book`) must be unique.
- A user can edit their existing review, but not add a second one for the same book.

---

## Project Structure

```
<REPO_FOLDER>/
├── manage.py
├── requirements.txt
├── fixtures/
│   └── reviews_sample.json   # example users, books, reviews, follows
├── <project_config>/         # settings, root URLs
├── users/                    # custom User model, follow logic
├── reviews/                  # Book and Review models, views, templates
└── README.md
```

<!-- TODO: adjust to match the real folder layout -->

---

## Resetting the Database

To return to a clean state with the example data:

```bash
rm db.sqlite3                                       # Windows: del db.sqlite3
python manage.py migrate
python manage.py loaddata fixtures/reviews_sample.json
```

Loading the fixture twice does not create duplicates, because each record has a fixed ID. It does overwrite any edits you made to those records, so reset as above when you want a clean slate.
