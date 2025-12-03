import streamlit as st
import pywhatkit
import sqlite3
import os
import csv
import io
from datetime import datetime
from PIL import Image
import uuid

# --- DATABASE SETUP ---
DB_PATH = "vinci_products.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        currency TEXT DEFAULT 'R ZAR',
        condition TEXT DEFAULT 'Good',
        category TEXT DEFAULT 'Other',
        description TEXT,
        location TEXT,
        whatsapp TEXT,
        images TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sold INTEGER DEFAULT 0,
        share_count INTEGER DEFAULT 0,
        last_shared TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        old_price REAL,
        new_price REAL,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        platform TEXT DEFAULT 'Both',
        template TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# --- CATEGORIES ---
CATEGORIES = [
    "Electronics 📱", "Furniture 🛋️", "Kitchen 🍳", "Appliances 🔌",
    "Garden 🌱", "Clothing 👕", "Sports ⚽", "Books 📚",
    "Toys 🧸", "Decor 🖼️", "Tools 🔧", "Vehicles 🚗",
    "Beauty 💄", "Baby 👶", "Music 🎸", "Gaming 🎮",
    "Collectibles 🏆", "Jewelry 💎", "Art 🎨", "Pets 🐕",
    "Office 💼", "Health 🏥", "Food 🍕", "Other 📦"
]

CONDITIONS = ["New", "Like New", "Good", "Fair", "For Parts"]
CURRENCIES = ["R ZAR", "$ USD", "£ GBP", "€ EUR"]

PRICE_SUGGESTIONS = {
    "Electronics 📱": {"New": 5000, "Like New": 4000, "Good": 3000, "Fair": 2000, "For Parts": 500},
    "Furniture 🛋️": {"New": 3000, "Like New": 2500, "Good": 1800, "Fair": 1000, "For Parts": 300},
    "Kitchen 🍳": {"New": 800, "Like New": 600, "Good": 400, "Fair": 250, "For Parts": 100},
    "Appliances 🔌": {"New": 2000, "Like New": 1500, "Good": 1000, "Fair": 600, "For Parts": 200},
    "Clothing 👕": {"New": 500, "Like New": 350, "Good": 200, "Fair": 100, "For Parts": 30},
    "Other 📦": {"New": 500, "Like New": 350, "Good": 250, "Fair": 150, "For Parts": 50},
}

def get_price_suggestion(category, condition):
    cat_prices = PRICE_SUGGESTIONS.get(category, PRICE_SUGGESTIONS["Other 📦"])
    base_price = cat_prices.get(condition, 250)
    return base_price, int(base_price * 0.7), int(base_price * 1.3)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Vinci-Vantage Pro", page_icon="🏪", layout="wide")

# --- HELPER FUNCTIONS ---
def get_currency_symbol(currency):
    return currency.split()[0]

def save_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        ext = uploaded_file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        img = Image.open(uploaded_file)
        img.thumbnail((1920, 1920))
        img.save(filepath, quality=85, optimize=True)
        return filename
    return None

def needs_repost(last_shared):
    if last_shared is None:
        return True
    try:
        last = datetime.strptime(last_shared, "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - last).days >= 7
    except:
        return True

# --- DATABASE OPERATIONS ---
def add_product(name, price, currency, condition, category, description, location, whatsapp, images):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO products (name, price, currency, condition, category, description, location, whatsapp, images)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, price, currency, condition, category, description, location, whatsapp, images))
    conn.commit()
    conn.close()

def get_products(category_filter=None, status_filter=None, search_query=None):
    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    if status_filter == "Available":
        query += " AND sold = 0"
    elif status_filter == "Sold":
        query += " AND sold = 1"
    if search_query:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    query += " ORDER BY created_at DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_product(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_product(product_id, **kwargs):
    conn = get_db()
    c = conn.cursor()
    if 'price' in kwargs:
        old = get_product(product_id)
        if old and old['price'] != kwargs['price']:
            c.execute("INSERT INTO price_history (product_id, old_price, new_price) VALUES (?, ?, ?)",
                     (product_id, old['price'], kwargs['price']))
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [product_id]
    c.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    c = conn.cursor()
    product = get_product(product_id)
    if product and product['images']:
        for img in product['images'].split(','):
            filepath = os.path.join(UPLOAD_DIR, img.strip())
            if os.path.exists(filepath):
                os.remove(filepath)
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    c.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()

