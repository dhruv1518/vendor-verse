# 🗄️ VendorVerse — Database Setup Guide (Supabase)

This guide walks you through connecting VendorVerse to the shared **Supabase PostgreSQL** database. Follow these steps **before** running the project for the first time.

---

## ⚡ Quick Summary

If you already know what you're doing:

```bash
# 1. Copy .env template
cp .env.example .env

# 2. Edit .env and paste your Supabase DATABASE_URL (Session Pooler URI)
# 3. Run migrations
python manage.py migrate

# 4. Start the server
python manage.py runserver
```

---

## 📋 Step-by-Step Instructions

### Step 1: Create your `.env` file

```bash
cp .env.example .env
```

> **⚠️ NEVER commit your `.env` file to Git!** It contains your database password. The `.gitignore` already protects this, but double-check before pushing.

---

### Step 2: Get your Supabase Connection String

1. Open the **Supabase Dashboard**: [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select the **VendorVerse** project
3. Click the green **"Connect"** button (top-right, next to the project name)
4. In the popup that appears:
   - Under **Connection Method**, select **"Session pooler"**
   - Under **Type**, make sure **"URI"** is selected
5. You will see a connection string like this:

```
postgresql://postgres.xxxxxx:[YOUR-PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
```

6. **Copy** the entire string

---

### Step 3: Update your `.env` file

Open your `.env` file and replace the placeholder `DATABASE_URL` with the string you copied:

```env
DATABASE_URL=postgresql://postgres.xxxxxx:[YOUR-PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
```

**Replace `[YOUR-PASSWORD]`** with the actual database password.

> 💡 **Don't know the password?** Ask the team lead (Dhruv or Shabbir) for the database password.

> ⚠️ **Special characters in password?** If your password contains characters like `@`, `#`, `/`, or `%`, you must URL-encode them. For example:
> - `@` → `%40`
> - `#` → `%23`
> - `/` → `%2F`
> - `%` → `%25`

---

### Step 4: Run Migrations

```bash
python manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: account, accounts, admin, auth, contenttypes, sessions, sites
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying accounts.0001_initial... OK
  ...
```

---

### Step 5: Start the Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) — you should see the VendorVerse homepage! 🎉

---

## 🔧 Troubleshooting

### ❌ `Connection timed out` Error

**Cause**: Your network doesn't support IPv6, or port 6543 is blocked.

**Fix**: Make sure you are using the **Session Pooler** URL (contains `pooler.supabase.com`), **NOT** the Direct Connection URL (contains `db.xxxxx.supabase.co`).

| ❌ Wrong (Direct — uses IPv6) | ✅ Correct (Pooler — uses IPv4) |
|---|---|
| `postgresql://postgres:pass@db.xxxxx.supabase.co:5432/postgres` | `postgresql://postgres.xxxxx:pass@aws-0-region.pooler.supabase.com:5432/postgres` |

---

### ❌ `SASL authentication failed` Error

**Cause**: Wrong password in your `DATABASE_URL`.

**Fix**: Double-check your password. Make sure special characters are URL-encoded (see Step 3 above).

---

### ❌ `ImproperlyConfigured: Set the DATABASE_URL environment variable`

**Cause**: You haven't created a `.env` file, or it doesn't contain `DATABASE_URL`.

**Fix**: Follow Step 1 and Step 3 above.

---

### ❌ `ModuleNotFoundError: No module named 'django'`

**Cause**: Your virtual environment is not activated, or dependencies are not installed.

**Fix**:
```bash
# Activate venv first
.\venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

---

### ❌ `ModuleNotFoundError: No module named 'psycopg2'`

**Cause**: PostgreSQL driver not installed.

**Fix**:
```bash
pip install -r requirements.txt
```

---

## 📁 File Reference

| File | Purpose |
|---|---|
| `.env` | Your local secrets (DATABASE_URL, etc.) — **never committed** |
| `.env.example` | Template showing which env vars are needed — **committed** |
| `config/settings/base.py` | Reads `DATABASE_URL` from `.env` using `django-environ` |
| `config/settings/development.py` | Dev-specific overrides (DEBUG=True, etc.) |
| `config/settings/test.py` | Test-specific overrides (uses in-memory SQLite for speed) |

---

## 🔒 Security Reminders

- **NEVER** commit your `.env` file
- **NEVER** paste real passwords or Supabase project IDs into code files
- If you accidentally commit a secret, tell the team immediately so the password can be rotated
- The `.gitignore` already blocks `.env` and `.env.*` files (except `.env.example`)
