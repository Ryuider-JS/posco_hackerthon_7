# Q-ProcureAssistant

AI-powered procurement management system for POSCO Hackathon.

## Features

- 📸 **AI Product Registration** - Upload product images for automatic analysis and registration
- 🔍 **Smart Search** - Search products by image or text specifications
- 🤖 **Intelligent Matching** - AI-based similarity detection to prevent duplicate registrations
- 📦 **Q-CODE System** - Automatic Q-CODE generation for product tracking
- 📹 **Real-time Inventory** - Webcam-based inventory monitoring (in progress)

## Quick Start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: http://localhost:5173

## Project Structure

```
posco_hackerthon/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── database.py  # Database configuration
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routes/      # API endpoints
│   │   └── services/    # AI services (OpenAI integration)
│   ├── uploads/         # Uploaded product images
│   ├── requirements.txt
│   └── .env            # API keys
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/ # Reusable components
│   │   └── pages/      # Page components
│   └── package.json
└── CLAUDE.md           # Developer guide for Claude Code
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, OpenAI API, Python 3.14
- **Frontend**: React 19, Vite 7, TailwindCSS 4, React Router v7
- **Database**: SQLite
- **AI**: OpenAI GPT-4 Vision for image analysis

## Key Workflows

### 1. Product Registration with Image

1. User uploads product image
2. AI analyzes image and extracts product information
3. System searches for similar existing products
4. If similarity >= 95%: Suggest existing product
5. If similarity 70-94%: Show similar products with differences
6. If similarity < 70%: Register as new product with auto-generated Q-CODE

### 2. Product Search by Specifications

1. User enters text specifications (e.g., "직경 10mm, 재질 스테인리스")
2. AI parses and structures the specifications
3. System finds matching products
4. Returns sorted list by similarity score

## API Endpoints

### Product Analysis

**POST /api/analyze-image**
- Upload image (with optional specs text)
- Returns AI analysis and similar products

**POST /api/products/search-by-specs**
- Search using text specifications only
- Returns matching products with similarity scores

### Product Management

**POST /api/products** - Register new product
**GET /api/products** - List all products (supports filtering/search)
**GET /api/products/{qcode}** - Get product by Q-CODE
**PUT /api/products/{qcode}** - Update product
**DELETE /api/products/{qcode}** - Delete product

## Similarity Scoring

The system calculates similarity between products using weighted criteria:

- **Name similarity**: 30%
- **Material match**: 25%
- **Category match**: 20%
- **Dimensions match**: 15%
- **Description similarity**: 10%

**Thresholds:**
- >= 95%: Exact match (green badge)
- 70-94%: Similar match (yellow badge)
- < 70%: Different product (gray badge)

## Testing

### Using API Docs

Visit http://localhost:8000/docs for interactive Swagger UI.

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List products
curl http://localhost:8000/api/products

# Search by specs
curl -X POST "http://localhost:8000/api/products/search-by-specs" \
  -F "specs_text=육각볼트 M10 스테인리스"
```

## Troubleshooting

**Backend won't start**
- Check Python 3.9+: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Verify `.env` file exists with API keys

**Frontend won't start**
- Check Node 18+: `node --version`
- Reinstall: `rm -rf node_modules && npm install`

**CORS errors**
- Ensure backend runs on port 8000
- Check CORS settings in `backend/app/main.py`

## License

MIT - Hackathon Project