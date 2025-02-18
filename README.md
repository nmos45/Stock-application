# Stockify

Stockify is a web-based inventory management system built using the Django framework. It enables consumers to monitor food stock and their respective expiry dates.

## 🚀 Features

- **Inventory Tracking**- Monitor your stock levels to prevent shortages and overstocking.
- **Food lookup**- Search functionality to lookup specific foods or categories
- **Authentication**- email password reset, google sign in and reserved create,delete permissions for original object creator.
- **Design**- models where designed so that they are normalised 3NF, including indexes on frequently queried atributes.: <a href="model-design-diagram.png">Database Design</a>

## 🛠 Installation

Follow these steps to set up the Stock-Application locally:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/nmos45/Stock-application.git
cd Stock-application
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 5️⃣ Create a Superuser (For Admin Access)
```bash
python manage.py createsuperuser
```

### 6️⃣ Run the Development Server
```bash
python manage.py runserver
```

## 🏗 Usage

- **Log In** – Use the superuser credentials to access the admin panel.
- **Add** Categories – Create product categories to organize your inventory.
- **Add** Products – Input product details, including name, expirydate, quantity, and category.
- **Manage** Inventory – Update stock levels as products are added or removed.
