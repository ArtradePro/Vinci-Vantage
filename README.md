# 🏪 Vinci-Vantage Pro

> **Complete Commerce Assistant for Facebook Marketplace & WhatsApp**

```
╔═══════════════════════════════════════════════════════════════╗
║  🏪 VINCI-VANTAGE PRO v2.0                                    ║
║  The Ultimate Selling Tool                                     ║
╚═══════════════════════════════════════════════════════════════╝
```

## ✨ Features

### 📊 Dashboard & Analytics
- Real-time stats (Total, Available, Sold)
- Inventory value tracking
- Revenue monitoring
- Share counter

### 📦 Full Inventory Management
- SQLite database for persistent storage
- 24 product categories
- 5 condition levels
- Search & filter products
- Price history tracking
- Repost reminders (7+ days)

### 📸 Image Management
- Multi-image upload
- Auto-compression (1920px, 85% quality)
- Supports PNG, JPG, JPEG, WebP

### 💡 Smart Pricing
- AI-powered price suggestions
- Based on category + condition
- Suggested range for negotiation

### 📝 Message Templates
- Create custom templates
- Placeholders: `{name}`, `{price}`, `{condition}`, `{description}`, `{location}`, `{category}`
- Platform-specific (WhatsApp/Facebook/Both)

### 📱 WhatsApp Automation (Unique!)
- Auto-send buy offers to sellers
- Bulk share products to groups
- Track share counts

### 💰 Multi-Currency Support
- 🇿🇦 R ZAR (South African Rand)
- 🇺🇸 $ USD (US Dollar)
- 🇬🇧 £ GBP (British Pound)
- 🇪🇺 € EUR (Euro)

### 📤 Data Export
- CSV export for spreadsheets
- Summary reports

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Open in Browser

Visit: **http://localhost:8501**

---

## 📖 Documentation

See the full **[MANUAL.md](MANUAL.md)** for:
- Detailed feature explanations
- Step-by-step guides
- Tips & best practices
- Troubleshooting

---

## 🗂️ Project Structure

```
Vinci-Vantage/
├── app.py                # Main Streamlit application
├── vinci_bot.py          # Terminal version (legacy)
├── vinci_products.db     # SQLite database (auto-created)
├── uploads/              # Product images
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── MANUAL.md             # User manual
```

---

## 📋 Requirements

- Python 3.8+
- Streamlit
- Pillow (image processing)
- pywhatkit (WhatsApp automation)

---

## 🖥️ Screenshots

### Dashboard
```
┌──────────┬──────────┬──────────┬──────────────┐
│  Total   │Available │  Sold    │  Inventory   │
│    15    │    12    │    3     │   R45,000    │
└──────────┴──────────┴──────────┴──────────────┘
```

### Add Product
```
┌─────────────────────────────────────┐
│ Product Name: [Samsung Galaxy S21 ] │
│ Category:     [Electronics 📱    ▼] │
│ Condition:    [Like New         ▼] │
│ 💡 Suggested: R4,000               │
│ Price:        [4000              ] │
│ [📸 Upload Images]                  │
│ [➕ Add Product]                    │
└─────────────────────────────────────┘
```

---

## 🔧 WhatsApp Setup

1. Open **web.whatsapp.com** in your browser
2. Scan QR code with your phone
3. Keep it logged in
4. Use the "📱 WhatsApp Automation" menu in the app

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 👨‍💻 Author

**ArtradePro** - *Building tools for entrepreneurs*

---

```
🛒 Happy Selling! 💰
```
