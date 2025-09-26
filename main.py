import air
import json
import os
from fastapi import FastAPI

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

# Combining the Air and FastAPI apps into one
app.mount("/api", api)
