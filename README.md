A comprehensive Django-based eCommerce platform that connects customers with nearby retailers using location-based services. Features include AI-powered product recommendations, smart search, and an intelligent chatbot powered by Google Gemini AI.
### Run Commands in Order:

```bash
# 1. Create virtual environment and install packages
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install django pillow

# 2. Make migrations
python manage.py makemigrations users
python manage.py makemigrations shops
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations chat

# 3. Apply migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Load initial data
python manage.py setup_initial_data

# 6. (Optional) Create test data
python manage.py create_test_data

# 7. Run server
python manage.py runserver
✨ Features
🛍️ Customer Features
Location-Based Shopping

Find shops near your location using GPS coordinates
Filter shops by distance radius
City-based shop search
Real-time distance calculation using Haversine formula
Smart Product Discovery

Browse products by category
AI-powered search with typo tolerance
Advanced filters (price range, category, city)
Autocomplete search suggestions
Product recommendations based on browsing history
Shopping Cart & Checkout

Add multiple products to cart
Grouped cart items by shop
Real-time stock validation
Multiple payment methods (COD, UPI)
Flexible delivery options (Retailer, Partner, Self-pickup)
Order Management

Complete order history
Real-time order tracking
Order status updates
Order cancellation (for pending orders)
Payment status tracking
Communication

Direct chat with shop owners
AI chatbot for instant support
Message history
🏪 Retailer Features
Shop Management

Create and customize shop profile
Shop location with map coordinates
Business hours management
GST number registration
Shop image upload
Delivery radius configuration
Product Management

Add unlimited products
Product categorization
Image upload with preview
Stock management
Price and discount settings
SKU and barcode support
Bulk product operations
Low stock alerts
Order Processing

Order dashboard with statistics
Order status management
Customer order details
Revenue tracking
Order filtering and search
Business Analytics

Total sales revenue
Product performance metrics
Low stock alerts
Recent order summaries
👨‍💼 Admin Features
User Management

View all users (customers & retailers)
Delete fake/abusive accounts
User activity monitoring
Role-based access control
Shop Approval System

Review new shop registrations
Approve or reject shops
Provide rejection reasons
Suspend shops for policy violations
Shop verification workflow
Content Moderation

Delete inappropriate products
Monitor shop listings
Review order disputes
Manage categories
Platform Analytics

Total users statistics
Active shops count
Order volume tracking
Revenue overview
🤖 AI-Powered Features
Product Recommendations

Personalized recommendations based on purchase history
"Frequently Bought Together" suggestions
Similar product recommendations
Trending products in your area
AI-powered cross-sell opportunities
Smart Search

Natural language search understanding
AI-enhanced query interpretation
Price range extraction from queries
Typo correction
Context-aware results
AI Chatbot Assistant

24/7 automated customer support
Order status inquiries
Product search assistance
FAQ responses
Shop information lookup
Contextual understanding using Google Gemini AI
BuyReal/
├── buyreal/                    # Main project directory
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── users/                      # User authentication & profiles
│   ├── models.py              # Custom user model
│   ├── views.py               # Auth views
│   ├── forms.py               # Registration/login forms
│   └── urls.py                # User URLs
│
├── shops/                      # Shop management
│   ├── models.py              # Shop, Category models
│   ├── views.py               # Shop CRUD operations
│   ├── forms.py               # Shop forms
│   ├── urls.py                # Shop URLs
│   └── management/            # Management commands
│       └── commands/
│           ├── setup_initial_data.py
│           └── create_test_data.py
│
├── products/                   # Product management
│   ├── models.py              # Product, ProductCategory models
│   ├── views.py               # Product CRUD operations
│   ├── forms.py               # Product forms
│   └── urls.py                # Product URLs
│
├── orders/                     # Cart & order management
│   ├── models.py              # Cart, Order, OrderItem models
│   ├── views.py               # Cart & checkout logic
│   ├── forms.py               # Checkout forms
│   ├── context_processors.py # Cart count context
│   └── urls.py                # Order URLs
│
├── chat/                       # Messaging system
│   ├── models.py              # Conversation, Message models
│   ├── views.py               # Chat views
│   └── urls.py                # Chat URLs
│
├── ai_services/                # AI features
│   ├── gemini_service.py      # Google Gemini integration
│   ├── recommendation_service.py  # Product recommendations
│   ├── search_service.py      # Smart search
│   ├── chatbot_service.py     # AI chatbot
│   ├── views.py               # AI API endpoints
│   └── urls.py                # AI service URLs
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── navbar.html            # Navigation
│   ├── footer.html            # Footer
│   ├── home.html              # Homepage
│   ├── users/                 # User templates
│   ├── shops/                 # Shop templates
│   ├── products/              # Product templates
│   ├── orders/                # Order templates
│   ├── chat/                  # Chat templates
│   └── ai_services/           # AI templates
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Custom CSS
│   ├── js/
│   │   └── main.js            # Custom JavaScript
│   └── images/                # Static images
│
├── media/                      # User uploaded files
│   ├── shop_images/           # Shop photos
│   ├── product_images/        # Product photos
│   └── profile_pics/          # User avatars
│
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
🛠️ Technologies Used
Backend
Django 4.2 - Web framework
Python 3.9+ - Programming language
SQLite - Database (development)
Django ORM - Database abstraction
Frontend
HTML5 - Markup
CSS3 - Styling
Bootstrap 5.3 - UI framework
Bootstrap Icons - Icon library
JavaScript (ES6) - Client-side scripting
AJAX - Asynchronous requests
AI & Machine Learning
Google Gemini AI - Natural language processing
google-genai - Gemini Python SDK
scikit-learn - ML algorithms
pandas - Data manipulation
numpy - Numerical computing
Additional Libraries
Pillow - Image processing
django-crispy-forms - Form rendering (optional
📥 Installation
Prerequisites
Python 3.9 or higher
pip (Python package manager)
Git (optional)
Virtual environment tool
Workflow Examples
Customer Journey
Register as customer
Browse nearby shops
View shop products
Add products to cart
Proceed to checkout
Enter delivery address
Choose payment method
Place order
Track order status
Chat with shop owner if needed
Retailer Journey
Register as retailer
Create shop profile
Wait for admin approval
Add products with images
Manage inventory
View incoming orders
Update order status
Chat with customers
Admin Journey
Login to admin panel
Review pending shop registrations
Approve or reject shops
Monitor user activity
Manage categories
View platform statistics
Customer
Permissions: Browse, shop, order, chat
Restrictions: Cannot create shops or products
Dashboard: Order history, cart, profile
Retailer
Permissions: Create shop, manage products, process orders
Restrictions: Cannot access other retailers' data
Dashboard: Sales analytics, inventory, orders
Admin
Permissions: Full system access
Capabilities: Approve shops, manage users, moderate content
Dashboard: Platform statistics, user management
created_at
🔌 API Endpoints
Authentication
