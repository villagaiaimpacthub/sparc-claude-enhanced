# System Architecture - Grocery Planning App

## 1. High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│   (React PWA)   │◄──►│   (Node.js)      │◄──►│   APIs          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                      │                      │
│ • Camera API         │ • RESTful API        │ • Spoonacular
│ • Service Worker     │ • Authentication     │ • Open Food Facts
│ • Local Storage      │ • PostgreSQL         │ • USDA FoodData
│ • PWA Features       │ • JWT Tokens         │ • Barcode Lookup
```

## 2. Frontend Architecture

### 2.1 Component Structure
```
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   └── Modal.tsx
│   ├── meal-planning/
│   │   ├── MealCalendar.tsx
│   │   ├── RecipeSearch.tsx
│   │   └── NutritionDisplay.tsx
│   ├── grocery-list/
│   │   ├── ShoppingList.tsx
│   │   ├── BarcodeScanner.tsx
│   │   └── ItemManager.tsx
│   └── budget/
│       ├── BudgetTracker.tsx
│       ├── SpendingChart.tsx
│       └── PriceHistory.tsx
├── hooks/
│   ├── useCamera.ts
│   ├── useOfflineSync.ts
│   └── useBarcodeScanner.ts
├── services/
│   ├── api.ts
│   ├── offline.ts
│   └── barcode.ts
└── utils/
    ├── nutrition.ts
    ├── currency.ts
    └── date.ts
```

### 2.2 State Management
- React Context for global state
- Local state with useState/useReducer
- IndexedDB for offline data persistence
- Service Worker for background sync

## 3. Backend Architecture

### 3.1 API Structure
```
api/
├── auth/
│   ├── POST /login
│   ├── POST /register
│   └── POST /refresh
├── meals/
│   ├── GET /meals
│   ├── POST /meals
│   ├── PUT /meals/:id
│   └── DELETE /meals/:id
├── recipes/
│   ├── GET /recipes/search
│   ├── GET /recipes/:id
│   └── POST /recipes/import
├── grocery/
│   ├── GET /grocery-lists
│   ├── POST /grocery-lists
│   ├── PUT /grocery-lists/:id
│   └── POST /grocery-lists/generate
├── budget/
│   ├── GET /budget/summary
│   ├── POST /budget/transactions
│   └── GET /budget/analytics
└── products/
    ├── GET /products/barcode/:code
    ├── POST /products
    └── GET /products/search
```

### 3.2 Database Schema
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recipes table
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients JSONB NOT NULL,
    instructions TEXT,
    nutrition_data JSONB,
    prep_time INTEGER,
    cook_time INTEGER,
    servings INTEGER
);

-- Meal plans table
CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    week_start DATE NOT NULL,
    meals JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    nutrition_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Grocery lists table
CREATE TABLE grocery_lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    items JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Budget transactions table
CREATE TABLE budget_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    store VARCHAR(255),
    items JSONB,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 4. Security Architecture

### 4.1 Authentication Flow
```
1. User Login → JWT Token Generation
2. Token Storage → Secure HttpOnly Cookie
3. Request Authentication → JWT Verification
4. Token Refresh → Automatic Renewal
5. Logout → Token Invalidation
```

### 4.2 Data Protection
- HTTPS encryption for all communications
- JWT tokens with short expiration (15 minutes)
- Refresh tokens with longer expiration (7 days)
- Input validation and sanitization
- Rate limiting for API endpoints
- CORS configuration for allowed origins

## 5. Performance Optimization

### 5.1 Frontend Optimizations
- React.lazy() for code splitting
- Service Worker for asset caching
- Image optimization and lazy loading
- Bundle size optimization with Webpack
- Virtual scrolling for large lists

### 5.2 Backend Optimizations
- Database indexing for frequent queries
- API response caching with Redis
- Pagination for large data sets
- Connection pooling for database
- Compression for API responses

## 6. Deployment Architecture

### 6.1 Infrastructure
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Database      │
│   (Vercel)      │    │   (Railway)      │    │ (PostgreSQL)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                      │                      │
│ • Static hosting     │ • Docker container   │ • Managed DB
│ • CDN distribution   │ • Auto-scaling       │ • Automated backups
│ • SSL certificate    │ • Health monitoring  │ • Connection pooling
```

### 6.2 CI/CD Pipeline
- GitHub Actions for automated testing
- Automated deployment on successful builds
- Environment-specific configurations
- Database migration scripts
- Rollback capabilities

---
*Generated for Grocery Planning App SPARC Workflow*
*Date: {datetime.now().isoformat()}*
