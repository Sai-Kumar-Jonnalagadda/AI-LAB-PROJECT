import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import os

# --- Constants & Config ---
DB_FILE = "agency.db"
st.set_page_config(page_title="MAMS - Medicine Agency Management", layout="wide", initial_sidebar_state="expanded")

def apply_custom_styles():
    st.markdown("""
        <style>
            /* Dark Noir UI Theme */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
            
            :root {
                --primary: #ffffff;
                --bg-dark: #0e1117;
                --card-bg: #1a1c23;
                --text-main: #ffffff;
                --text-muted: #a0aec0;
                --border-color: #2d3748;
            }

            .main {
                background-color: var(--bg-dark) !important;
                font-family: 'Inter', sans-serif;
                color: var(--text-main);
            }
            
            /* Force dark background for main containers */
            [data-testid="stAppViewContainer"] {
                background-color: var(--bg-dark) !important;
            }
            [data-testid="stHeader"] {
                background-color: var(--bg-dark) !important;
                color: white;
            }

            /* Metric Cards Noir Style */
            .metric-card {
                flex: 1;
                min-width: 200px;
                background: var(--card-bg) !important;
                padding: 24px;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 1px solid var(--border-color) !important;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                border-color: #4a5568 !important;
            }
            .metric-label {
                font-size: 13px;
                font-weight: 700;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .metric-value {
                font-size: 32px;
                font-weight: 800;
                color: #ffffff;
                margin: 0;
            }

            /* Sidebar Noir Refinement */
            [data-testid="stSidebar"] {
                background-color: #161922 !important;
                border-right: 1px solid var(--border-color);
            }
            [data-testid="stSidebar"] .stMarkdown p {
                color: var(--text-muted);
            }
            
            /* Custom Sidebar Branding */
            .sidebar-brand {
                text-align: center;
                padding: 30px 20px;
                background: #ffffff;
                border-radius: 16px;
                margin: 15px;
                box-shadow: 0 10px 30px rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
            }
            .sidebar-brand:hover {
                transform: scale(1.02);
                box-shadow: 0 15px 40px rgba(255, 255, 255, 0.15);
            }
            .sidebar-brand h2 {
                color: #000000 !important;
                margin: 0 !important;
                font-size: 28px !important;
                font-weight: 800 !important;
            }
            .sidebar-brand-sub {
                font-size: 11px !important;
                font-weight: 700 !important;
                color: #333333 !important;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 5px;
            }
            
            /* Logout Button Specific Styling */
            div[data-testid="stSidebar"] .stButton button {
                background: #ef233c !important; /* Vibrant Red */
                color: white !important;
                border: none !important;
                margin-top: 20px;
                box-shadow: 0 4px 15px rgba(239, 35, 60, 0.3);
            }
            div[data-testid="stSidebar"] .stButton button:hover {
                background: #d90429 !important;
                box-shadow: 0 6px 20px rgba(239, 35, 60, 0.4);
            }
            
            /* Styled Headers */
            h1, h2, h3 {
                font-weight: 800 !important;
                color: #ffffff !important;
                letter-spacing: -0.5px;
            }
            
            /* Buttons & Inputs */
            .stButton>button {
                background: #ffffff !important;
                color: #000000 !important;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-weight: 700;
                width: 100%;
                transition: all 0.2s ease;
            }
            .stButton>button:hover {
                background: #e2e8f0 !important;
                transform: scale(1.02);
            }

            /* Inputs and Selectboxes */
            .stTextInput>div>div>input, .stSelectbox>div>div>div {
                background-color: #2d3748 !important;
                color: white !important;
                border: 1px solid var(--border-color) !important;
            }
            
            /* Glassmorphism for Containers */
            .stForm {
                background: var(--card-bg) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 20px !important;
                padding: 40px !important;
                box-shadow: 0 20px 50px rgba(0,0,0,0.4) !important;
            }
            .stForm * {
                color: white !important;
            }
            
            /* Dataframe/Table Polish */
            .stDataFrame {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid var(--border-color);
                background-color: var(--card-bg) !important;
            }

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
                background-color: transparent !important;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent !important;
                border-radius: 4px 4px 0px 0px;
                color: var(--text-muted) !important;
            }
            .stTabs [aria-selected="true"] {
                color: white !important;
                border-bottom-color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Database Functions ---
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    
    # Create Suppliers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT
    )''')
    
    # Create Medicines table
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        manufacturer TEXT,
        batch_no TEXT,
        expiry_date DATE,
        quantity INTEGER DEFAULT 0,
        unit_price REAL DEFAULT 0.0,
        reorder_level INTEGER DEFAULT 10,
        supplier_id INTEGER,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )''')
    
    # Create Customers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        credit_limit REAL DEFAULT 0.0
    )''')
    
    # Create Orders table
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date DATE DEFAULT CURRENT_DATE,
        status TEXT DEFAULT 'Pending',
        total_amount REAL DEFAULT 0.0,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )''')
    
    # Create Order Items table
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        medicine_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )''')
    
    # Seed default admin user
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ('admin', 'admin123', 'Admin'))
    
    # Check if we need to seed dummy data
    cursor.execute("SELECT COUNT(*) FROM medicines")
    if cursor.fetchone()[0] == 0:
        seed_dummy_data(cursor)

    conn.commit()
    conn.close()

def seed_dummy_data(cursor):
    # Suppliers
    suppliers = [
        ('Global Pharma Solutions', 'Dr. Smith', '1234567890', 'contact@globalpharma.com', '123 Medical Park, NY'),
        ('SafeMeds Inc.', 'Jane Doe', '0987654321', 'sales@safemeds.com', '456 Pharma Rd, CA'),
        ('BioLife Distribution', 'Mark Wilson', '1122334455', 'info@biolife.com', '789 Bio Blvd, TX')
    ]
    cursor.executemany("INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)", suppliers)
    
    # Medicines
    medicines = [
        ('Paracetamol 500mg', 'Analgesic', 'PharmaCorp', 'BATCH001', '2026-12-31', 500, 0.50, 50, 1),
        ('Amoxicillin 250mg', 'Antibiotic', 'MediLife', 'BATCH002', '2026-06-15', 200, 1.20, 30, 1),
        ('Lisinopril 10mg', 'Hypertension', 'SafeHealth', 'BATCH003', '2027-01-20', 150, 0.85, 40, 2),
        ('Metformin 850mg', 'Anti-diabetic', 'GlobalPharma', 'BATCH004', '2026-10-10', 300, 0.45, 60, 2),
        ('Ibuprofen 400mg', 'NSAID', 'QuickRelief', 'BATCH005', '2025-05-12', 5, 0.65, 20, 3), # Low stock & Expiring soon
        ('Atorvastatin 20mg', 'Cholesterol', 'HeartCare', 'BATCH006', '2026-08-30', 100, 1.50, 25, 3)
    ]
    cursor.executemany("""
        INSERT INTO medicines (name, category, manufacturer, batch_no, expiry_date, quantity, unit_price, reorder_level, supplier_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, medicines)
    
    # Customers
    customers = [
        ('City General Hospital', 'Director James', '5551234', 'orders@cityhospital.org', 'Main St, Downtown', 5000),
        ('St. Mary Pharmacy', 'Sarah Brown', '5555678', 'stmary@pharmacy.com', 'High St, Uptown', 2000),
        ('Family Health Clinic', 'Dr. Adams', '5559900', 'clinic@familyhealth.com', 'Medical Square', 1000)
    ]
    cursor.executemany("INSERT INTO customers (name, contact_person, phone, email, address, credit_limit) VALUES (?, ?, ?, ?, ?, ?)", customers)
    
    # Orders
    orders = [
        (1, '2026-03-28', 'Delivered', 250.00),
        (2, '2026-04-01', 'Confirmed', 120.50),
        (3, date.today().strftime('%Y-%m-%d'), 'Pending', 45.00)
    ]
    cursor.executemany("INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (?, ?, ?, ?)", orders)
    
    # Order Items
    order_items = [
        (1, 1, 100, 0.50),
        (1, 2, 50, 1.20),
        (2, 3, 40, 0.85),
        (3, 4, 100, 0.45)
    ]
    cursor.executemany("INSERT INTO order_items (order_id, medicine_id, quantity, unit_price) VALUES (?, ?, ?, ?)", order_items)

# --- Authentication Logic ---
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def handle_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

    if not st.session_state.logged_in:
        st.markdown("""
            <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh; flex-direction: column; background-color: #0e1117;">
                <div style="background: #1a1c23; padding: 50px; border-radius: 30px; box-shadow: 0 30px 60px rgba(0,0,0,0.5); width: 100%; max-width: 450px; border: 1px solid #2d3748;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 42px;">⚕️ MAMS</h1>
                        <p style="color: #a0aec0; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">Medicine Management</p>
                    </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form", border=False):
                username = st.text_input("Username", placeholder="e.g. admin")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("LOGIN TO DASHBOARD")
                
                if submit:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user[0]
                        st.session_state.role = user[1]
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        st.markdown("""
                </div>
                <p style="color: #a0aec0; margin-top: 30px; font-size: 12px; font-weight: 600;">© 2024 PHARMA AGENCY SOLUTIONS</p>
            </div>
        """, unsafe_allow_html=True)
        return False
    return True

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# --- Main Application ---
def main():
    init_db()
    apply_custom_styles()
    
    if handle_login():
        # Global Alerts in Sidebar
        low_stock_df = get_low_stock_medicines()
        expiring_soon_df = get_expiring_soon_medicines(30)
        
        st.sidebar.markdown(f"""
            <div class="sidebar-brand">
                <h2>⚕️ MAMS</h2>
                <div class="sidebar-brand-sub">PHARMA MANAGEMENT</div>
            </div>
        """, unsafe_allow_html=True)
        
        if not low_stock_df.empty:
            st.sidebar.warning(f"⚠️ **{len(low_stock_df)}** Low Stock")
        if not expiring_soon_df.empty:
            st.sidebar.error(f"🚨 **{len(expiring_soon_df)}** Expiring")

        st.sidebar.markdown("<div style='padding: 10px 20px; color: #a0aec0; font-size: 12px; font-weight: 700;'>ACCOUNT</div>", unsafe_allow_html=True)
        st.sidebar.markdown(f"""
            <div style="padding: 0 20px; margin-bottom: 20px;">
                <div style="color: #ffffff; font-weight: 700; font-size: 15px;">{st.session_state.username}</div>
                <div style="color: #a0aec0; font-weight: 600; font-size: 12px; text-transform: uppercase;">{st.session_state.role}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("<div style='padding: 0 20px; color: #a0aec0; font-size: 12px; font-weight: 700;'>NAVIGATION</div>", unsafe_allow_html=True)
        
        menu = ["Dashboard", "Medicines", "Suppliers", "Customers", "Orders", "Reports"]
        if st.session_state.role == "Admin":
            menu.append("User Management")
        
        choice = st.sidebar.selectbox("Navigation", menu)
        
        if st.sidebar.button("Logout"):
            logout()

        if choice == "Dashboard":
            render_dashboard()
        elif choice == "Medicines":
            render_medicines()
        elif choice == "Suppliers":
            render_suppliers()
        elif choice == "Customers":
            render_customers()
        elif choice == "Orders":
            render_orders()
        elif choice == "Reports":
            render_reports()
        elif choice == "User Management":
            render_users()

# --- Helper Functions ---
def get_low_stock_medicines():
    conn = get_connection()
    df = pd.read_sql_query("SELECT name, quantity, reorder_level FROM medicines WHERE quantity < reorder_level", conn)
    conn.close()
    return df

def get_expiring_soon_medicines(days=30):
    conn = get_connection()
    target_date = (date.today() + timedelta(days=days)).strftime('%Y-%m-%d')
    df = pd.read_sql_query("SELECT name, expiry_date FROM medicines WHERE expiry_date <= ?", conn, params=(target_date,))
    conn.close()
    return df

# --- Placeholder Render Functions ---
def render_dashboard():
    st.title("📊 Dashboard Overview")
    
    # Check for alerts
    low_stock_df = get_low_stock_medicines()
    expiring_soon_df = get_expiring_soon_medicines(30)
    
    if not low_stock_df.empty or not expiring_soon_df.empty:
        with st.container():
            if not low_stock_df.empty:
                st.warning(f"⚠️ **Low Stock Alert:** {len(low_stock_df)} medicines are below reorder level. Please check the inventory.")
            if not expiring_soon_df.empty:
                st.error(f"🚨 **Expiry Alert:** {len(expiring_soon_df)} medicines are expiring within 30 days. Prioritize stock clearance.")

    # Summary Metrics - Modern Card Layout
    conn = get_connection()
    total_medicines = pd.read_sql_query("SELECT COUNT(*) FROM medicines", conn).iloc[0,0]
    today_orders = pd.read_sql_query("SELECT COUNT(*) FROM orders WHERE order_date = CURRENT_DATE", conn).iloc[0,0]
    monthly_revenue = pd.read_sql_query("SELECT SUM(total_amount) FROM orders WHERE order_date >= date('now', 'start of month')", conn).iloc[0,0] or 0.0
    low_stock_count = len(low_stock_df)
    conn.close()

    # Custom HTML for metric cards with refined design
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    def metric_card(label, value, icon):
        return f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
                <div style="position: absolute; bottom: -20px; right: -10px; font-size: 80px; opacity: 0.03; transform: rotate(-15deg); color: white;">{icon}</div>
            </div>
        """

    with m_col1:
        st.markdown(metric_card("Total Medicines", total_medicines, "📦"), unsafe_allow_html=True)
    with m_col2:
        st.markdown(metric_card("Low Stock Items", low_stock_count, "⚠️"), unsafe_allow_html=True)
    with m_col3:
        st.markdown(metric_card("Today's Orders", today_orders, "🛒"), unsafe_allow_html=True)
    with m_col4:
        st.markdown(metric_card("Monthly Revenue", f"${monthly_revenue:,.0f}", "💰"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts & Tables
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Inventory Stock Levels")
        conn = get_connection()
        stock_df = pd.read_sql_query("SELECT name, quantity FROM medicines ORDER BY quantity DESC LIMIT 10", conn)
        conn.close()
        if not stock_df.empty:
            st.bar_chart(stock_df.set_index('name'), color="#007bff")
        else:
            st.info("No medicine data available for stock levels chart.")

    with c2:
        st.subheader("Recent Activity")
        conn = get_connection()
        recent_orders = pd.read_sql_query("""
            SELECT o.id as ID, c.name as Customer, o.total_amount as Total, o.status as Status
            FROM orders o 
            JOIN customers c ON o.customer_id = c.id 
            ORDER BY o.id DESC LIMIT 5
        """, conn)
        conn.close()
        if not recent_orders.empty:
            st.dataframe(recent_orders, use_container_width=True, hide_index=True)
        else:
            st.info("No recent orders found.")

def render_medicines():
    st.title("💊 Medicine Management")
    
    tabs = st.tabs(["Inventory", "Add Medicine", "Edit/Delete"])
    
    with tabs[0]:
        st.subheader("Inventory List")
        
        # Search and Filter
        col1, col2 = st.columns([2, 1])
        search_query = col1.text_input("Search by name", "")
        conn = get_connection()
        categories = pd.read_sql_query("SELECT DISTINCT category FROM medicines", conn)['category'].tolist()
        conn.close()
        category_filter = col2.selectbox("Filter by Category", ["All"] + categories)
        
        # Build Query
        query = "SELECT m.*, s.name as supplier_name FROM medicines m LEFT JOIN suppliers s ON m.supplier_id = s.id WHERE 1=1"
        params = []
        if search_query:
            query += " AND m.name LIKE ?"
            params.append(f"%{search_query}%")
        if category_filter != "All":
            query += " AND m.category = ?"
            params.append(category_filter)
            
        conn = get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df.empty:
            # Highlight low stock
            def highlight_low_stock(row):
                return ['background-color: #ffcccc' if row.quantity < row.reorder_level else '' for _ in row]
            
            st.dataframe(df.style.apply(highlight_low_stock, axis=1), use_container_width=True)
        else:
            st.info("No medicines found matching the criteria.")

    with tabs[1]:
        st.subheader("Add New Medicine")
        with st.form("add_medicine_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Medicine Name")
            category = col2.text_input("Category")
            manufacturer = col1.text_input("Manufacturer")
            batch_no = col2.text_input("Batch No")
            expiry_date = col1.date_input("Expiry Date", min_value=date.today() + timedelta(days=1))
            quantity = col2.number_input("Quantity", min_value=0, step=1)
            unit_price = col1.number_input("Unit Price", min_value=0.0, step=0.01)
            reorder_level = col2.number_input("Reorder Level", min_value=0, step=1, value=10)
            
            # Fetch suppliers for dropdown
            conn = get_connection()
            suppliers_df = pd.read_sql_query("SELECT id, name FROM suppliers", conn)
            conn.close()
            supplier_options = {row['name']: row['id'] for _, row in suppliers_df.iterrows()}
            supplier_name = st.selectbox("Supplier", options=list(supplier_options.keys()) if supplier_options else ["None"])
            
            submit = st.form_submit_button("Add Medicine")
            if submit:
                if not name:
                    st.error("Medicine name is required.")
                elif not supplier_options:
                    st.error("Please add a supplier first.")
                elif expiry_date <= date.today():
                    st.error("Expiry date must be in the future.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO medicines (name, category, manufacturer, batch_no, expiry_date, quantity, unit_price, reorder_level, supplier_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (name, category, manufacturer, batch_no, expiry_date.strftime('%Y-%m-%d'), quantity, unit_price, reorder_level, supplier_options.get(supplier_name)))
                        conn.commit()
                        conn.close()
                        st.success(f"Medicine '{name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding medicine: {e}")

    with tabs[2]:
        st.subheader("Edit or Delete Medicine")
        conn = get_connection()
        medicines_list = pd.read_sql_query("SELECT id, name FROM medicines", conn)
        conn.close()
        
        if not medicines_list.empty:
            med_options = {row['name']: row['id'] for _, row in medicines_list.iterrows()}
            selected_med_name = st.selectbox("Select Medicine to Edit/Delete", list(med_options.keys()))
            selected_med_id = med_options[selected_med_name]
            
            # Load existing data
            conn = get_connection()
            med_data = pd.read_sql_query("SELECT * FROM medicines WHERE id = ?", conn, params=(selected_med_id,)).iloc[0]
            conn.close()
            
            with st.form("edit_medicine_form"):
                col1, col2 = st.columns(2)
                e_name = col1.text_input("Medicine Name", value=med_data['name'])
                e_category = col2.text_input("Category", value=med_data['category'])
                e_manufacturer = col1.text_input("Manufacturer", value=med_data['manufacturer'])
                e_batch_no = col2.text_input("Batch No", value=med_data['batch_no'])
                e_expiry_date = col1.date_input("Expiry Date", value=datetime.strptime(med_data['expiry_date'], '%Y-%m-%d').date())
                e_quantity = col2.number_input("Quantity", min_value=0, step=1, value=int(med_data['quantity']))
                e_unit_price = col1.number_input("Unit Price", min_value=0.0, step=0.01, value=float(med_data['unit_price']))
                e_reorder_level = col2.number_input("Reorder Level", min_value=0, step=1, value=int(med_data['reorder_level']))
                
                # Fetch suppliers
                conn = get_connection()
                suppliers_df = pd.read_sql_query("SELECT id, name FROM suppliers", conn)
                conn.close()
                supplier_options = {row['name']: row['id'] for _, row in suppliers_df.iterrows()}
                current_supplier_name = next((k for k, v in supplier_options.items() if v == med_data['supplier_id']), None)
                e_supplier_name = st.selectbox("Supplier", options=list(supplier_options.keys()), index=list(supplier_options.keys()).index(current_supplier_name) if current_supplier_name else 0)
                
                c1, c2 = st.columns(2)
                update_btn = c1.form_submit_button("Update Medicine")
                delete_btn = c2.form_submit_button("Delete Medicine", type="primary")
                
                if update_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE medicines SET name=?, category=?, manufacturer=?, batch_no=?, expiry_date=?, quantity=?, unit_price=?, reorder_level=?, supplier_id=?
                        WHERE id=?
                    """, (e_name, e_category, e_manufacturer, e_batch_no, e_expiry_date.strftime('%Y-%m-%d'), e_quantity, e_unit_price, e_reorder_level, supplier_options.get(e_supplier_name), selected_med_id))
                    conn.commit()
                    conn.close()
                    st.success("Medicine updated successfully!")
                    st.rerun()
                
                if delete_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM medicines WHERE id = ?", (selected_med_id,))
                    conn.commit()
                    conn.close()
                    st.success("Medicine deleted successfully!")
                    st.rerun()
        else:
            st.info("No medicines available to edit.")

def render_suppliers():
    st.title("🚛 Supplier Management")
    
    tabs = st.tabs(["Supplier List", "Add Supplier", "Edit/Delete"])
    
    with tabs[0]:
        st.subheader("All Suppliers")
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No suppliers found.")

    with tabs[1]:
        st.subheader("Add New Supplier")
        with st.form("add_supplier_form", clear_on_submit=True):
            name = st.text_input("Supplier Name")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            
            submit = st.form_submit_button("Add Supplier")
            if submit:
                if not name:
                    st.error("Supplier name is required.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                                   (name, contact_person, phone, email, address))
                    conn.commit()
                    conn.close()
                    st.success(f"Supplier '{name}' added successfully!")
                    st.rerun()

    with tabs[2]:
        st.subheader("Edit or Delete Supplier")
        conn = get_connection()
        suppliers_list = pd.read_sql_query("SELECT id, name FROM suppliers", conn)
        conn.close()
        
        if not suppliers_list.empty:
            sup_options = {row['name']: row['id'] for _, row in suppliers_list.iterrows()}
            selected_sup_name = st.selectbox("Select Supplier to Edit/Delete", list(sup_options.keys()))
            selected_sup_id = sup_options[selected_sup_name]
            
            conn = get_connection()
            sup_data = pd.read_sql_query("SELECT * FROM suppliers WHERE id = ?", conn, params=(selected_sup_id,)).iloc[0]
            conn.close()
            
            with st.form("edit_supplier_form"):
                e_name = st.text_input("Supplier Name", value=sup_data['name'])
                e_contact_person = st.text_input("Contact Person", value=sup_data['contact_person'])
                e_phone = st.text_input("Phone", value=sup_data['phone'])
                e_email = st.text_input("Email", value=sup_data['email'])
                e_address = st.text_area("Address", value=sup_data['address'])
                
                c1, c2 = st.columns(2)
                update_btn = c1.form_submit_button("Update Supplier")
                delete_btn = c2.form_submit_button("Delete Supplier", type="primary")
                
                if update_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE suppliers SET name=?, contact_person=?, phone=?, email=?, address=? WHERE id=?",
                                   (e_name, e_contact_person, e_phone, e_email, e_address, selected_sup_id))
                    conn.commit()
                    conn.close()
                    st.success("Supplier updated successfully!")
                    st.rerun()
                
                if delete_btn:
                    # Check if supplier is linked to medicines
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM medicines WHERE supplier_id = ?", (selected_sup_id,))
                    if cursor.fetchone()[0] > 0:
                        st.error("Cannot delete supplier linked to medicines. Please reassign medicines first.")
                    else:
                        cursor.execute("DELETE FROM suppliers WHERE id = ?", (selected_sup_id,))
                        conn.commit()
                        st.success("Supplier deleted successfully!")
                        st.rerun()
                    conn.close()
        else:
            st.info("No suppliers available to edit.")

def render_customers():
    st.title("🏥 Customer Management")
    
    tabs = st.tabs(["Customer List", "Add Customer", "Edit/Delete"])
    
    with tabs[0]:
        st.subheader("All Customers")
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM customers", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No customers found.")

    with tabs[1]:
        st.subheader("Add New Customer")
        with st.form("add_customer_form", clear_on_submit=True):
            name = st.text_input("Customer Name (Hospital/Clinic/Pharmacy)")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            credit_limit = st.number_input("Credit Limit", min_value=0.0, step=100.0)
            
            submit = st.form_submit_button("Add Customer")
            if submit:
                if not name:
                    st.error("Customer name is required.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO customers (name, contact_person, phone, email, address, credit_limit) VALUES (?, ?, ?, ?, ?, ?)",
                                   (name, contact_person, phone, email, address, credit_limit))
                    conn.commit()
                    conn.close()
                    st.success(f"Customer '{name}' added successfully!")
                    st.rerun()

    with tabs[2]:
        st.subheader("Edit or Delete Customer")
        conn = get_connection()
        customers_list = pd.read_sql_query("SELECT id, name FROM customers", conn)
        conn.close()
        
        if not customers_list.empty:
            cust_options = {row['name']: row['id'] for _, row in customers_list.iterrows()}
            selected_cust_name = st.selectbox("Select Customer to Edit/Delete", list(cust_options.keys()))
            selected_cust_id = cust_options[selected_cust_name]
            
            conn = get_connection()
            cust_data = pd.read_sql_query("SELECT * FROM customers WHERE id = ?", conn, params=(selected_cust_id,)).iloc[0]
            conn.close()
            
            with st.form("edit_customer_form"):
                e_name = st.text_input("Customer Name", value=cust_data['name'])
                e_contact_person = st.text_input("Contact Person", value=cust_data['contact_person'])
                e_phone = st.text_input("Phone", value=cust_data['phone'])
                e_email = st.text_input("Email", value=cust_data['email'])
                e_address = st.text_area("Address", value=cust_data['address'])
                e_credit_limit = st.number_input("Credit Limit", min_value=0.0, step=100.0, value=float(cust_data['credit_limit']))
                
                c1, c2 = st.columns(2)
                update_btn = c1.form_submit_button("Update Customer")
                delete_btn = c2.form_submit_button("Delete Customer", type="primary")
                
                if update_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE customers SET name=?, contact_person=?, phone=?, email=?, address=?, credit_limit=? WHERE id=?",
                                   (e_name, e_contact_person, e_phone, e_email, e_address, e_credit_limit, selected_cust_id))
                    conn.commit()
                    conn.close()
                    st.success("Customer updated successfully!")
                    st.rerun()
                
                if delete_btn:
                    # Check if customer has orders
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (selected_cust_id,))
                    if cursor.fetchone()[0] > 0:
                        st.error("Cannot delete customer with existing orders.")
                    else:
                        cursor.execute("DELETE FROM customers WHERE id = ?", (selected_cust_id,))
                        conn.commit()
                        st.success("Customer deleted successfully!")
                        st.rerun()
                    conn.close()
        else:
            st.info("No customers available to edit.")

