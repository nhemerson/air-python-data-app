import air
import json
import os
import asyncio
import random
import math
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = air.Air()
api = FastAPI()

# Load streaming data
def load_streaming_data_json():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'streaming-data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

# Generate chart data using simple calculation
def generate_daily_completion_chart_data():
    """Generate daily completion rate trend data using simple calculation"""
    try:
        # Load data directly from JSON
        data = load_streaming_data_json()
        
        # Calculate completion rates for each session
        daily_data = {}
        for record in data:
            date = record['created_date']
            show_duration = float(record['show_duration_seconds'])
            watch_duration = float(record['user_watch_duration_seconds'])
            
            # Calculate completion rate for this session
            completion_rate = (watch_duration / show_duration) * 100 if show_duration > 0 else 0
            
            # Group by date
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(completion_rate)
        
        # Calculate daily averages
        daily_averages = {}
        for date, rates in daily_data.items():
            daily_averages[date] = sum(rates) / len(rates)
        
        # Sort by date and prepare chart data
        sorted_dates = sorted(daily_averages.keys())
        labels = sorted_dates
        completion_rates = [round(daily_averages[date], 2) for date in sorted_dates]
        
        # Prepare data for Chart.js
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Daily Completion Rate (%)',
                'data': completion_rates,
                'borderColor': 'rgb(76, 175, 80)',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'tension': 0.1,
                'fill': True
            }]
        }
        
        return chart_data
    except Exception as e:
        # Return empty data if there's an error
        print(f"Error generating chart data: {e}")
        return {
            'labels': [],
            'datasets': [{
                'label': 'Daily Completion Rate (%)',
                'data': [],
                'borderColor': 'rgb(76, 175, 80)',
                'backgroundColor': 'rgba(76, 175, 80, 0.1)',
                'tension': 0.1,
                'fill': True
            }]
        }

def generate_daily_watched_hours_chart_data():
    """Generate daily total watched hours trend data"""
    try:
        # Load data directly from JSON
        data = load_streaming_data_json()
        
        # Calculate total watched hours for each day
        daily_hours = {}
        for record in data:
            date = record['created_date']
            watch_duration_seconds = float(record['user_watch_duration_seconds'])
            
            # Convert seconds to hours
            watch_hours = watch_duration_seconds / 3600
            
            # Group by date and sum hours
            if date not in daily_hours:
                daily_hours[date] = 0
            daily_hours[date] += watch_hours
        
        # Sort by date and prepare chart data
        sorted_dates = sorted(daily_hours.keys())
        labels = sorted_dates
        hours_data = [round(daily_hours[date], 2) for date in sorted_dates]
        
        # Prepare data for Chart.js
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Daily Total Watched Hours',
                'data': hours_data,
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                'tension': 0.1,
                'fill': True
            }]
        }
        
        return chart_data
    except Exception as e:
        # Return empty data if there's an error
        print(f"Error generating watched hours chart data: {e}")
        return {
            'labels': [],
            'datasets': [{
                'label': 'Daily Total Watched Hours',
                'data': [],
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                'tension': 0.1,
                'fill': True
            }]
        }

