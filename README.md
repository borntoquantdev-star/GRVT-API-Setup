# 🚀 GRVT API Setup - Complete Guide

## 📋 สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [วิธีติดตั้ง Virtual Environment](#วิธีติดตั้ง-virtual-environment)
3. [การติดตั้ง Dependencies](#การติดตั้ง-dependencies)
4. [การตั้งค่า Jupyter Kernel](#การตั้งค่า-jupyter-kernel)
5. [การตั้งค่า Environment Variables](#การตั้งค่า-environment-variables)
6. [การใช้งาน Notebook](#การใช้งาน-notebook)
7. [ความปลอดภัย](#ความปลอดภัย)
8. [FAQ](#faq)

---

## 🎯 ภาพรวม

โฟลเดอร์นี้ประกอบด้วย:
- `01_api_setup.ipynb` - Jupyter notebook สำหรับ GRVT API setup
- `grvt_helpers.py` - Helper functions สำหรับ GRVT API
- `requirements.txt` - Python dependencies
- `.env.template` - Template สำหรับ environment variables
- `README.md` - เอกสารนี้

---

## 🔧 วิธีติดตั้ง Virtual Environment

### ทำไมต้องใช้ Virtual Environment?

**Virtual Environment (venv)** คือสภาพแวดล้อม Python แยกต่างหากที่:
- ✅ แยก dependencies ของแต่ละโปรเจคออกจากกัน
- ✅ ป้องกัน conflict ระหว่าง package versions
- ✅ ทำให้โปรเจคสามารถ reproduce ได้ง่าย
- ✅ **เพิ่มความปลอดภัย** โดยแยก credentials ออกจาก system Python

---

### Step 1: สร้าง Virtual Environment

เปิด Terminal/PowerShell ใน directory นี้:

```powershell
# Windows PowerShell
python -m venv env

# หรือระบุ Python version
python3.11 -m venv env
```

```bash
# Linux/Mac
python3 -m venv env
```

**ผลลัพธ์:** จะมีโฟลเดอร์ `env/` ถูกสร้างขึ้น

---

### Step 2: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\env\Scripts\Activate.ps1

# ถ้า error "running scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows CMD:**
```cmd
.\env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source env/bin/activate
```

**ตรวจสอบว่า activate สำเร็จ:**
- เห็น `(env)` ข้างหน้า command prompt
- รัน `which python` (Linux/Mac) หรือ `where python` (Windows)
- ต้องชี้ไปที่ `env/Scripts/python` หรือ `env/bin/python`

---

## 📦 การติดตั้ง Dependencies

หลังจาก activate virtual environment แล้ว:

```powershell
# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. ติดตั้ง dependencies ทั้งหมด
pip install -r requirements.txt

# 3. ติดตั้ง ipykernel (สำคัญมาก!)
pip install ipykernel

# 4. ตรวจสอบว่าติดตั้งสำเร็จ
pip list | Select-String "ipykernel"  # PowerShell
pip list | grep ipykernel              # Linux/Mac
```

**หมายเหตุ:** การติดตั้งจาก `requirements.txt` จะใช้เวลา 2-5 นาที เนื่องจากต้อง compile บาง packages

---

## 🪐 การตั้งค่า Jupyter Kernel

### ทำไมต้องใช้ ipykernel?

**`ipykernel`** คือตัวที่เชื่อม Jupyter Notebook กับ Python virtual environment:

```
Jupyter Notebook ←→ ipykernel ←→ Python (env)
```

**ถ้าไม่มี ipykernel:**
- ❌ Jupyter จะใช้ system Python แทน
- ❌ ไม่เห็น packages ที่ติดตั้งใน venv
- ❌ ImportError และ dependency issues

---

### วิธีที่ 1: สร้าง Kernel จาก Virtual Environment (แนะนำ!)

```powershell
# ต้อง activate venv ก่อน!
python -m ipykernel install --user --name=grvt-env --display-name="Python (GRVT Trading)"
```

**พารามิเตอร์:**
- `--user` = ติดตั้งสำหรับ user ปัจจุบันเท่านั้น
- `--name=grvt-env` = ชื่อ kernel (ใช้ internal)
- `--display-name="..."` = ชื่อที่แสดงใน Jupyter

**ผลลัพธ์:**
```
Installed kernelspec grvt-env in C:\Users\<username>\AppData\Roaming\jupyter\kernels\grvt-env
```

---

### วิธีที่ 2: เลือก Interpreter ใน VS Code

ถ้าใช้ Jupyter ใน VS Code:

1. เปิด `01_api_setup.ipynb`
2. กด **"Select Kernel"** มุมขวาบน
3. เลือก **"Python Environments..."**
4. เลือก `.\env\Scripts\python.exe`

**ข้อดี:**
- ✅ ใช้งานง่าย
- ✅ VS Code จัดการ kernel ให้อัตโนมัติ

---

### วิธีที่ 3: ใช้ Jupyter Notebook/Lab แบบ Classic

```powershell
# Activate venv ก่อน
.\env\Scripts\Activate.ps1

# เปิด Jupyter
jupyter notebook

# หรือ Jupyter Lab
jupyter lab
```

**ข้อดี:**
- ✅ Jupyter จะใช้ venv โดยอัตโนมัติ (เพราะ activate แล้ว)

**ข้อเสีย:**
- ❌ ต้อง activate ทุกครั้งก่อนเปิด Jupyter

---

## 🔐 การตั้งค่า Environment Variables

### Step 1: คัดลอก Template

```powershell
copy .env.template .env
```

### Step 2: แก้ไข `.env`

เปิดไฟล์ `.env` และกรอกข้อมูล:

```bash
# GRVT Configuration
GRVT_ENV=testnet  # หรือ prod
GRVT_SUB_ACCOUNT_ID=your_sub_account_id_here

# GRVT API Credentials (สำหรับ API Key Flow)
GRVT_API_KEY=your_api_key_here
GRVT_API_SECRET=your_api_secret_here

# GRVT Private Key (สำหรับ EIP-712 Signing)
GRVT_PRIVATE_KEY=your_private_key_here
```

### Step 3: เช็คว่าโหลดสำเร็จ

ใน notebook:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# ตรวจสอบ
print(f"GRVT_ENV: {os.getenv('GRVT_ENV')}")
print(f"Sub Account ID: {os.getenv('GRVT_SUB_ACCOUNT_ID')[:10]}...")
```

---

## 🎮 การใช้งาน Notebook

### Step 1: เปิด Jupyter

**วิธีที่ 1 - VS Code:**
1. เปิด `01_api_setup.ipynb`
2. เลือก kernel: **"Python (GRVT Trading)"**
3. Run cells

**วิธีที่ 2 - Jupyter Notebook:**
```powershell
.\env\Scripts\Activate.ps1
jupyter notebook
```

### Step 2: Run Cells

1. **Cell 1:** Import และ setup
2. **Cell 2:** Load environment variables
3. **Cell 3:** Connect to GRVT
4. **Cell 4-6:** ทดสอบ API calls

### Step 3: ตรวจสอบการเชื่อมต่อ

ดูที่ output:
- ✅ "Connected to GRVT Testnet"
- ✅ Balance, Positions แสดงผลถูกต้อง
- ❌ Error? → ตรวจสอบ credentials และ network

---

## 🔒 ความปลอดภัย

### การเปรียบเทียบ: System Python vs Virtual Environment

| ลักษณะ | System Python | Virtual Environment (venv) |
|--------|---------------|----------------------------|
| **Package Location** | Global (`C:\Python\Lib\site-packages`) | Local (`./env/Lib/site-packages`) ✅ |
| **Credentials** | อาจรั่วไหลใน global env | แยกตาม project ✅ |
| **Access Control** | ทุก script เห็นทุก package | แค่ที่ activate ✅ |
| **Isolation** | ไม่มี | มี ✅ |
| **Security Risk** | สูง ⚠️ | ต่ำกว่า ✅ |

---

### Virtual Environment ช่วยเรื่องความปลอดภัยยังไง?

#### 1. **Credential Isolation**

**ไม่ใช้ venv:**
```
System Python
  └── .env (accessible by ALL Python scripts on system)
      ├── Trading Bot A
      ├── Random Script B  ← อาจอ่าน .env ได้!
      └── Malicious Script C  ← อันตราย!
```

**ใช้ venv:**
```
Project A/
  └── env/ + .env  ← แค่ scripts ใน Project A เท่านั้น!

Project B/
  └── env/ + .env  ← แยกออกจาก Project A!
```

---

#### 2. **Package Dependency Isolation**

**ปัญหาที่อาจเกิด (ไม่ใช้ venv):**

```python
# Global Python: Package X version 1.0
import package_x

# Trading Bot ต้องการ Package X version 2.0
# → Conflict! → Trading Bot crash!
```

**แก้ไขด้วย venv:**

```
env1/ → Package X version 1.0
env2/ → Package X version 2.0
→ ไม่ conflict!
```

---

#### 3. **Jupyter Kernel + ipykernel ช่วยอะไร?**

**ถ้าไม่ใช้ ipykernel:**

```
Jupyter → System Python
  → ใช้ global packages
  → อาจโหลด .env จาก location อื่น
  → ไม่ปลอดภัย!
```

**ใช้ ipykernel:**

```
Jupyter → ipykernel → env/
  → ใช้แค่ packages ใน env/
  → โหลด .env ใน project directory เท่านั้น
  → ปลอดภัยกว่า! ✅
```

---

### Best Practices สำหรับความปลอดภัย

1. ✅ **ใช้ venv เสมอ** - แยก project ออกจากกัน
2. ✅ **ติดตั้ง ipykernel** - เชื่อม Jupyter กับ venv อย่างถูกต้อง
3. ✅ **ไม่ commit `.env`** - เพิ่มใน `.gitignore`
4. ✅ **ใช้ `.env.template`** - แชร์โครงสร้างโดยไม่แชร์ credentials
5. ✅ **Testnet ก่อน Production** - ทดสอบให้มั่นใจก่อนใช้เงินจริง
6. ✅ **ใช้ Testnet Private Key** - อย่าใช้ private key ที่มีเงินจริง
7. ✅ **chmod 600 .env** (Linux/Mac) - จำกัดสิทธิ์อ่านไฟล์

---

## ❓ FAQ

### Q1: ทำไม `pip install` ใน venv แต่ Jupyter ยังไม่เห็น package?

**A:** Jupyter ใช้ kernel ผิด!

**วิธีแก้:**
1. ติดตั้ง ipykernel: `pip install ipykernel`
2. สร้าง kernel: `python -m ipykernel install --user --name=grvt-env`
3. Restart Jupyter และเลือก kernel ใหม่

---

### Q2: ต่างกันไหมระหว่าง "activate venv + jupyter" vs "ipykernel install"?

**A:** **ใช้ได้ทั้งคู่** แต่มีข้อดีข้อเสียต่างกัน:

| วิธี | ข้อดี | ข้อเสีย |
|------|-------|---------|
| **Activate + Jupyter** | ✅ ตรงไปตรงมา | ❌ ต้อง activate ทุกครั้ง |
| **ipykernel install** | ✅ สะดวก (เลือก kernel ครั้งเดียว) | ❌ ต้อง setup kernel ก่อน |

**คำแนะนำ:** ใช้ **ipykernel install** สำหรับโปรเจคที่ใช้งานบ่อย

---

### Q3: venv ช่วยเรื่องความปลอดภัยจริงหรือ?

**A:** **ช่วย แต่ไม่ใช่ 100%**

**venv ช่วย:**
- ✅ แยก packages ออกจาก global Python
- ✅ ป้องกัน malicious package ที่ติดตั้ง global แอบอ่าน .env
- ✅ จำกัด scope ของ credentials

**venv ไม่ช่วย:**
- ❌ ไม่ encrypt .env (ยังอ่านได้ถ้ามี file access)
- ❌ ไม่ป้องกัน malicious code ใน notebook เอง
- ❌ ไม่ป้องกัน network attacks

**สำหรับความปลอดภัยสูงสุด:**
- ใช้ secrets manager (e.g., AWS Secrets Manager)
- ใช้ hardware wallet สำหรับ private keys
- ใช้ encrypted volumes สำหรับ .env

---

### Q4: ลบ venv ทิ้งแล้วสร้างใหม่ได้ไหม?

**A:** **ได้เลย!**

```powershell
# 1. Deactivate
deactivate

# 2. ลบโฟลเดอร์ env
Remove-Item -Recurse -Force env

# 3. สร้างใหม่
python -m venv env

# 4. Activate และติดตั้ง packages ใหม่
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

venv เป็นแค่ "container" - ลบทิ้งแล้วสร้างใหม่ได้ตลอด!

---

### Q5: จำเป็นต้องใช้ venv ไหมถ้าใช้ Docker?

**A:** **Docker ดีกว่า venv!**

Docker = venv + OS isolation
- ถ้ามี Docker → ไม่จำเป็นต้องใช้ venv
- ถ้าไม่มี Docker → ใช้ venv เป็น minimum requirement

---

## 🚀 Quick Start Summary

```powershell
# 1. สร้าง venv
python -m venv env

# 2. Activate
.\env\Scripts\Activate.ps1

# 3. ติดตั้ง packages
pip install -r requirements.txt
pip install ipykernel

# 4. สร้าง Jupyter kernel
python -m ipykernel install --user --name=grvt-env --display-name="Python (GRVT Trading)"

# 5. คัดลอกและแก้ไข .env
copy .env.template .env
# (แก้ไข .env ด้วย text editor)

# 6. เปิด Jupyter และเลือก kernel "Python (GRVT Trading)"
jupyter notebook
```

---

## 📚 เอกสารเพิ่มเติม

- `CREDENTIALS_GUIDE.md` - วิธีหา GRVT credentials
- `GRVT_API_REFERENCE.md` - GRVT API field names และ structures
- `grvt_helpers.py` - Helper functions พร้อม docstrings

---

## 🆘 ติดปัญหา?

1. เช็ค error message ละเอียด
2. ตรวจสอบว่า:
   - ✅ Virtual environment activated
   - ✅ Jupyter ใช้ kernel ที่ถูกต้อง
   - ✅ `.env` มี credentials ครบ
   - ✅ Network เชื่อมต่อ GRVT ได้
3. ลอง restart kernel และ run ใหม่
4. ถ้ายังไม่ได้ → ลบ venv และสร้างใหม่

---

**Happy Trading! 🚀📈**