def duplicate_product(product_id):
    product = get_product(product_id)
    if product:
        add_product(f"{product['name']} (Copy)", product['price'], product['currency'],
                   product['condition'], product['category'], product['description'],
                   product['location'], product['whatsapp'], product['images'])

def get_price_history(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM price_history WHERE product_id = ? ORDER BY changed_at DESC", (product_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def track_share(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE products SET share_count = share_count + 1, last_shared = ? WHERE id = ?",
             (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))
    conn.commit()
    conn.close()

# --- TEMPLATES ---
def get_templates():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM templates ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_template(name, platform, template):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO templates (name, platform, template) VALUES (?, ?, ?)", (name, platform, template))
    conn.commit()
    conn.close()

def delete_template(template_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()

def apply_template(template_text, product):
    symbol = get_currency_symbol(product['currency'])
    return template_text.replace("{name}", product['name']).replace("{price}", f"{symbol}{product['price']}").replace("{condition}", product['condition']).replace("{description}", product['description'] or "").replace("{location}", product['location'] or "").replace("{category}", product['category'])

# --- STATS ---
def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM products WHERE sold = 0")
    available = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM products WHERE sold = 1")
    sold = c.fetchone()[0]
    c.execute("SELECT SUM(price) FROM products WHERE sold = 0")
    inventory_value = c.fetchone()[0] or 0
    c.execute("SELECT SUM(price) FROM products WHERE sold = 1")
    revenue = c.fetchone()[0] or 0
    c.execute("SELECT SUM(share_count) FROM products")
    total_shares = c.fetchone()[0] or 0
    conn.close()
    return {"total": total, "available": available, "sold": sold, "inventory_value": inventory_value, "revenue": revenue, "total_shares": total_shares}

# --- GENERATE LISTINGS ---
def generate_whatsapp_message(product, template=None):
    symbol = get_currency_symbol(product['currency'])
    if template:
        return apply_template(template, product)
    return f"""🔥 *{product['name'].upper()}* - {product['condition'].upper()}

💰 *Price:* {symbol}{product['price']}
📍 *Location:* {product['location']}

{product['description']}

📱 WhatsApp me if interested!"""

def generate_facebook_post(product, template=None):
    symbol = get_currency_symbol(product['currency'])
    if template:
        return apply_template(template, product)
    return f"""🔥 {product['name'].upper()} - {product['condition'].upper()} - {symbol}{product['price']}

Selling a {product['condition']} {product['name']}. 

{product['description']}

📍 Location: {product['location']}
💰 Price: {symbol}{product['price']}
📩 Message me if interested! First come, first served."""

# --- MAIN APP ---
st.sidebar.title("🏪 Vinci-Vantage Pro")
st.sidebar.markdown("*Complete Commerce Assistant*")
st.sidebar.divider()

menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "➕ Add Product", "📦 Inventory", "📝 Templates", "📱 WhatsApp Automation", "📤 Export Data"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    stats = get_stats()
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Products", stats['total'])
    with col2:
        st.metric("Available", stats['available'])
    with col3:
        st.metric("Sold", stats['sold'])
    with col4:
        st.metric("Inventory Value", f"R{stats['inventory_value']:,.0f}")
    with col5:
        st.metric("Revenue", f"R{stats['revenue']:,.0f}")
    with col6:
        st.metric("Total Shares", stats['total_shares'])
    st.divider()
    st.subheader("Recent Listings")
    products = get_products()[:6]
    if products:
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                symbol = get_currency_symbol(product['currency'])
                if product['images']:
                    img_file = product['images'].split(',')[0].strip()
                    img_path = os.path.join(UPLOAD_DIR, img_file)
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                st.markdown(f"**{product['name']}**")
                st.markdown(f"💰 {symbol}{product['price']}")
                if product['sold']:
                    st.success("SOLD ✓")
                else:
                    st.info("Available")
                st.caption(f"📤 {product['share_count']} shares")
    else:
        st.info("No products yet. Add your first product!")

# --- ADD PRODUCT ---
elif menu == "➕ Add Product":
    st.title("➕ Add New Product")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name *", placeholder="e.g., Samsung Galaxy S21")
            category = st.selectbox("Category *", CATEGORIES)
            condition = st.selectbox("Condition *", CONDITIONS)
            st.markdown("##### 💡 Price Suggestion")
            suggested, low, high = get_price_suggestion(category, condition)
            st.caption(f"Suggested: R{suggested} (Range: R{low} - R{high})")
            price = st.number_input("Price *", min_value=0.0, value=float(suggested))
            currency = st.selectbox("Currency", CURRENCIES)
        with col2:
            location = st.text_input("Pickup Location", placeholder="e.g., Cape Town")
            whatsapp = st.text_input("WhatsApp Number", placeholder="+27821234567")
            description = st.text_area("Description", height=150, placeholder="Describe your item...")
        st.markdown("##### 📸 Product Images")
        uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)
        submitted = st.form_submit_button("➕ Add Product", type="primary", use_container_width=True)
        if submitted:
            if name and price:
                image_filenames = []
                for file in uploaded_files:
                    filename = save_uploaded_image(file)
                    if filename:
                        image_filenames.append(filename)
                images_str = ",".join(image_filenames) if image_filenames else ""
                add_product(name, price, currency, condition, category, description, location, whatsapp, images_str)
                st.success("✅ Product added successfully!")
                st.balloons()
            else:
                st.error("Please fill in required fields (Name and Price)")