@app.get("/")
def streaming_data_table():
    data = load_streaming_data_json()
    chart_data = generate_daily_completion_chart_data()
    watched_hours_chart_data = generate_daily_watched_hours_chart_data()
    
    # Don't limit data for filtering - let JavaScript handle it
    # But we'll still show counts properly
    
    # Get unique values for filter dropdowns
    show_types = sorted(list(set(record["show_type"] for record in data)))
    genres = sorted(list(set(record["show_genre"] for record in data)))
    states = sorted(list(set(record["state"] for record in data)))
    ratings = sorted(list(set(record["show_rating"] for record in data)))
    
    return air.Html(
        air.Head(
            air.Title("Streaming Data Dashboard"),
            air.Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
            air.Style("""
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 100%;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                
                /* Filter Controls */
                .filter-section {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                    border: 1px solid #e9ecef;
                }
                .filter-row {
                    display: flex;
                    gap: 15px;
                    align-items: center;
                    flex-wrap: wrap;
                    margin-bottom: 15px;
                }
                .filter-group {
                    display: flex;
                    flex-direction: column;
                    min-width: 150px;
                }
                .filter-group label {
                    font-size: 12px;
                    font-weight: bold;
                    color: #666;
                    margin-bottom: 4px;
                }
                .filter-group input, .filter-group select {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                .filter-group input:focus, .filter-group select:focus {
                    outline: none;
                    border-color: #4CAF50;
                    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
                }
                .clear-btn {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-top: 18px;
                }
                .clear-btn:hover {
                    background-color: #c82333;
                }
                
                /* Table Styles */
                .table-container {
                    max-height: 600px;
                    overflow-y: auto;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }
                th, td {
                    padding: 12px 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                    cursor: pointer;
                    user-select: none;
                }
                th:hover {
                    background-color: #45a049;
                }
                th .sort-indicator {
                    margin-left: 5px;
                    font-size: 12px;
                }
                tbody tr {
                    display: table-row;
                }
                tbody tr.hidden {
                    display: none;
                }
                tbody tr:hover {
                    background-color: #f5f5f5;
                }
                .info {
                    text-align: center;
                    color: #666;
                    margin-bottom: 20px;
                }
                .numeric {
                    text-align: right;
                }
                .small-col {
                    width: 80px;
                }
                .medium-col {
                    width: 120px;
                }
                
                /* Result counter */
                .result-counter {
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 4px;
                    text-align: center;
                    font-weight: bold;
                    color: #1976d2;
                    margin-bottom: 15px;
                }
                
                /* Collapsible Table Styles */
                .table-header {
                    margin-bottom: 10px;
                }
                .table-toggle-btn {
                    width: 100%;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white;
                    border: none;
                    padding: 15px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 18px;
                    font-weight: bold;
                    text-align: left;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .table-toggle-btn:hover {
                    background: linear-gradient(135deg, #45a049, #3d8b40);
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    transform: translateY(-1px);
                }
                .table-toggle-btn:active {
                    transform: translateY(0);
                }
                .collapsible-content {
                    transition: all 0.4s ease;
                    overflow: hidden;
                    opacity: 1;
                    max-height: none;
                }
                .collapsible-content.collapsed {
                    max-height: 0;
                    opacity: 0;
                    margin-bottom: 0;
                    padding-top: 0;
                    padding-bottom: 0;
                }
                #collapse-icon {
                    transition: transform 0.3s ease;
                    font-size: 16px;
                }
                #collapse-icon.rotated {
                    transform: rotate(180deg);
                }
                
                /* Chart Styles */
                .charts-section {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .chart-section {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    flex: 1;
                    min-width: 400px;
                }
                .chart-title {
                    text-align: center;
                    margin-bottom: 20px;
                    color: #333;
                    font-size: 18px;
                    font-weight: bold;
                }
                .chart-container {
                    position: relative;
                    height: 400px;
                    width: 100%;
                }
                
                /* Interactive Streaming Section */
                .interactive-section {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    margin-bottom: 30px;
                    color: white;
                }
                .interactive-title {
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: white;
                }
                .interactive-subtitle {
                    text-align: center;
                    font-size: 14px;
                    margin-bottom: 25px;
                    color: rgba(255,255,255,0.9);
                }
                .stream-controls {
                    display: flex;
                    gap: 20px;
                    align-items: center;
                    justify-content: center;
                    flex-wrap: wrap;
                    margin-bottom: 30px;
                }
                .stream-input-group {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                .stream-input-group label {
                    font-weight: bold;
                    font-size: 14px;
                }
                .stream-input-group input {
                    padding: 12px 16px;
                    border: 2px solid rgba(255,255,255,0.3);
                    border-radius: 8px;
                    font-size: 16px;
                    width: 200px;
                    background: rgba(255,255,255,0.95);
                    color: #333;
                }
                .stream-input-group input:focus {
                    outline: none;
                    border-color: #4CAF50;
                    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3);
                }
                .stream-btn {
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white;
                    border: none;
                    padding: 12px 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    margin-top: 22px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                }
                .stream-btn:hover {
                    background: linear-gradient(135deg, #45a049, #3d8b40);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
                }
                .stream-btn:active {
                    transform: translateY(0);
                }
                .stream-btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                }
                .stream-status {
                    text-align: center;
                    font-size: 14px;
                    min-height: 24px;
                    margin-bottom: 20px;
                    font-weight: bold;
                }
                .stream-chart-wrapper {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .stream-chart-container {
                    position: relative;
                    height: 350px;
                    width: 100%;
                }
                .progress-bar-container {
                    width: 100%;
                    height: 6px;
                    background: rgba(255,255,255,0.3);
                    border-radius: 3px;
                    overflow: hidden;
                    margin-bottom: 20px;
                }
                .progress-bar {
                    height: 100%;
                    background: linear-gradient(90deg, #4CAF50, #8BC34A);
                    width: 0%;
                    transition: width 0.2s ease;
                    border-radius: 3px;
                }
            """)
        ),
        air.Body(
            air.Div(
                air.H1("📺 Streaming Data Dashboard"),
                
                # Charts Section
                air.Div(
                    air.Div(
                        air.Div("📈 Daily Completion Rate Trend", class_="chart-title"),
                        air.Div(
                            air.Canvas(id="completionChart"),
                            class_="chart-container"
                        ),
                        class_="chart-section"
                    ),
                    air.Div(
                        air.Div("🕒 Daily Total Watched Hours", class_="chart-title"),
                        air.Div(
                            air.Canvas(id="watchedHoursChart"),
                            class_="chart-container"
                        ),
                        class_="chart-section"
                    ),
                    class_="charts-section"
                ),
                
                # Interactive Streaming Section
                air.Div(
                    air.Div("⚡ Real-Time Async Data Streaming", class_="interactive-title"),
                    air.Div("Watch data points generate and stream in real-time! This showcases Air's async capabilities.", class_="interactive-subtitle"),
                    
                    # Progress Bar
                    air.Div(
                        air.Div(class_="progress-bar", id="stream-progress"),
                        class_="progress-bar-container"
                    ),
                    
                    # Controls
                    air.Div(
                        air.Div(
                            air.Label("Number of Data Points (5-100)", for_="num-points-input"),
                            air.Input(
                                type="number",
                                id="num-points-input",
                                min="5",
                                max="100",
                                value="30",
                                placeholder="Enter number of points"
                            ),
                            class_="stream-input-group"
                        ),
                        air.Button("🚀 Start Streaming", class_="stream-btn", id="stream-btn", onclick="startStreaming()"),
                        class_="stream-controls"
                    ),
                    
                    # Status
                    air.Div("Enter a number and click 'Start Streaming' to begin", id="stream-status", class_="stream-status"),
                    
                    # Chart
                    air.Div(
                        air.Div(
                            air.Canvas(id="streamChart"),
                            class_="stream-chart-container"
                        ),
                        class_="stream-chart-wrapper"
                    ),
                    
                    class_="interactive-section"
                ),
                
                # Filter Section
                air.Div(
                    air.Div(
                        air.Div(
                            air.Label("🔍 Search", for_="search-input"),
                            air.Input(
                                type="text",
                                id="search-input",
                                placeholder="Search shows, users, or any data...",
                                oninput="filterTable()"
                            ),
                            class_="filter-group"
                        ),
                        air.Div(
                            air.Label("📺 Show Type", for_="type-filter"),
                            air.Select(
                                air.Option("All Types", value=""),
                                *[air.Option(show_type, value=show_type) for show_type in show_types],
                                id="type-filter",
                                onchange="filterTable()"
                            ),
                            class_="filter-group"
                        ),
                        air.Div(
                            air.Label("🎭 Genre", for_="genre-filter"),
                            air.Select(
                                air.Option("All Genres", value=""),
                                *[air.Option(genre, value=genre) for genre in genres],
                                id="genre-filter",
                                onchange="filterTable()"
                            ),
                            class_="filter-group"
                        ),
                        air.Div(
                            air.Label("📍 State", for_="state-filter"),
                            air.Select(
                                air.Option("All States", value=""),
                                *[air.Option(state, value=state) for state in states],
                                id="state-filter",
                                onchange="filterTable()"
                            ),
                            class_="filter-group"
                        ),
                        air.Div(
                            air.Label("⭐ Rating", for_="rating-filter"),
                            air.Select(
                                air.Option("All Ratings", value=""),
                                *[air.Option(rating, value=rating) for rating in ratings],
                                id="rating-filter",
                                onchange="filterTable()"
                            ),
                            class_="filter-group"
                        ),
                        air.Button("Clear All", class_="clear-btn", onclick="clearFilters()"),
                        class_="filter-row"
                    ),
                    class_="filter-section"
                ),
                
                # Table Header with Collapse Toggle
                air.Div(
                    air.Button(
                        "📋 Streaming Data Table ",
                        air.Span("▲", id="collapse-icon", class_="rotated"),
                        onclick="toggleTable()",
                        class_="table-toggle-btn",
                        id="table-toggle"
                    ),
                    class_="table-header"
                ),
                
                # Collapsible Table Section
                air.Div(
                    # Result Counter
                    air.Div(
                        "Showing ",
                        air.Span(str(len(data)), id="visible-count"),
                        f" of {len(data)} total records",
                        class_="result-counter",
                        id="result-counter"
                    ),
                
                # Table Container
                air.Div(
                    air.Table(
                        air.Thead(
                            air.Tr(
                                air.Th("User ID", class_="small-col", onclick="sortTable(0)", **{"data-column": "0"}),
                                air.Th("Date", class_="medium-col", onclick="sortTable(1)", **{"data-column": "1"}),
                                air.Th("Time", class_="medium-col", onclick="sortTable(2)", **{"data-column": "2"}),
                                air.Th("State", class_="small-col", onclick="sortTable(3)", **{"data-column": "3"}),
                                air.Th("Show Name", onclick="sortTable(4)", **{"data-column": "4"}),
                                air.Th("Type", class_="medium-col", onclick="sortTable(5)", **{"data-column": "5"}),
                                air.Th("Genre", class_="medium-col", onclick="sortTable(6)", **{"data-column": "6"}),
                                air.Th("Rating", class_="small-col", onclick="sortTable(7)", **{"data-column": "7"}),
                                air.Th("Duration", class_="small-col numeric", onclick="sortTable(8)", **{"data-column": "8"}),
                                air.Th("Watched", class_="small-col numeric", onclick="sortTable(9)", **{"data-column": "9"}),
                                air.Th("% Watched", class_="small-col numeric", onclick="sortTable(10)", **{"data-column": "10"}),
                            )
                        ),
                        air.Tbody(
                            *[
                                air.Tr(
                                    air.Td(record["user_id"]),
                                    air.Td(record["created_date"]),
                                    air.Td(record["created_at"].split()[1][:5]),  # Just time part
                                    air.Td(record["state"]),
                                    air.Td(record["show_name"]),
                                    air.Td(record["show_type"]),
                                    air.Td(record["show_genre"]),
                                    air.Td(record["show_rating"]),
                                    air.Td(f"{int(record['show_duration_seconds'])//60}m", class_="numeric"),
                                    air.Td(f"{int(record['user_watch_duration_seconds'])//60}m", class_="numeric"),
                                    air.Td(f"{round((int(record['user_watch_duration_seconds']) / int(record['show_duration_seconds'])) * 100)}%", class_="numeric"),
                                    id=f"row-{i}"
                                )
                                for i, record in enumerate(data)
                            ],
                            id="table-body"
                        ),
                        id="data-table"
                    ),
                    class_="table-container"
                ),
                    class_="collapsible-content collapsed",
                    id="table-content"
                ),
                
                air.P(air.A("API Docs", target="_blank", href="/api/docs"), class_="info"),
                class_="container"
            ),
            
            # JavaScript for filtering and sorting
            air.Script("""
                let sortDirection = {};
                let currentData = """ + json.dumps(data) + """;
                let chartData = """ + json.dumps(chart_data) + """;
                let watchedHoursChartData = """ + json.dumps(watched_hours_chart_data) + """;
                let completionChart = null;
                let watchedHoursChart = null;
                let streamChart = null;
                let streamingData = {
                    labels: [],
                    data: []
                };
                let eventSource = null;
                
                // Initialize Charts
                function initChart() {
                    // Initialize Completion Rate Chart
                    const completionCtx = document.getElementById('completionChart').getContext('2d');
                    completionChart = new Chart(completionCtx, {
                        type: 'line',
                        data: chartData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: 'Completion Rate (%)'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Date'
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top'
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false,
                                    callbacks: {
                                        label: function(context) {
                                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                                        }
                                    }
                                }
                            },
                            interaction: {
                                mode: 'nearest',
                                axis: 'x',
                                intersect: false
                            }
                        }
                    });
                    
                    // Initialize Watched Hours Chart
                    const hoursCtx = document.getElementById('watchedHoursChart').getContext('2d');
                    watchedHoursChart = new Chart(hoursCtx, {
                        type: 'line',
                        data: watchedHoursChartData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Hours Watched'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Date'
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top'
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false,
                                    callbacks: {
                                        label: function(context) {
                                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' hours';
                                        }
                                    }
                                }
                            },
                            interaction: {
                                mode: 'nearest',
                                axis: 'x',
                                intersect: false
                            }
                        }
                    });
                    
                    // Initialize Stream Chart
                    const streamCtx = document.getElementById('streamChart').getContext('2d');
                    streamChart = new Chart(streamCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Streamed Data Points',
                                data: [],
                                borderColor: 'rgb(102, 126, 234)',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                borderWidth: 2,
                                tension: 0.4,
                                fill: true,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                pointBackgroundColor: 'rgb(102, 126, 234)',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            animation: {
                                duration: 300
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: 'Value',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    },
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.05)'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Data Point Index',
                                        font: {
                                            size: 14,
                                            weight: 'bold'
                                        }
                                    },
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.05)'
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                    labels: {
                                        font: {
                                            size: 12,
                                            weight: 'bold'
                                        }
                                    }
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false,
                                    callbacks: {
                                        label: function(context) {
                                            return 'Value: ' + context.parsed.y.toFixed(2);
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
                
                // Stream data functionality
                function startStreaming() {
                    const numPoints = parseInt(document.getElementById('num-points-input').value);
                    
                    // Validate input
                    if (isNaN(numPoints) || numPoints < 5 || numPoints > 100) {
                        alert('Please enter a number between 5 and 100');
                        return;
                    }
                    
                    // Reset chart and data
                    streamingData.labels = [];
                    streamingData.data = [];
                    streamChart.data.labels = [];
                    streamChart.data.datasets[0].data = [];
                    streamChart.update();
                    
                    // Reset progress bar
                    document.getElementById('stream-progress').style.width = '0%';
                    
                    // Disable button during streaming
                    const btn = document.getElementById('stream-btn');
                    btn.disabled = true;
                    btn.textContent = '⏳ Streaming...';
                    
                    // Update status
                    document.getElementById('stream-status').textContent = 'Initializing stream...';
                    
                    // Close existing connection if any
                    if (eventSource) {
                        eventSource.close();
                    }
                    
                    // Create new EventSource connection
                    eventSource = new EventSource(`/api/stream-data/${numPoints}`);
                    
                    eventSource.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.complete) {
                            // Streaming complete
                            eventSource.close();
                            btn.disabled = false;
                            btn.textContent = '🚀 Start Streaming';
                            document.getElementById('stream-status').textContent = 
                                `✅ Streaming complete! Generated ${numPoints} data points.`;
                            document.getElementById('stream-progress').style.width = '100%';
                        } else {
                            // Add new data point
                            streamChart.data.labels.push(data.x);
                            streamChart.data.datasets[0].data.push(data.y);
                            streamChart.update('none'); // Update without animation for smooth streaming
                            
                            // Update progress bar
                            document.getElementById('stream-progress').style.width = data.progress + '%';
                            
                            // Update status
                            document.getElementById('stream-status').textContent = 
                                `📊 Streaming... ${data.index + 1}/${data.total} points (${data.progress}%)`;
                        }
                    };
                    
                    eventSource.onerror = function(error) {
                        console.error('EventSource error:', error);
                        eventSource.close();
                        btn.disabled = false;
                        btn.textContent = '🚀 Start Streaming';
                        document.getElementById('stream-status').textContent = 
                            '❌ Error during streaming. Please try again.';
                    };
                }
                
                function filterTable() {
                    const searchTerm = document.getElementById('search-input').value.toLowerCase();
                    const typeFilter = document.getElementById('type-filter').value;
                    const genreFilter = document.getElementById('genre-filter').value;
                    const stateFilter = document.getElementById('state-filter').value;
                    const ratingFilter = document.getElementById('rating-filter').value;
                    
                    const tbody = document.getElementById('table-body');
                    const rows = tbody.getElementsByTagName('tr');
                    let visibleCount = 0;
                    
                    for (let i = 0; i < rows.length; i++) {
                        const row = rows[i];
                        const cells = row.getElementsByTagName('td');
                        
                        if (cells.length === 0) continue;
                        
                        const rowData = currentData[i];
                        let showRow = true;
                        
                        // Search filter
                        if (searchTerm) {
                            const rowText = Array.from(cells).map(cell => cell.textContent.toLowerCase()).join(' ');
                            if (!rowText.includes(searchTerm)) {
                                showRow = false;
                            }
                        }
                        
                        // Type filter
                        if (typeFilter && rowData.show_type !== typeFilter) {
                            showRow = false;
                        }
                        
                        // Genre filter
                        if (genreFilter && rowData.show_genre !== genreFilter) {
                            showRow = false;
                        }
                        
                        // State filter
                        if (stateFilter && rowData.state !== stateFilter) {
                            showRow = false;
                        }
                        
                        // Rating filter
                        if (ratingFilter && rowData.show_rating !== ratingFilter) {
                            showRow = false;
                        }
                        
                        if (showRow) {
                            row.classList.remove('hidden');
                            visibleCount++;
                        } else {
                            row.classList.add('hidden');
                        }
                    }
                    
                    // Update counter
                    document.getElementById('visible-count').textContent = visibleCount;
                }
                
                function sortTable(columnIndex) {
                    const table = document.getElementById('data-table');
                    const tbody = table.getElementsByTagName('tbody')[0];
                    const rows = Array.from(tbody.getElementsByTagName('tr'));
                    
                    // Toggle sort direction
                    if (sortDirection[columnIndex] === undefined) {
                        sortDirection[columnIndex] = 'asc';
                    } else {
                        sortDirection[columnIndex] = sortDirection[columnIndex] === 'asc' ? 'desc' : 'asc';
                    }
                    
                    const isAsc = sortDirection[columnIndex] === 'asc';
                    
                    rows.sort((a, b) => {
                        const aCell = a.getElementsByTagName('td')[columnIndex];
                        const bCell = b.getElementsByTagName('td')[columnIndex];
                        
                        if (!aCell || !bCell) return 0;
                        
                        let aValue = aCell.textContent.trim();
                        let bValue = bCell.textContent.trim();
                        
                        // Handle numeric columns
                        if (columnIndex >= 8) { // Duration, Watched, % Watched
                            aValue = parseFloat(aValue.replace(/[^0-9.]/g, '')) || 0;
                            bValue = parseFloat(bValue.replace(/[^0-9.]/g, '')) || 0;
                            return isAsc ? aValue - bValue : bValue - aValue;
                        }
                        
                        // Handle date columns
                        if (columnIndex === 1) { // Date
                            aValue = new Date(aValue);
                            bValue = new Date(bValue);
                            return isAsc ? aValue - bValue : bValue - aValue;
                        }
                        
                        // Handle text columns
                        return isAsc ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
                    });
                    
                    // Re-append sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                    
                    // Update sort indicators
                    const headers = table.getElementsByTagName('th');
                    for (let i = 0; i < headers.length; i++) {
                        const indicator = headers[i].querySelector('.sort-indicator');
                        if (indicator) {
                            indicator.remove();
                        }
                        
                        if (i === columnIndex) {
                            const span = document.createElement('span');
                            span.className = 'sort-indicator';
                            span.textContent = isAsc ? '↑' : '↓';
                            headers[i].appendChild(span);
                        }
                    }
                }
                
                function clearFilters() {
                    document.getElementById('search-input').value = '';
                    document.getElementById('type-filter').value = '';
                    document.getElementById('genre-filter').value = '';
                    document.getElementById('state-filter').value = '';
                    document.getElementById('rating-filter').value = '';
                    filterTable();
                }
                
                function toggleTable() {
                    const content = document.getElementById('table-content');
                    const icon = document.getElementById('collapse-icon');
                    
                    if (content.classList.contains('collapsed')) {
                        // Expand the table
                        content.classList.remove('collapsed');
                        icon.classList.remove('rotated');
                        icon.textContent = '▼';
                    } else {
                        // Collapse the table
                        content.classList.add('collapsed');
                        icon.classList.add('rotated');
                        icon.textContent = '▲';
                    }
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    initChart();
                    filterTable();
                });
            """)
        ),
    )

