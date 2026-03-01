# Government Job Notification System

An automated system that scrapes government job notifications from Telegram channels, performs intelligent eligibility matching, and delivers personalized notifications to users.

## 🎯 Features

- **Automated Scraping**: Monitors Telegram channels for new job notifications every 15 minutes
- **Smart Parsing**: Extracts structured data (title, organization, age limits, education, vacancies, dates)
- **AI-Powered Fallback**: Uses Google Gemini to parse complex notifications when regex fails
- **Eligibility Matching**: Checks user eligibility based on age, education, category, and state
- **Category-Aware Age Relaxation**: Automatic OBC (+3 years), SC/ST (+5 years) relaxation
- **State-Specific Filtering**: Filters state PSC exams by user's state
- **Telegram Delivery**: Sends matched notifications directly to users' Telegram
- **Two User Modes**:
  - **Premium**: Auto-delivery based on eligibility
  - **Free**: Manually select notifications to receive
- **Admin Dashboard**: Manage monitored channels, view statistics
- **Modern Frontend**: React + TypeScript + Tailwind CSS

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram       │
│  Channels       │
└────────┬────────┘
         │
         │ Telethon (every 15 min)
         ▼
┌─────────────────┐      ┌──────────────┐
│  Celery Beat    │─────▶│ Celery Worker│
│  (Scheduler)    │      │  (Tasks)     │
└─────────────────┘      └──────┬───────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│  Parser        │    │  Eligibility    │   │  Telegram Bot   │
│  (Regex+Gemini)│    │  Matcher        │   │  (Delivery)     │
└────────────────┘    └─────────────────┘   └─────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                     ┌─────────────────┐
                     │   Supabase      │
                     │   (PostgreSQL)  │
                     └─────────────────┘
                                ▲
                                │
                     ┌──────────┴──────────┐
                     │                     │
              ┌──────▼──────┐      ┌──────▼──────┐
              │  FastAPI    │      │  React      │
              │  Backend    │◀─────│  Frontend   │
              └─────────────┘      └─────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database + authentication
- **Celery + Redis** - Async task queue and scheduling
- **Telethon** - Telegram MTProto API for scraping
- **Google Gemini** - AI for complex notification parsing

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client

### Infrastructure
- **Railway** - Hosting (backend, workers, Redis)
- **Vercel** - Frontend hosting
- **Docker** - Containerization

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL (or Supabase account)
- Redis
- Telegram account

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Run database migrations
# (Run schema.sql in your Supabase SQL editor)

# Authorize Telethon (one-time)
python -m scraper.auth

# Start API server
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A worker.celery_app worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A worker.celery_app beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with API URL
nano .env

# Start development server
npm run dev
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide covering:
- Supabase database setup
- Railway backend deployment
- Vercel frontend deployment
- Telegram bot configuration
- Environment variables

---

## 📊 Database Schema

```sql
users
  ├── id (UUID, PK)
  ├── email (TEXT, UNIQUE)
  ├── password_hash (TEXT)
  ├── telegram_chat_id (BIGINT)
  ├── is_premium (BOOLEAN)
  ├── role (TEXT) -- 'user' | 'admin'
  └── timestamps

user_profiles
  ├── user_id (UUID, FK)
  ├── dob (DATE)
  ├── gender (TEXT)
  ├── education_level (TEXT)
  ├── category (TEXT) -- General, OBC, SC, ST, EWS
  ├── state (TEXT)
  └── exam_interests (TEXT[])

notifications
  ├── id (SERIAL, PK)
  ├── title (TEXT)
  ├── organization (TEXT)
  ├── exam_type (TEXT) -- Central, State, Banking, etc.
  ├── last_date (DATE)
  ├── min_age / max_age (INTEGER)
  ├── education_required (TEXT)
  ├── total_vacancies (INTEGER)
  ├── source_channel (TEXT)
  └── raw_text (TEXT)

telegram_channels
  ├── id (SERIAL, PK)
  ├── channel_username (TEXT, UNIQUE)
  ├── is_active (BOOLEAN)
  └── last_scraped_id (BIGINT)
```

---

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### User
- `GET /api/users/me` - Get current user
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update eligibility profile
- `PUT /api/users/telegram-chat-id` - Link Telegram account

### Notifications
- `GET /api/notifications` - List notifications (with pagination, filters)
- `GET /api/notifications/{id}` - Get notification details
- `POST /api/notifications/select` - Submit selected notifications (free users)

### Admin
- `GET /api/admin/channels` - List monitored channels
- `POST /api/admin/channels` - Add new channel
- `DELETE /api/admin/channels/{id}` - Remove channel
- `PATCH /api/admin/channels/{id}/toggle` - Toggle active status
- `GET /api/admin/stats` - System statistics

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Run with coverage
pytest --cov=app
```

---

## 📝 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DATABASE_URL=postgresql://...

TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef...
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

GOOGLE_API_KEY=AIza...

REDIS_URL=redis://localhost:6379

APP_ENV=development
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=72
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

---

## 🎨 Features in Detail

### Eligibility Matching Engine

The system performs sophisticated eligibility checks:

1. **Age Verification**
   - Calculates user's age from DOB
   - Applies category-specific relaxation:
     - General/EWS: No relaxation
     - OBC: +3 years
     - SC/ST: +5 years
   - Returns detailed reasons for eligibility status

2. **Education Matching**
   - Hierarchical matching (PhD > Post Grad > Grad > Diploma > 12th > 10th)
   - Users with higher education qualify for lower requirements

3. **State Filtering**
   - Maps state PSC organizations (BPSC → Bihar, UPPSC → UP, etc.)
   - Filters state exams based on user's state

4. **Category Vacancy Check**
   - Checks if vacancies exist for user's category
   - Marks as partial if no category-wise data available

### Smart Parsing

1. **Regex Extraction** (Primary)
   - Title detection from first meaningful line
   - Organization matching against known list (UPSC, SSC, IBPS, etc.)
   - Date parsing (multiple formats)
   - Age limit extraction (multiple patterns)
   - Education level detection
   - Vacancy counting

2. **Gemini AI Fallback** (Secondary)
   - Activates when critical fields (title, org, date) are missing
   - Uses structured JSON prompts
   - Validates and sanitizes AI responses
   - Falls back gracefully on errors

---

## 🔒 Security Features

- JWT-based authentication with bcrypt password hashing
- Row Level Security (RLS) in Supabase
- Input validation using Pydantic
- CORS protection
- Rate limiting (configurable)
- Admin role checking
- SQL injection prevention via ORM

---

## 📈 Roadmap

### Phase 1 ✅ (Current)
- [x] Basic scraping and parsing
- [x] Eligibility matching
- [x] Telegram delivery
- [x] Frontend dashboard
- [x] Admin panel

### Phase 2 🚧 (In Progress)
- [ ] Comprehensive test suite
- [ ] Premium payment integration (Razorpay/Stripe)
- [ ] Email notifications
- [ ] Advanced analytics

### Phase 3 📋 (Planned)
- [ ] Mobile app (React Native)
- [ ] WhatsApp integration
- [ ] PDF text extraction and analysis
- [ ] Previous year cutoff predictions
- [ ] Mock test recommendations
- [ ] Study material aggregation

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

Built with ❤️ for students preparing for government exams.

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Email: support@example.com (update this)

---

## 🙏 Acknowledgments

- OpenAI for inspiration
- Telegram for the amazing API
- All the government job aspirants this project aims to help
