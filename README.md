# 🔋 Delhi Power Prediction

**Delhi Power Prediction** is a web-based system that provides real-time and historical electricity demand visualization and forecasting for Delhi. It aims to aid power distribution companies, researchers, and policymakers in analyzing power consumption trends and making informed decisions for load management.

---

## 🚀 Features

- ✅ User Registration & Role-based Login (Admin, Government Engineer, Researcher, Entrepreneur, Normal User)
- 📈 Power Demand Forecasting using advanced machine learning models
- 📊 Interactive Graphs with different time scales (Hourly, Daily, Monthly)
- 🧠 Smart Clustering & Load Balancing Suggestions using K-Means
- 🗂️ Credential Management by Admins (Add, Update, Delete)
- 🗺️ Geospatial Visualization using Folium
- 📂 Export and analyze past electricity consumption data
- 🔐 Secure access with role-based permissions
- 🧠 RAG based LLM using Sentence Transformer and Llama model for area and location based Q/A

---

## 👥 User Roles

- **Normal User**: Can register and analyze power data.
- **Entrepreneur / Researcher**: Access extended insights for research or product development.
- **Government Engineer / Admin**: Have advanced privileges for managing credentials and overseeing usage.

---

## ⚙️ How it Works

1. **Registration/Login**: Role-based registration and access control.
2. **Demand Prediction**: Users can view forecasted demand for different durations using trained ML models.
3. **Visualization**: Dynamic graphs created using Plotly and geospatial maps using Folium.
4. **Credential Management**: Admins manage access credentials for secure usage.

---

## 📁 Folder Structure

```plaintext
delhi_power_prediction/
│
├── core/                 # Main Django app with models, views, forms, etc.
├── templates/            # HTML templates
├── static/               # CSS, JS, and other static files
├── media/                # Uploaded files and generated charts
├── manage.py             # Django management script
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (not tracked in Git)
└── README.md             # Project description
```

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/delhi-power-prediction.git
cd delhi-power-prediction
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Project

```bash
python manage.py runserver
```

Access the project at http://localhost:8000
