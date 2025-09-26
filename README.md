# 📺 Streaming Data Analytics Dashboard

A comprehensive streaming analytics platform built with Python, featuring real-time data visualization, semantic layer metrics, and an interactive web dashboard.

## 🌟 Features

### 📊 Interactive Dashboard
- **Real-time Data Visualization**: Line charts showing daily completion rates and total watched hours
- **Advanced Filtering**: Search and filter by show type, genre, state, and rating
- **Sortable Data Table**: Click column headers to sort by any field
- **Collapsible Interface**: Toggle table visibility for better UX
- **Responsive Design**: Modern, mobile-friendly interface

### 📈 Analytics Metrics
Built using the [Boring Semantic Layer](https://github.com/boring-ml/boring-semantic-layer), the platform provides:

1. **Watch Completion Rate by Content Type**: Analyze how different content types perform
2. **User Engagement Score by Geographic Region**: Regional viewing patterns and engagement
3. **Content Performance Index by Genre**: Multi-factor performance scoring
4. **Peak Viewing Time Analysis**: Identify optimal viewing hours
5. **Daily Completion Rate Trends**: Track completion rates over time

### 🚀 Tech Stack
- **Backend**: FastAPI for REST API endpoints
- **Frontend**: Air framework for reactive web UI
- **Data Processing**: Pandas + Ibis with DuckDB backend
- **Analytics**: Boring Semantic Layer for metric definitions
- **Visualization**: Chart.js for interactive charts

## 📁 Project Structure

```
air-python/
├── main.py                 # Main Air/FastAPI application
├── streaming_metrics.py    # Semantic layer metrics definitions
├── test_metrics.py        # Test suite for metrics
├── data/
│   └── streaming-data.json # Sample streaming data
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.13 or higher
- uv (recommended) or pip

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd air-python
   ```

2. **Install dependencies**
   
   Using uv (recommended):
   ```bash
   uv sync
   ```
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Using uv
   uv run python main.py
   
   # Using python directly
   python main.py
   ```

4. **Access the dashboard**
   - Web Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Raw API: http://localhost:8000/api

## 🎯 Usage

### Web Dashboard
The main dashboard provides:
- **Charts Section**: Visual trends and patterns
- **Filters**: Real-time data filtering capabilities
- **Data Table**: Detailed view of all streaming sessions

### Programmatic Access

#### Running Metrics Analysis
```python
from streaming_metrics import StreamingMetrics, load_streaming_data, create_ibis_table

# Load and prepare data
df = load_streaming_data()
table = create_ibis_table(df)
metrics = StreamingMetrics(table)

# Get completion rates by content type
completion_data = metrics.get_completion_rate_by_content_type().execute()
print(completion_data)

# Get engagement by region
engagement_data = metrics.get_engagement_by_region().execute()
print(engagement_data)
```

#### API Endpoints
- `GET /api/` - API information
- `GET /api/data` - Raw streaming data

### Testing
Run the test suite:
```bash
# Using uv
uv run python -m pytest test_metrics.py -v

# Using python
python -m pytest test_metrics.py -v
```

## 📊 Data Schema

The streaming data includes:
- `user_id`: Unique user identifier
- `created_date`/`created_at`: Session timestamp
- `timezone`/`state`: Geographic information
- `show_*`: Content metadata (name, type, genre, rating, duration)
- `user_watch_duration_seconds`: Actual watch time
- Calculated: `completion_rate`, `viewing_hour`

## 🔧 Configuration

### Environment Variables
No environment variables required for basic setup.

### Data Sources
- Default data location: `data/streaming-data.json`
- To use custom data, modify the path in `load_streaming_data()` function

## 🚀 Deployment

### Local Development
```bash
uv run python main.py
```

### Production
For production deployment, consider:
- Using a production WSGI server (gunicorn, uvicorn)
- Setting up environment-specific configurations
- Implementing proper logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Air Framework](https://github.com/amiyoAir/air) - For the reactive web framework
- [Boring Semantic Layer](https://github.com/boring-ml/boring-semantic-layer) - For semantic analytics
- [FastAPI](https://fastapi.tiangolo.com/) - For the REST API
- [Chart.js](https://www.chartjs.org/) - For interactive visualizations

## 📞 Support

For questions, issues, or contributions:
- Open an issue in the repository
- Check the API documentation at `/api/docs`
- Review the test files for usage examples

---

**Happy Streaming Analytics! 📺📊**
