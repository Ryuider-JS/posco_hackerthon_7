# Q-ProcureAssistant Backend API

FastAPI backend for AI-powered procurement management system.

## Features

- 📸 **Image-based Product Analysis** - Upload product images for AI analysis (OpenAI Vision)
- 👁️ **Visual Similarity Matching** - Compare product images using Google Gemini Vision
- 🔍 **Spec-based Search** - Search products using text specifications
- 🤖 **Hybrid AI Matching** - Combines visual (60%) + text (40%) similarity for accurate matching
- 📦 **Q-CODE Management** - Automatic Q-CODE generation and product registration
- 💾 **SQLite Database** - Lightweight database for product storage

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./qcode.db
```

The API keys are already provided in the repository `.env` file for hackathon use.

### 3. Run the Server

```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
# From backend directory
python app/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Product Analysis

#### `POST /api/analyze-image`
Analyze uploaded product image and find similar products

**Request:**
- `file` (File): Product image
- `specs` (Optional String): Additional text specifications

**Response:**
```json
{
  "success": true,
  "image_path": "uploads/product_20240106_123456.jpg",
  "ai_analysis": "AI analysis text...",
  "extracted_data": {
    "name": "스테인리스 육각볼트 M10x50",
    "category": "체결부품",
    "material": "스테인리스",
    "dimensions": "M10x50",
    "description": "...",
    "keywords": ["볼트", "육각", "스테인리스"]
  },
  "similar_products": [
    {
      "id": 1,
      "qcode": "Q-2401-1234",
      "name": "스테인리스 볼트",
      "similarity": 95.5,
      "purchase_count": 23,
      "average_rating": 4.8,
      "last_price": 1200
    }
  ]
}
```

#### `POST /api/products/search-by-specs`
Search products using text specifications only

**Request:**
- `specs_text` (String): Text description (e.g., "직경 10mm, 길이 50mm, 재질 스테인리스")

**Response:**
```json
{
  "success": true,
  "analyzed_specs": { /* extracted data */ },
  "ai_analysis": "AI analysis text...",
  "similar_products": [ /* list of matches */ ]
}
```

### Product Management

#### `POST /api/products`
Register a new product

**Request (Form Data):**
- `name` (required): Product name
- `category`: Category (default: "미분류")
- `description`: Product description
- `image_path`: Path to uploaded image
- `diameter`: Diameter specification
- `length`: Length specification
- `material`: Material type
- `specs`: Additional specifications
- `last_price`: Last purchase price

**Response:**
```json
{
  "id": 1,
  "qcode": "Q-2401-5678",
  "name": "스테인리스 육각볼트 M10x50",
  "category": "체결부품",
  ...
}
```

#### `GET /api/products`
List all products with optional filtering

**Query Parameters:**
- `skip` (default: 0): Pagination offset
- `limit` (default: 100): Max results
- `category`: Filter by category
- `search`: Search term (name, description, qcode, material)

**Response:**
```json
{
  "total": 42,
  "products": [ /* list of products */ ]
}
```

#### `GET /api/products/{qcode}`
Get specific product by Q-CODE

#### `PUT /api/products/{qcode}`
Update an existing product

#### `DELETE /api/products/{qcode}`
Delete a product

## Database Schema

### Product Model

```python
{
  "id": Integer (Primary Key),
  "qcode": String (Unique, Auto-generated),
  "name": String (Required),
  "category": String (Default: "미분류"),
  "description": Text,
  "image_path": String,

  # Specifications
  "diameter": String,
  "length": String,
  "material": String,
  "specs": Text,

  # Purchase History
  "purchase_count": Integer (Default: 0),
  "average_rating": Float (Default: 0.0),
  "last_price": Float (Default: 0.0),

  # Timestamps
  "created_at": DateTime,
  "updated_at": DateTime
}
```

## AI Services

### OpenAI Services (`ai_service.py`)

**`analyze_product_image(image_path)`**
- Uses OpenAI GPT-4o-mini Vision to analyze product images
- Extracts: name, category, material, dimensions, description, keywords

**`analyze_with_specs(specs_text)`**
- Uses OpenAI GPT-4o-mini to parse text specifications
- Extracts structured data from free-form text

**`calculate_similarity(product1, product2)`**
- Calculates text-based similarity score (0-100) between two products
- Weights:
  - Name: 30%
  - Material: 25%
  - Category: 20%
  - Dimensions: 15%
  - Description: 10%

### Gemini Services (`gemini_service.py`)

**`analyze_product_image_gemini(image_path)`**
- Uses Google Gemini 1.5 Flash for image analysis
- Alternative to OpenAI Vision with similar output format

**`compare_images_similarity_gemini(image1_path, image2_path)`**
- **Visual similarity comparison between two product images**
- Evaluates: visual appearance, color, shape, size, material
- Returns similarity score (0-100) with detailed breakdown

**`calculate_similarity_with_gemini(analysis, products, image_path)`**
- **Hybrid similarity calculation (NEW!)**
- Combines visual similarity (60%) + text similarity (40%)
- More accurate than text-only matching
- Returns sorted list with both visual and text similarity scores

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py       # Product SQLAlchemy model
│   ├── routes/
│   │   ├── __init__.py
│   │   └── products.py      # Product API endpoints
│   └── services/
│       ├── __init__.py
│       └── ai_service.py    # OpenAI integration
├── uploads/                 # Uploaded images
├── requirements.txt
├── .env                     # Environment variables
└── README.md
```

## Testing

### Using curl

```bash
# Analyze image
curl -X POST "http://localhost:8000/api/analyze-image" \
  -F "file=@product.jpg" \
  -F "specs=직경 10mm, 재질 스테인리스"

# Register product
curl -X POST "http://localhost:8000/api/products" \
  -F "name=스테인리스 볼트" \
  -F "category=체결부품" \
  -F "material=스테인리스"

# List products
curl "http://localhost:8000/api/products"

# Search by specs
curl -X POST "http://localhost:8000/api/products/search-by-specs" \
  -F "specs_text=육각볼트 M10"
```

### Using API Docs

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database

The SQLite database (`qcode.db`) is automatically created on first run. To reset:

```bash
rm qcode.db
# Restart server to recreate
```

## Troubleshooting

**ImportError: No module named 'app'**
- Make sure you're running from the `backend` directory
- Use `python -m uvicorn app.main:app` instead of `uvicorn app.main:app`

**OpenAI API Error**
- Check that `OPENAI_API_KEY` is set in `.env`
- Verify the API key is valid and has credits

**CORS Error from Frontend**
- Ensure frontend URL is in `allow_origins` list in [app/main.py](app/main.py:20)
- Default: `http://localhost:5173` (Vite) and `http://localhost:3000` (React)

## License

MIT License - Hackathon Project