def render_orders():
    st.title("🛒 Order Management")
    
    tabs = st.tabs(["Order List", "Create New Order", "Update Status", "View Invoice", "Delete Order"])
    
    with tabs[0]:
        st.subheader("All Orders")
        conn = get_connection()
        df = pd.read_sql_query("""
            SELECT o.id, c.name as customer, o.order_date, o.status, o.total_amount 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.id 
            ORDER BY o.id DESC
        """, conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No orders found.")

    with tabs[1]:
        st.subheader("Create New Order")
        if 'temp_order_items' not in st.session_state:
            st.session_state.temp_order_items = []
            
        conn = get_connection()
        customers_df = pd.read_sql_query("SELECT id, name FROM customers", conn)
        medicines_df = pd.read_sql_query("SELECT id, name, unit_price, quantity FROM medicines WHERE quantity > 0", conn)
        conn.close()
        
        if customers_df.empty:
            st.warning("Please add customers first.")
        elif medicines_df.empty:
            st.warning("No medicines in stock.")
        else:
            with st.form("add_item_form"):
                col1, col2, col3 = st.columns([2, 1, 1])
                med_options = {row['name']: (row['id'], row['unit_price'], row['quantity']) for _, row in medicines_df.iterrows()}
                selected_med = col1.selectbox("Select Medicine", list(med_options.keys()))
                qty = col2.number_input("Quantity", min_value=1, step=1)
                add_item = col3.form_submit_button("Add to Order")
                
                if add_item:
                    med_id, price, available = med_options[selected_med]
                    if qty > available:
                        st.error(f"Only {available} units available.")
                    else:
                        st.session_state.temp_order_items.append({
                            'medicine_id': med_id,
                            'name': selected_med,
                            'quantity': qty,
                            'unit_price': price,
                            'subtotal': qty * price
                        })
            
            if st.session_state.temp_order_items:
                st.write("### Order Items")
                temp_df = pd.DataFrame(st.session_state.temp_order_items)
                st.table(temp_df)
                total_amt = temp_df['subtotal'].sum()
                st.write(f"**Total Amount: ${total_amt:,.2f}**")
                
                if st.button("Clear Items"):
                    st.session_state.temp_order_items = []
                    st.rerun()
                
                with st.form("finalize_order_form"):
                    cust_options = {row['name']: row['id'] for _, row in customers_df.iterrows()}
                    selected_cust = st.selectbox("Select Customer", list(cust_options.keys()))
                    order_date = st.date_input("Order Date", value=date.today())
                    submit_order = st.form_submit_button("Place Order")
                    
                    if submit_order:
                        conn = get_connection()
                        cursor = conn.cursor()
                        try:
                            cursor.execute("INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES (?, ?, ?, ?)",
                                           (cust_options[selected_cust], order_date.strftime('%Y-%m-%d'), 'Pending', total_amt))
                            order_id = cursor.lastrowid
                            for item in st.session_state.temp_order_items:
                                cursor.execute("INSERT INTO order_items (order_id, medicine_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                                               (order_id, item['medicine_id'], item['quantity'], item['unit_price']))
                            conn.commit()
                            st.session_state.temp_order_items = []
                            st.success(f"Order #{order_id} placed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error placing order: {e}")
                        finally:
                            conn.close()

    with tabs[2]:
        st.subheader("Update Order Status")
        conn = get_connection()
        df = pd.read_sql_query("SELECT o.id, o.status FROM orders o ORDER BY o.id DESC", conn)
        conn.close()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            order_id_to_update = col1.selectbox("Select Order ID", df['id'].tolist(), key="status_order_id")
            current_status = df[df['id'] == order_id_to_update]['status'].values[0]
            new_status = col2.selectbox("New Status", ["Pending", "Confirmed", "Delivered", "Cancelled"], 
                                        index=["Pending", "Confirmed", "Delivered", "Cancelled"].index(current_status), 
                                        key="new_status")
            
            if st.button("Update Status"):
                conn = get_connection()
                cursor = conn.cursor()
                if new_status == "Confirmed" and current_status != "Confirmed":
                    items = pd.read_sql_query("SELECT medicine_id, quantity FROM order_items WHERE order_id = ?", conn, params=(order_id_to_update,))
                    for _, item in items.iterrows():
                        cursor.execute("SELECT quantity, name FROM medicines WHERE id = ?", (item['medicine_id'],))
                        stock_data = cursor.fetchone()
                        if stock_data[0] < item['quantity']:
                            st.error(f"Not enough stock for {stock_data[1]}! Available: {stock_data[0]}")
                            conn.close()
                            return
                    for _, item in items.iterrows():
                        cursor.execute("UPDATE medicines SET quantity = quantity - ? WHERE id = ?", (item['quantity'], item['medicine_id']))
                cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id_to_update))
                conn.commit()
                conn.close()
                st.success(f"Order #{order_id_to_update} updated!")
                st.rerun()
        else:
            st.info("No orders to update.")

    with tabs[3]:
        st.subheader("View Invoice")
        conn = get_connection()
        all_orders = pd.read_sql_query("SELECT id FROM orders ORDER BY id DESC", conn)
        conn.close()
        if not all_orders.empty:
            inv_order_id = st.selectbox("Select Order ID for Invoice", all_orders['id'].tolist(), key="inv_order_id")
            if inv_order_id:
                conn = get_connection()
                order_info = pd.read_sql_query("""
                    SELECT o.*, c.name as customer_name, c.address, c.phone, c.email
                    FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.id = ?
                """, conn, params=(inv_order_id,)).iloc[0]
                items_info = pd.read_sql_query("""
                    SELECT oi.*, m.name as medicine_name FROM order_items oi 
                    JOIN medicines m ON oi.medicine_id = m.id WHERE oi.order_id = ?
                """, conn, params=(inv_order_id,))
                conn.close()
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white;">
                    <h2 style="text-align: center;">INVOICE</h2><hr>
                    <div style="display: flex; justify-content: space-between;">
                        <div><strong>Bill To:</strong><br>{order_info['customer_name']}<br>{order_info['address']}<br>Phone: {order_info['phone']}</div>
                        <div style="text-align: right;"><strong>Order ID:</strong> #{order_info['id']}<br><strong>Date:</strong> {order_info['order_date']}<br><strong>Status:</strong> {order_info['status']}</div>
                    </div><br>
                </div>
                """, unsafe_allow_html=True)
                items_info['Subtotal'] = items_info['quantity'] * items_info['unit_price']
                st.table(items_info[['medicine_name', 'quantity', 'unit_price', 'Subtotal']])
                st.markdown(f"<h3 style='text-align: right;'>Total: ${order_info['total_amount']:,.2f}</h3>", unsafe_allow_html=True)
        else:
            st.info("No orders to view invoice.")

    with tabs[4]:
        st.subheader("Delete Order")
        conn = get_connection()
        all_orders = pd.read_sql_query("SELECT id FROM orders ORDER BY id DESC", conn)
        conn.close()
        if not all_orders.empty:
            order_id_to_del = st.selectbox("Select Order ID to Delete", all_orders['id'].tolist(), key="del_order_id")
            if st.button("Delete Order", type="primary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id_to_del,))
                cursor.execute("DELETE FROM orders WHERE id = ?", (order_id_to_del,))
                conn.commit()
                conn.close()
                st.success(f"Order #{order_id_to_del} deleted.")
                st.rerun()
        else:
            st.info("No orders to delete.")

def render_reports():
    st.title("📈 Reports & Analytics")
    
    tabs = st.tabs(["Sales Report", "Low Stock Report", "Expiry Report"])
    
    with tabs[0]:
        st.subheader("Sales Report")
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=date.today() - timedelta(days=30))
        end_date = col2.date_input("End Date", value=date.today())
        
        if start_date > end_date:
            st.error("Start date must be before end date.")
        else:
            conn = get_connection()
            query = """
                SELECT o.id as Order_ID, c.name as Customer, o.order_date as Date, o.status as Status, o.total_amount as Amount
                FROM orders o 
                JOIN customers c ON o.customer_id = c.id 
                WHERE o.order_date BETWEEN ? AND ?
                ORDER BY o.order_date DESC
            """
            sales_df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            conn.close()
            
            if not sales_df.empty:
                st.write(f"Total Sales: **${sales_df['Amount'].sum():,.2f}**")
                st.dataframe(sales_df, use_container_width=True)
                
                csv = sales_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "sales_report.csv", "text/csv")
            else:
                st.info("No sales found in this date range.")

    with tabs[1]:
        st.subheader("Low Stock Report")
        conn = get_connection()
        ls_df = pd.read_sql_query("""
            SELECT name, category, quantity, reorder_level 
            FROM medicines 
            WHERE quantity < reorder_level
        """, conn)
        conn.close()
        
        if not ls_df.empty:
            st.warning(f"Found {len(ls_df)} items with low stock.")
            st.dataframe(ls_df, use_container_width=True)
            csv = ls_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "low_stock_report.csv", "text/csv")
        else:
            st.success("All items have sufficient stock.")

    with tabs[2]:
        st.subheader("Expiry Report")
        days_ahead = st.selectbox("Expiring in next (days):", [30, 60, 90])
        conn = get_connection()
        target_date = (date.today() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        exp_df = pd.read_sql_query("""
            SELECT name, category, batch_no, expiry_date, quantity 
            FROM medicines 
            WHERE expiry_date <= ? AND expiry_date >= CURRENT_DATE
        """, conn, params=(target_date,))
        conn.close()
        
        if not exp_df.empty:
            st.error(f"Found {len(exp_df)} items expiring within {days_ahead} days.")
            st.dataframe(exp_df, use_container_width=True)
            csv = exp_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "expiry_report.csv", "text/csv")
        else:
            st.success(f"No items expiring within {days_ahead} days.")

def render_users():
    st.title("👤 User Management")
    
    if st.session_state.role != "Admin":
        st.error("Access Denied. Admins only.")
        return

    tabs = st.tabs(["User List", "Add User", "Update/Delete User"])
    
    with tabs[0]:
        st.subheader("System Users")
        conn = get_connection()
        df = pd.read_sql_query("SELECT id, username, role FROM users", conn)
        conn.close()
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Add New User")
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Staff"])
            submit = st.form_submit_button("Add User")
            
            if submit:
                if not new_username or not new_password:
                    st.error("Username and Password are required.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                       (new_username, new_password, new_role))
                        conn.commit()
                        conn.close()
                        st.success(f"User '{new_username}' added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    with tabs[2]:
        st.subheader("Update or Delete User")
        conn = get_connection()
        users_df = pd.read_sql_query("SELECT id, username FROM users WHERE username != ?", conn, params=(st.session_state.username,))
        conn.close()
        
        if not users_df.empty:
            user_options = {row['username']: row['id'] for _, row in users_df.iterrows()}
            selected_user_name = st.selectbox("Select User", list(user_options.keys()))
            selected_user_id = user_options[selected_user_name]
            
            # Load user data
            conn = get_connection()
            user_data = pd.read_sql_query("SELECT * FROM users WHERE id = ?", conn, params=(selected_user_id,)).iloc[0]
            conn.close()
            
            with st.form("edit_user_form"):
                e_username = st.text_input("Username", value=user_data['username'])
                e_password = st.text_input("New Password (leave empty to keep current)", type="password")
                e_role = st.selectbox("Role", ["Admin", "Staff"], index=0 if user_data['role'] == "Admin" else 1)
                
                c1, c2 = st.columns(2)
                update_btn = c1.form_submit_button("Update User")
                delete_btn = c2.form_submit_button("Delete User", type="primary")
                
                if update_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    if e_password:
                        cursor.execute("UPDATE users SET username=?, password=?, role=? WHERE id=?", (e_username, e_password, e_role, selected_user_id))
                    else:
                        cursor.execute("UPDATE users SET username=?, role=? WHERE id=?", (e_username, e_role, selected_user_id))
                    conn.commit()
                    conn.close()
                    st.success("User updated successfully!")
                    st.rerun()
                
                if delete_btn:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id = ?", (selected_user_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"User '{selected_user_name}' deleted.")
                    st.rerun()
        else:
            st.info("No other users to manage.")

if __name__ == "__main__":
    main()
