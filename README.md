# DevQuery - Full-Stack Q&A Platform

DevQuery is a robust, full-stack Question and Answer web application designed to host community discussions. Built using the **Python/Django** framework and a **MySQL** relational database, the project follows clean MVC design principles, enterprise-grade security structures, and optimized URL routing mechanisms.

## 🚀 Key Features
* **Relational Database Management:** Leverages Django ORM to seamlessly map dynamic relationships between users, questions, and responses inside a MySQL database.
* **SEO-Optimized Slugs:** Automatically generates human-readable, clean URLs using `SlugField` validation logic.
* **Environment Security:** Isolates sensitive credentials, encryption keys, and database passwords locally using `python-dotenv` to ensure zero credential leaks.
* **Modular Codebase:** Organized architecture utilizing separate Django apps (`users`, `questions`) for scalability and clean code separation.

## 🛠️ Tech Stack
* **Backend:** Python, Django
* **Database:** MySQL
* **Environment Control:** Dotenv (`.env`), Virtual Environments (`venv`)
* **Version Control:** Git, GitHub

---

## 💻 Local Setup Instructions

Follow these steps to clone and run this web application on your local machine:

### 1. Clone the Repository
```bash
git clone [https://github.com/TejasWaindeshkar/qasite.git](https://github.com/TejasWaindeshkar/qasite.git)
cd qasite
