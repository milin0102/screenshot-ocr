# Screenshot OCR

A FastAPI-based web application that extracts text from screenshots using OCR (Optical Character Recognition) and enhances the results with AI refinement using Groq's API.

## Features

- **Image Upload & Processing**: Accepts image uploads and preprocesses them for optimal OCR results
- **OCR Text Extraction**: Uses Tesseract OCR to extract text from images
- **Key-Value Pair Extraction**: Automatically identifies and extracts key-value pairs from extracted text
- **AI Refinement**: Leverages Groq's AI models to clean and improve extracted key-value pairs
- **Web UI**: Clean, responsive web interface for easy interaction
- **RESTful API**: JSON API endpoints for programmatic access

## Tech Stack

- **Backend**: FastAPI (Python)
- **OCR Engine**: Tesseract (pytesseract)
- **Image Processing**: Pillow (PIL)
- **AI Integration**: Groq API (llama3-8b-8192 model)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templates
- **Environment**: Python with dotenv support

## Prerequisites

- Python 3.7+
- Tesseract OCR installed on your system
- Groq API key (optional, for AI refinement)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd screenshot-ocr
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```
   
   **Windows:**
   Download and install from [Tesseract GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Note**: The GROQ_API_KEY is optional. Without it, the application will still work but won't use AI refinement for key-value pairs.

## Usage

### Running the Application

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```

2. **Access the web interface**
   - Main interface: http://localhost:8000/
   - Debug interface: http://localhost:8000/debug
   - API documentation: http://localhost:8000/docs

### Web Interface

1. Navigate to the main page
2. Upload an image file (supports common image formats)
3. The application will process the image and display:
   - Extracted text
   - Identified key-value pairs
   - AI-refined results (if API key is configured)

### API Usage

#### Extract Text from Image

```bash
curl -X POST "http://localhost:8000/api/extract" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_screenshot.png"
```

**Response Format:**
```json
{
  "text": "Extracted text content...",
  "key_values": [
    {
      "key": "Field Name",
      "value": "Field Value"
    }
  ]
}
```

## API Endpoints

- `GET /` - Main web interface
- `GET /debug` - Debug interface
- `POST /api/extract` - Extract text and key-value pairs from uploaded image

## Image Processing Pipeline

1. **Upload Validation**: Checks file type and content
2. **Image Preprocessing**:
   - Converts to RGB format
   - Applies EXIF orientation correction
   - Converts to grayscale
   - Enhances contrast and sharpness
3. **OCR Processing**: Uses Tesseract for text extraction
4. **Key-Value Extraction**: Regex-based parsing with fallback heuristics
5. **AI Refinement**: Optional Groq API integration for result improvement

## Key-Value Extraction Rules

The application uses intelligent regex patterns to identify key-value pairs:

- **Primary Pattern**: `key: value` or `key - value`
- **Fallback Pattern**: Space-separated pairs for cases without explicit separators
- **Deduplication**: Removes duplicate entries while preserving order
- **Length Limits**: Keys limited to 60 characters, values to 200 characters

## Error Handling

- File type validation
- Empty file detection
- OCR failure handling
- API timeout management
- Graceful fallbacks when AI refinement fails

## Development

### Project Structure

```
screenshot-ocr/
├── main.py              # FastAPI application
├── templates/           # Jinja2 HTML templates
├── static/             # CSS/JS static files
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

### Adding New Features

1. **New API Endpoints**: Add routes in `main.py`
2. **UI Improvements**: Modify templates in `templates/` directory
3. **Styling**: Update CSS files in `static/` directory
4. **OCR Improvements**: Enhance the `preprocess_image_for_ocr()` function

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in your PATH
2. **Poor OCR results**: Try adjusting image preprocessing parameters in `preprocess_image_for_ocr()`
3. **AI refinement fails**: Check your GROQ_API_KEY and internet connection
4. **Large file uploads**: The application handles standard image sizes; very large images may need resizing

### Performance Tips

- Use PNG or JPEG formats for best OCR results
- Ensure images have good contrast and resolution
- Consider image compression for faster processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the repository
- Check the debug interface at `/debug` for troubleshooting information
- Review the API documentation at `/docs`