# --- INVENTORY ---
elif menu == "📦 Inventory":
    st.title("📦 Inventory Management")
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search products...")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Available", "Sold"])
    with col3:
        category_filter = st.selectbox("Category", ["All"] + CATEGORIES)
    products = get_products(category_filter=category_filter if category_filter != "All" else None, status_filter=status_filter if status_filter != "All" else None, search_query=search if search else None)
    st.divider()
    st.caption(f"Showing {len(products)} products")
    if products:
        for product in products:
            with st.expander(f"{'✅' if product['sold'] else '📦'} {product['name']} - {get_currency_symbol(product['currency'])}{product['price']}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if product['images']:
                        img_file = product['images'].split(',')[0].strip()
                        img_path = os.path.join(UPLOAD_DIR, img_file)
                        if os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                    else:
                        st.info("No image")
                    st.caption(f"📤 Shared {product['share_count']} times")
                    if needs_repost(product['last_shared']):
                        st.warning("⏰ Needs Repost!")
                with col2:
                    st.markdown(f"**Category:** {product['category']}")
                    st.markdown(f"**Condition:** {product['condition']}")
                    st.markdown(f"**Location:** {product['location']}")
                    st.markdown(f"**WhatsApp:** {product['whatsapp']}")
                    st.markdown(f"**Description:** {product['description']}")
                    history = get_price_history(product['id'])
                    if history:
                        with st.popover("🕐 Price History"):
                            for h in history:
                                st.caption(f"R{h['old_price']} → R{h['new_price']} ({h['changed_at']})")
                st.divider()
                action_cols = st.columns(6)
                with action_cols[0]:
                    if st.button("📱 WhatsApp", key=f"wa_{product['id']}"):
                        msg = generate_whatsapp_message(product)
                        st.code(msg)
                        track_share(product['id'])
                with action_cols[1]:
                    if st.button("👤 Facebook", key=f"fb_{product['id']}"):
                        msg = generate_facebook_post(product)
                        st.code(msg)
                        track_share(product['id'])
                with action_cols[2]:
                    if st.button("📋 Duplicate", key=f"dup_{product['id']}"):
                        duplicate_product(product['id'])
                        st.success("Duplicated!")
                        st.rerun()
                with action_cols[3]:
                    if not product['sold']:
                        if st.button("✅ Mark Sold", key=f"sold_{product['id']}"):
                            update_product(product['id'], sold=1)
                            st.rerun()
                    else:
                        if st.button("↩️ Unmark", key=f"unsold_{product['id']}"):
                            update_product(product['id'], sold=0)
                            st.rerun()
                with action_cols[4]:
                    new_price = st.number_input("Price", value=float(product['price']), key=f"price_{product['id']}", label_visibility="collapsed")
                    if new_price != product['price']:
                        if st.button("💰", key=f"upd_{product['id']}"):
                            update_product(product['id'], price=new_price)
                            st.rerun()
                with action_cols[5]:
                    if st.button("🗑️", key=f"del_{product['id']}"):
                        delete_product(product['id'])
                        st.rerun()
    else:
        st.info("No products found.")

# --- TEMPLATES ---
elif menu == "📝 Templates":
    st.title("📝 Message Templates")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Create Template")
        with st.form("template_form"):
            template_name = st.text_input("Template Name", placeholder="e.g., Weekend Special")
            platform = st.selectbox("Platform", ["Both", "WhatsApp", "Facebook"])
            st.caption("Placeholders: `{name}` `{price}` `{condition}` `{description}` `{location}` `{category}`")
            template_text = st.text_area("Template Text", height=200, placeholder="🔥 {name} - ONLY {price}!")
            if st.form_submit_button("💾 Save Template", type="primary"):
                if template_name and template_text:
                    add_template(template_name, platform, template_text)
                    st.success("Template saved!")
                    st.rerun()
    with col2:
        st.subheader("Your Templates")
        templates = get_templates()
        if templates:
            for t in templates:
                with st.expander(f"📄 {t['name']} ({t['platform']})"):
                    st.code(t['template'])
                    if st.button("🗑️ Delete", key=f"del_tmpl_{t['id']}"):
                        delete_template(t['id'])
                        st.rerun()
        else:
            st.info("No templates yet.")

# --- WHATSAPP AUTOMATION ---
elif menu == "📱 WhatsApp Automation":
    st.title("📱 WhatsApp Automation")
    st.warning("⚠️ Make sure you're logged into web.whatsapp.com!")
    tab1, tab2 = st.tabs(["📤 Send Offer", "📢 Bulk Share"])
    with tab1:
        st.subheader("Send Buy Offer")
        phone = st.text_input("Seller Phone", placeholder="+27821234567")
        item_name = st.text_input("Item Name", placeholder="What are you interested in?")
        col1, col2 = st.columns(2)
        with col1:
            offer_price = st.number_input("Your Offer", min_value=0)
        with col2:
            offer_currency = st.selectbox("Currency", CURRENCIES, key="offer_curr")
        if st.button("🚀 Send WhatsApp Offer", type="primary"):
            if phone and offer_price:
                symbol = get_currency_symbol(offer_currency)
                message = f"Hi! I saw your listing for the {item_name} on Facebook. I'm interested. Would you accept {symbol}{offer_price} if I pick it up today?"
                with st.spinner("Opening WhatsApp..."):
                    try:
                        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)
                        st.success("Message sent!")
                    except Exception as e:
                        st.error(f"Error: {e}")
    with tab2:
        st.subheader("Share Products")
        products = get_products(status_filter="Available")
        if products:
            selected = st.multiselect("Select Products", options=[p['id'] for p in products], format_func=lambda x: next((p['name'] for p in products if p['id'] == x), x))
            group_phone = st.text_input("Group/Contact", placeholder="+27821234567")
            if st.button("📤 Share Selected", type="primary"):
                if selected and group_phone:
                    for pid in selected:
                        product = get_product(pid)
                        msg = generate_whatsapp_message(product)
                        try:
                            pywhatkit.sendwhatmsg_instantly(group_phone, msg, wait_time=15, tab_close=False)
                            track_share(pid)
                            st.success(f"Shared: {product['name']}")
                        except Exception as e:
                            st.error(f"Failed: {e}")

# --- EXPORT DATA ---
elif menu == "📤 Export Data":
    st.title("📤 Export Data")
    products = get_products()
    if products:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'Price', 'Currency', 'Condition', 'Category', 'Description', 'Location', 'WhatsApp', 'Sold', 'Shares', 'Created'])
        for p in products:
            writer.writerow([p['name'], p['price'], p['currency'], p['condition'], p['category'], p['description'], p['location'], p['whatsapp'], 'Yes' if p['sold'] else 'No', p['share_count'], p['created_at']])
        st.download_button("📥 Download CSV", output.getvalue(), f"vinci_products_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", type="primary")
        st.divider()
        stats = get_stats()
        st.subheader("📈 Summary")
        st.markdown(f"""
**Total Products:** {stats['total']} | **Available:** {stats['available']} | **Sold:** {stats['sold']}

**Inventory Value:** R{stats['inventory_value']:,.2f} | **Revenue:** R{stats['revenue']:,.2f} | **Shares:** {stats['total_shares']}
        """)
    else:
        st.info("No products to export")

# --- FOOTER ---
st.sidebar.divider()
st.sidebar.caption("Vinci-Vantage Pro v2.0")
st.sidebar.caption("© ArtradePro 2025")
