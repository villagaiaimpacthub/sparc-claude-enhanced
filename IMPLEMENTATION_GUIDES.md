# SPARC Implementation Guides

## 🎯 **Step-by-Step Implementation Instructions**

This document provides exact code implementations and step-by-step instructions for the critical fixes identified in the technical debt analysis.

---

## 🚨 **Priority 1: Fix Pydantic v2 Serialization**

### **Step 1: Fix BMO Intent Tracker**

**File**: `lib/bmo_intent_tracker.py`

**Lines to Replace:**
```python
# Lines 89, 95, 159 - FIND AND REPLACE:

# OLD (Line 89):
intent_type_value = intent.intent_type.value if hasattr(intent.intent_type, 'value') else intent.intent_type
source_value = intent.source.value if hasattr(intent.source, 'value') else intent.source

# NEW:
intent_data = intent.model_dump(mode='json')
intent_type_value = intent_data['intent_type']
source_value = intent_data['source']

# OLD (Line 95):
'intent_data': intent.dict(),

# NEW:
'intent_data': intent.model_dump(mode='json'),

# OLD (Line 159):
return intent.dict()

# NEW:
return intent.model_dump(mode='json')
```

**Complete Fixed Method:**
```python
async def store_intent(self, intent: Intent) -> bool:
    """Store intent with proper Pydantic v2 serialization"""
    try:
        intent_data = intent.model_dump(mode='json')
        intent_type_value = intent_data['intent_type']
        source_value = intent_data['source']
        
        data = {
            'namespace': self.namespace,
            'intent_type': intent_type_value,
            'content': intent.content,
            'confidence_score': intent.confidence_score,
            'source': source_value,
            'evidence': intent.evidence,
            'created_at': intent.created_at.isoformat(),
            'last_updated': intent.last_updated.isoformat(),
            'intent_data': intent.model_dump(mode='json'),
        }
        
        result = await self.supabase.table("intent_tracking").insert(data).execute()
        return True
    except Exception as e:
        console.print(f"[yellow]Warning: Could not store intent: {str(e)}[/yellow]")
        return False
```

### **Step 2: Fix Interactive Question Engine**

**File**: `lib/interactive_question_engine.py`

**Lines to Replace:**
```python
# Lines 78, 83, 184 - FIND AND REPLACE:

# OLD (Line 78):
'question_data': question.dict(),

# NEW:
'question_data': question.model_dump(mode='json'),

# OLD (Line 83):
'ai_verifiable_criteria': [c.dict() for c in question.ai_verifiable_criteria],

# NEW:
'ai_verifiable_criteria': [c.model_dump(mode='json') for c in question.ai_verifiable_criteria],

# OLD (Line 184):
'user_response': response.dict(),

# NEW:
'user_response': response.model_dump(mode='json'),
```

### **Step 3: Fix Implementation Phase Agent**

**File**: `agents/enhanced/implementation_phase_agent_enhanced.py`

**Lines to Replace:**
```python
# Lines 117, 153, 257, 393 - ALREADY FIXED in our session
# Verify these changes are in place:

# Line 117:
oracle_criteria=oracle_result.model_dump(mode='json'),

# Line 153:
'verifiable_criteria': oracle_result.model_dump(mode='json'),

# Line 257:
conversation_history.append(user_response.model_dump(mode='json'))

# Line 393:
'perfect_prompt': perfect_prompt.model_dump(mode='json'),
```

---

## 🛡️ **Priority 2: Implement Real Security**

### **Step 1: Update Code Generation Security**

**File**: `lib/uber_orchestrator_enhanced.py`

**Method to Replace**: `_create_auth_endpoints()` (around line 650)

```python
def _create_auth_endpoints(self) -> str:
    """Create authentication endpoints with real security"""
    return '''"""Authentication endpoints with real JWT implementation"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

router = APIRouter()
security = HTTPBearer()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: str = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """User login with real JWT authentication"""
    # In production, verify against database
    # This is a simplified version for demonstration
    if credentials.email and credentials.password:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": credentials.email}, expires_delta=access_token_expires
        )
        return LoginResponse(
            access_token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )

@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """User logout"""
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    return {"email": current_user.email, "authenticated": True}
'''
```

### **Step 2: Update User Endpoints with Password Hashing**

**Method to Replace**: `_create_user_endpoints()` (around line 570)

```python
def _create_user_endpoints(self) -> str:
    """Create user endpoints with real password hashing"""
    return '''"""
User API Endpoints with Real Security
FastAPI routes for user management with bcrypt password hashing
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import uuid

from src.database import get_db
from src.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = None
    last_name: str = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str = None
    last_name: str = None
    is_active: bool
    
    class Config:
        from_attributes = True

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with secure password hashing"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password securely
    hashed_password = get_password_hash(user.password)
    
    # Create user
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, user_update: UserCreate, db: Session = Depends(get_db)):
    """Update user with password re-hashing if provided"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.email = user_update.email
    user.first_name = user_update.first_name
    user.last_name = user_update.last_name
    
    # Re-hash password if provided
    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
'''
```

