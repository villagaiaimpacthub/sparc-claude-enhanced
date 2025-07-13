# SPARC CLI Examples

This guide provides practical examples of using SPARC CLI for various development tasks.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Web Development](#web-development)
3. [API Development](#api-development)
4. [Database Projects](#database-projects)
5. [Frontend Applications](#frontend-applications)
6. [Full-Stack Projects](#full-stack-projects)
7. [DevOps and Deployment](#devops-and-deployment)
8. [Integration Examples](#integration-examples)

## Basic Examples

### Hello World Application

**Goal:** Create a simple command-line application

```bash
mkdir hello-world
cd hello-world
sparc init
```

In Claude Code:
```
/sparc "Create a simple Python command-line application that greets users and asks for their favorite programming language"
```

**What SPARC will do:**
1. **Specification:** Define CLI requirements and user interaction flow
2. **Architecture:** Design simple script structure
3. **Implementation:** Create Python script with input/output handling
4. **Testing:** Generate unit tests and user acceptance tests
5. **Documentation:** Create README and usage instructions

### Calculator Application

**Goal:** Build a mathematical calculator

```
/sparc "Build a calculator application with basic arithmetic operations (add, subtract, multiply, divide) and a simple GUI interface"
```

**Expected Output:**
- Python application with tkinter GUI
- Error handling for division by zero
- Clear and reset functionality
- Unit tests for all operations
- User documentation

## Web Development

### Personal Blog

**Goal:** Create a personal blog with admin features

```
/sparc "Create a personal blog website with:
- Homepage showing recent posts
- Individual post pages with comments
- Admin area for creating and editing posts
- User authentication for admin
- Responsive design
- SQLite database
- Flask or FastAPI backend"
```

**SPARC Process:**
1. **Specification Phase:**
   - Define user stories (reader, admin)
   - Specify database schema
   - Plan URL structure and navigation

2. **Architecture Phase:**
   - Choose Flask framework
   - Design MVC structure
   - Plan authentication system

3. **Implementation:**
   - Backend API endpoints
   - Database models and migrations
   - Frontend templates
   - CSS styling and responsiveness

### E-commerce Store

**Goal:** Build a simple online store

```
/sparc "Build an e-commerce website for selling books with:
- Product catalog with search and filtering
- Shopping cart functionality
- User registration and login
- Order management system
- Payment integration (Stripe simulation)
- Admin panel for inventory management
- PostgreSQL database
- React frontend with Node.js backend"
```

## API Development

### REST API for Task Management

**Goal:** Create a comprehensive task management API

```
/sparc "Create a REST API for task management with:
- User authentication using JWT tokens
- CRUD operations for tasks and projects
- Task assignment to users
- Due date tracking and notifications
- Priority levels and status updates
- API documentation with OpenAPI/Swagger
- PostgreSQL database with proper indexing
- Express.js backend with TypeScript"
```

**Features SPARC will implement:**
- User registration/login endpoints
- Project and task CRUD operations
- Authentication middleware
- Database schema and relationships
- API documentation
- Error handling and validation
- Unit and integration tests

### GraphQL API

**Goal:** Build a GraphQL API for a library system

```
/sparc "Create a GraphQL API for a library management system with:
- Books, authors, and user entities
- Query operations for searching books
- Mutation operations for borrowing/returning
- Real-time subscriptions for book availability
- Apollo Server with TypeScript
- MongoDB database
- Authentication and authorization"
```

## Database Projects

### Data Analytics Dashboard

**Goal:** Create a dashboard for data visualization

```
/sparc "Build a data analytics dashboard that:
- Connects to a PostgreSQL database with sample sales data
- Displays interactive charts and graphs
- Allows filtering by date range and categories
- Shows key performance indicators (KPIs)
- Exports reports to PDF and CSV
- Uses Python Flask backend with Chart.js frontend
- Includes data refresh functionality"
```

### Database Migration Tool

**Goal:** Create a tool for database schema migrations

```
/sparc "Build a database migration tool that:
- Supports PostgreSQL and MySQL
- Tracks migration history
- Allows rollback functionality
- Validates schema changes
- Generates migration scripts from schema differences
- Command-line interface
- Configuration file support
- Backup functionality before migrations"
```

## Frontend Applications

### React Todo Application

**Goal:** Modern todo application with advanced features

```
/sparc "Create a React todo application with:
- Add, edit, delete, and mark tasks complete
- Categories and tags for organization
- Search and filter functionality
- Local storage persistence
- Dark/light theme toggle
- Drag and drop reordering
- TypeScript for type safety
- Styled-components for styling
- Jest and React Testing Library for tests"
```

### Vue.js Weather App

**Goal:** Weather application with location services

```
/sparc "Build a Vue.js weather application that:
- Shows current weather for user's location
- 7-day weather forecast
- Search for weather in different cities
- Weather maps and radar
- Favorite locations storage
- Responsive design for mobile and desktop
- Integration with OpenWeatherMap API
- Progressive Web App (PWA) features"
```

## Full-Stack Projects

### Social Media Platform

**Goal:** Mini social media platform

```
/sparc "Create a social media platform with:
- User profiles with photos and bio
- Post creation with text and images
- Like and comment functionality
- Follow/unfollow users
- News feed with posts from followed users
- Real-time notifications
- Image upload and storage
- React frontend with Node.js/Express backend
- Socket.io for real-time features
- MongoDB database
- JWT authentication"
```

### Learning Management System

**Goal:** Platform for online courses

```
/sparc "Build a learning management system with:
- Course creation and management
- Video lessons with progress tracking
- Quizzes and assignments
- Student enrollment and grades
- Discussion forums for each course
- Certificate generation upon completion
- Payment integration for course purchases
- Admin dashboard for analytics
- Next.js frontend with Prisma and PostgreSQL
- Video streaming with progress tracking"
```

## DevOps and Deployment

### CI/CD Pipeline Setup

**Goal:** Automated deployment pipeline

```
/sparc "Create a CI/CD pipeline setup that:
- Automatically tests code on push to GitHub
- Builds Docker containers
- Deploys to staging and production environments
- Includes database migrations
- Monitors application health
- Sends notifications on deployment status
- Uses GitHub Actions or GitLab CI
- Deploys to AWS or DigitalOcean
- Includes rollback functionality"
```

### Monitoring Dashboard

**Goal:** Application and infrastructure monitoring

```
/sparc "Build a monitoring dashboard that:
- Tracks application performance metrics
- Monitors server health and resources
- Displays real-time logs and alerts
- Creates custom dashboards for different teams
- Integrates with popular monitoring tools
- Sends notifications via email and Slack
- Historical data analysis and reporting
- Grafana-style interface
- Support for multiple data sources"
```

## Integration Examples

### Slack Bot

**Goal:** Intelligent Slack bot with various features

```
/sparc "Create a Slack bot that:
- Responds to natural language commands
- Integrates with Google Calendar for meeting scheduling
- Provides weather updates and news summaries
- Manages team standup meetings
- Tracks and reports on team productivity metrics
- Integrates with Jira for ticket management
- Uses OpenAI API for intelligent responses
- Stores user preferences in database
- Deployable to Heroku or AWS Lambda"
```

### Email Marketing Platform

**Goal:** Complete email marketing solution

```
/sparc "Build an email marketing platform with:
- Contact list management and segmentation
- Email template editor with drag-and-drop
- Campaign scheduling and automation
- Analytics and reporting on open rates, clicks
- A/B testing functionality
- Integration with popular CRM systems
- GDPR compliance features
- Webhook support for third-party integrations
- React frontend with FastAPI backend
- Celery for background task processing"
```

## Working with Examples

### How to Use These Examples

1. **Copy the exact prompt** into Claude Code after running `/sparc`
2. **Let SPARC complete each phase** before providing additional input
3. **Review outputs** at each phase and provide feedback
4. **Ask questions** if anything is unclear
5. **Test the final application** thoroughly

### Customizing Examples

You can modify any example by adding specific requirements:

```
/sparc "Create a personal blog website with:
- Homepage showing recent posts
- Individual post pages with comments
- Admin area for creating and editing posts
- User authentication for admin
- Responsive design
- SQLite database
- Flask backend

Additional requirements:
- Support for multiple authors
- Category-based post organization
- RSS feed generation
- SEO optimization
- Social media sharing buttons"
```

### Progressive Enhancement

Start simple and add features:

```
# Start with basic version
/sparc "Create a simple todo list application with add, edit, delete functionality"

# After completion, enhance it
/sparc "Enhance the todo application by adding user authentication and cloud synchronization"

# Continue enhancing
/sparc "Add collaboration features allowing users to share todo lists with others"
```

## Best Practices for Examples

### Writing Good Prompts

**Good Example:**
```
/sparc "Create a REST API for a library management system with:
- Book catalog with CRUD operations
- User authentication using JWT
- Book borrowing and return functionality
- Search books by title, author, or ISBN
- PostgreSQL database
- Express.js with TypeScript
- Comprehensive API documentation
- Unit and integration tests"
```

**Why it's good:**
- Specific technologies mentioned
- Clear feature requirements
- Database choice specified
- Testing requirements included
- Documentation requested

### Providing Context

Include relevant context about your project:

```
/sparc "I'm building a fitness tracking application for my gym. Create a React Native mobile app that:
- Tracks workouts and exercises
- Records weights, reps, and sets
- Shows progress over time with charts
- Includes a timer for rest periods
- Syncs data with a cloud backend
- Works offline with data synchronization
- Uses Firebase for backend services"
```

### Iterative Development

Break large projects into phases:

```
# Phase 1: Core functionality
/sparc "Create the basic user authentication and profile management for my social media app"

# Phase 2: Main features
/sparc "Add post creation, viewing, and basic interaction features"

# Phase 3: Advanced features
/sparc "Implement real-time chat and notification systems"
```

## Common Patterns

### Database-Driven Applications

Most applications follow this pattern:
1. Database schema design
2. Backend API development
3. Frontend interface creation
4. Authentication implementation
5. Testing and deployment

### Real-time Applications

For apps requiring real-time features:
1. WebSocket or Socket.io integration
2. Event-driven architecture
3. Real-time data synchronization
4. Optimistic updates in frontend

### Microservices Architecture

For complex applications:
1. Service decomposition
2. API gateway setup
3. Inter-service communication
4. Database per service
5. Container orchestration

---

## Next Steps

After trying these examples:

1. **Experiment** with different technologies and frameworks
2. **Combine features** from multiple examples
3. **Scale up** successful projects
4. **Deploy** applications to cloud platforms
5. **Share** your creations with the community

**Remember:** SPARC learns from your feedback. The more specific and detailed your requirements, the better the results will be.

Happy coding with SPARC! 🚀