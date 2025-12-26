# 🚀 Startup Scripts Guide

## 📋 Available Scripts

### 1. `start.bat` - Start Services
**Usage**: Double-click to run

**Features**:
- ✅ Checks project directories
- ✅ Starts backend service in new window (port 8000)
- ✅ Starts frontend service in new window (port 5173)
- ✅ Shows service URLs

**How it works**:
- Opens 2 command windows (backend + frontend)
- Each window shows real-time logs
- Close windows to stop services

---

### 2. `stop.bat` - Stop Services
**Usage**: Double-click to run

**Features**:
- 🛑 Finds processes on port 8000 (backend)
- 🛑 Finds processes on port 5173 (frontend)
- 🛑 Force kills all related processes

**When to use**:
- Service windows were closed but processes still running
- Port conflicts
- Quick shutdown needed

---

### 3. `install.bat` - First-time Setup
**Usage**: Double-click to run (before first start)

**Features**:
- ✅ Checks Python environment
- ✅ Installs Poetry (if not installed)
- ✅ Installs all backend dependencies
- ✅ Checks Node.js environment
- ✅ Installs all frontend dependencies
- ✅ Checks database configuration

**What it does**:
1. Verifies Python 3.10+ is installed
2. Verifies/installs Poetry
3. Runs `poetry install` in backend
4. Verifies Node.js 16+ is installed
5. Runs `npm install` in frontend
6. Reminds you to configure database

---

### 4. `start.ps1` - PowerShell Version (Advanced)
**Usage**: Right-click → Run with PowerShell

**Extra features**:
- ✅ Port conflict detection
- ✅ Poetry installation check
- ✅ node_modules verification
- ✅ Colored output
- ✅ Better error messages

---

## 🎯 Quick Start Guide

### First Time Setup (3 steps)

#### Step 1: Install Dependencies
```bash
# Double-click
install.bat
```

#### Step 2: Configure Database
Create `backend/.env` file:
```env
DATABASE_URL=mysql://root:password@localhost:3306/erp_db
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
```

Create database:
```sql
CREATE DATABASE erp_db CHARACTER SET utf8mb4;
```

#### Step 3: Initialize Database
```bash
cd backend
poetry run alembic upgrade head
poetry run python scripts/init_db.py
cd ..
```

### Daily Usage (1 step)

```bash
# Double-click to start
start.bat

# Close windows or run stop.bat to stop
```

---

## 🌐 Service URLs

After starting:

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI service |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:5173 | Vue3 application |

---

## ❓ Troubleshooting

### Problem: "Port already in use"

**Solution**:
```bash
# Run stop script
stop.bat

# Or manually check
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### Problem: "Poetry not found"

**Solution**:
```bash
pip install poetry
```

### Problem: "npm install failed"

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Problem: Database connection error

**Solution**:
1. Check MySQL is running
2. Verify `backend/.env` configuration
3. Create database: `CREATE DATABASE erp_db CHARACTER SET utf8mb4;`
4. Run migrations: `cd backend && poetry run alembic upgrade head`

### Problem: "PowerShell script cannot run"

**Solution**:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned

# Or run with bypass
PowerShell -ExecutionPolicy Bypass -File start.ps1
```

---

## 🛠️ Manual Startup (Alternative)

If scripts don't work:

### Backend
```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## 📝 Notes

- **Windows Only**: These .bat scripts are for Windows
- **Line Endings**: CRLF (Windows style)
- **Encoding**: ASCII to avoid encoding issues
- **Logs**: Check service windows for errors
- **Ports**: Default 8000 (backend) and 5173 (frontend)

---

## 🔒 Default Account

After database initialization:

- Username: `admin`
- Password: `admin123`

**⚠️ Change password in production!**

---

**Print-ERP System v1.0.0**
Made with ❤️ by Claude Code
