## Expense Tracker Web Application

A simple expense tracker web application built using **Python, Flask, and SQLite**. This project helps users track their income and expenses, organize transactions by categories, and set budgets for better financial management.

---

## 💰 Features

* **Add Category** – Create categories to classify income and expenses.
* **Add Transaction** – Record income and expenses with amount, type, and category.
* **Set Budget** – Define budgets for each category.
* **Summary Dashboard** – View total income, total expenses, and net balance.
* User-friendly and lightweight interface.

---

## 🧠 Tech Stack

**Backend:**

* Python 3.7+
* Flask
* Flask-SQLAlchemy

**Database:**

* SQLite

**Frontend:**

* HTML, CSS, Bootstrap (if used)

---

## 📂 Project Structure

```
Expense-Tracker/
│
├── app.py                # Main Flask application
├── models.py             # Database models
├── templates/             # HTML templates
│   ├── index.html
│   ├── add_transaction.html
│   ├── add_category.html
│   └── summary.html
├── static/                # CSS and JS files
├── expense_tracker.db     # SQLite database file
├── requirements.txt        # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/expense-tracker.git
```

2. Navigate to the project directory:

```bash
cd expense-tracker
```

3. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\\Scripts\\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
python app.py
```

6. Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## 📊 How It Works

1. Users add categories for income and expenses.
2. Transactions are recorded with amount, type, and category.
3. Budgets are assigned to categories.
4. The app calculates total income, total expenses, and net balance.
5. Summary is displayed on the dashboard.

---

## 🧪 Future Enhancements

* User authentication (login & signup)
* Monthly and yearly expense reports
* Charts and graphs using Matplotlib/Chart.js
* Export data to CSV or Excel
* Cloud deployment (Heroku, Render, AWS)

---

## 👩‍💻 Author

**Bhumi**
Student | Python & Web Development Enthusiast

---

## 📜 License

This project is for educational purposes and is free to use and modify.