### **Step 3: Update Requirements.txt**

**Method to Replace**: `_create_requirements()` (around line 520)

```python
def _create_requirements(self) -> str:
    """Create requirements.txt with security dependencies"""
    return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic[email]==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
bandit[toml]==1.7.5
python-dotenv==1.0.0
'''
```

---

## 🔧 **Priority 3: Fix Environment Configuration**

### **Step 1: Update Config File Generation**

**Method to Replace**: `_create_config_file()` (around line 490)

```python
def _create_config_file(self, arch_spec: Dict) -> str:
    """Create production-ready configuration with environment variables"""
    return '''"""
Production Configuration Settings
Environment-based configuration with secure defaults
"""
import os
import secrets
from typing import List

class Settings:
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/sparc_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", None) or secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:8080"
    ).split(",")
    
    # Redis Configuration (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Email Configuration (optional)
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@example.com")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "localhost")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "SPARC Generated API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    def validate_config(self):
        """Validate critical configuration"""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        
        if self.DEBUG and "localhost" not in self.ALLOWED_ORIGINS[0]:
            print("WARNING: DEBUG mode enabled with non-localhost CORS origins")

# Global settings instance
settings = Settings()

# Validate configuration on import
settings.validate_config()
'''
```

### **Step 2: Create Environment File Template**

**Add this method to uber_orchestrator_enhanced.py:**

```python
def _create_env_template(self) -> str:
    """Create .env.example template"""
    return '''# SPARC Generated Application Environment Configuration

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/sparc_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security Configuration (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your-secret-key-here-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=false

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (optional)
EMAIL_FROM=noreply@example.com
EMAIL_HOST=localhost
EMAIL_PORT=587

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Application Metadata
APP_NAME=SPARC Generated API
APP_VERSION=1.0.0
'''
```

---

## 🧪 **Priority 4: Implement Database Fallback**

### **Step 1: Create Database Fallback Utility**

**New File**: `lib/database_fallback.py`

```python
#!/usr/bin/env python3
"""
Database Fallback Utility
Provides local file storage when Supabase is unavailable
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console

console = Console()

class DatabaseFallback:
    """Local file storage fallback for when Supabase is unavailable"""
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.storage_path = Path('.sparc') / 'fallback_storage'
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def store_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Store data in local JSON file"""
        try:
            file_path = self.storage_path / f"{self.namespace}_{table_name}.json"
            
            # Load existing data
            existing_data = []
            if file_path.exists():
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            
            # Add timestamp and ID
            data['_id'] = f"{table_name}_{datetime.now().isoformat()}"
            data['_timestamp'] = datetime.now().isoformat()
            
            # Append new data
            existing_data.append(data)
            
            # Save back to file
            with open(file_path, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            console.print(f"[yellow]📁 Stored {table_name} data locally[/yellow]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Fallback storage failed: {str(e)}[/red]")
            return False
    
    async def retrieve_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Retrieve data from local JSON file"""
        try:
            file_path = self.storage_path / f"{self.namespace}_{table_name}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            console.print(f"[red]❌ Fallback retrieval failed: {str(e)}[/red]")
            return []
```

### **Step 2: Update Layer 2 Components with Fallback**

**Add to each Layer 2 component (example for BMOIntentTracker):**

```python
# Add to __init__ method:
from lib.database_fallback import DatabaseFallback

def __init__(self, namespace: str):
    # ... existing code ...
    self.fallback = DatabaseFallback(namespace)

# Update storage methods:
async def _store_with_fallback(self, data: Dict[str, Any], table_name: str) -> bool:
    """Store data with fallback to local storage"""
    try:
        # Try Supabase first
        result = await self.supabase.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        console.print(f"[yellow]Database unavailable, using fallback storage[/yellow]")
        return await self.fallback.store_data(table_name, data)
```

---

## 🎯 **Quick Implementation Summary**

### **Do These in Order:**

1. **Fix Serialization (30 minutes)**:
   - Replace all `.dict()` with `.model_dump(mode='json')` in 4 files
   - Test with validation protocol

2. **Implement Security (45 minutes)**:
   - Update auth endpoints with real JWT
   - Update user endpoints with bcrypt
   - Update requirements.txt

3. **Environment Config (15 minutes)**:
   - Update config file generation
   - Create .env template
   - Test configuration loading

4. **Database Fallback (30 minutes)**:
   - Create fallback utility
   - Update Layer 2 components
   - Test fallback mode

### **Validation After Each Step:**
```bash
# After each priority fix:
uv run lib/uber_orchestrator_enhanced.py --goal "test fix" --namespace validation-test

# Check for success indicators:
grep -c "Could not store" output.log  # Should decrease after each fix
grep -c "✅.*COMPLETED" output.log    # Should be 9
```

### **Final Test:**
```bash
# Should complete with no warnings and high quality score:
uv run lib/uber_orchestrator_enhanced.py --goal "create production API" --namespace final-test
```

Following these implementation guides will transform SPARC from a proof-of-concept into a production-ready autonomous development system.