@api.get("/")
def api_root():
    return {"message": "Streaming Data API", "total_records": len(load_streaming_data_json())}

@api.get("/data")
def get_streaming_data():
    return load_streaming_data_json()

# Async streaming endpoint for progressive data generation
async def generate_progressive_data(num_points: int):
    """
    Progressively generate data points with simulated computation delay.
    This demonstrates Air's async/streaming capabilities.
    """
    for i in range(num_points):
        # Simulate some computation time
        await asyncio.sleep(0.3)  # 100ms delay between points
        
        # Generate interesting data using sine wave with some randomness
        x = i
        y = 50 + 30 * math.sin(i * .2) + random.uniform(-5, 5)
        
        # Stream as Server-Sent Events format
        data = {
            'index': i,
            'x': x,
            'y': round(y, 2),
            'total': num_points,
            'progress': round((i + 1) / num_points * 100, 1)
        }
        
        yield f"data: {json.dumps(data)}\n\n"
    
    # Send completion signal
    yield f"data: {json.dumps({'complete': True})}\n\n"

@api.get("/stream-data/{num_points}")
async def stream_data_endpoint(num_points: int):
    """
    Endpoint that streams data progressively to showcase async capabilities.
    User specifies how many data points to generate.
    """
    # Limit to reasonable range
    num_points = max(5, min(num_points, 100))
    
    return StreamingResponse(
        generate_progressive_data(num_points),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Combining the Air and FastAPI apps into one
app.mount("/api", api)
