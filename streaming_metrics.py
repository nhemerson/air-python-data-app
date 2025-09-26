"""
Streaming Analytics Metrics using Boring Semantic Layer
=====================================================

This module defines 4 key metrics for streaming data analysis:
1. Watch Completion Rate by Content Type
2. User Engagement Score by Geographic Region  
3. Content Performance Index by Genre
4. Peak Viewing Time Analysis
"""

import json
import ibis
from boring_semantic_layer import SemanticModel
from datetime import datetime
import pandas as pd

# Load the streaming data
def load_streaming_data():
    """Load streaming data from JSON file into a pandas DataFrame"""
    with open('/Users/hoytemerson/Documents/Applications/air-python/data/streaming-data.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Convert datetime strings to datetime objects
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Convert numeric columns
    numeric_cols = ['show_duration_seconds', 'user_watch_duration_seconds']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
    
    # Calculate completion rate
    df['completion_rate'] = (df['user_watch_duration_seconds'] / df['show_duration_seconds']) * 100
    
    # Extract hour from datetime for peak viewing analysis
    df['viewing_hour'] = df['created_at'].dt.hour
    
    return df

# Create Ibis table from DataFrame
def create_ibis_table(df):
    """Create an Ibis table from pandas DataFrame"""
    # For this example, we'll use DuckDB as the backend
    con = ibis.duckdb.connect()
    table = con.create_table('streaming_data', df)
    return table

class StreamingMetrics:
    """Class to define and calculate streaming metrics using Boring Semantic Layer"""
    
    def __init__(self, table):
        self.table = table
        self.setup_semantic_models()
    
    def setup_semantic_models(self):
        """Setup semantic models for different metric calculations"""
        
        # 1. Watch Completion Rate by Content Type Model
        self.completion_model = SemanticModel(
            table=self.table,
            dimensions={
                "content_type": lambda t: t.show_type,
                "genre": lambda t: t.show_genre,
                "rating": lambda t: t.show_rating
            },
            measures={
                "avg_completion_rate": lambda t: t.completion_rate.mean(),
                "total_sessions": lambda t: t.count(),
                "avg_watch_duration": lambda t: t.user_watch_duration_seconds.mean(),
                "avg_show_duration": lambda t: t.show_duration_seconds.mean()
            }
        )
        
        # 2. Geographic Engagement Model
        self.geographic_model = SemanticModel(
            table=self.table,
            dimensions={
                "timezone": lambda t: t.timezone,
                "state": lambda t: t.state
            },
            measures={
                "avg_engagement_score": lambda t: (
                    t.user_watch_duration_seconds.mean() * t.completion_rate.mean() / 100
                ),
                "total_watch_time": lambda t: t.user_watch_duration_seconds.sum(),
                "session_count": lambda t: t.count(),
                "unique_users": lambda t: t.user_id.nunique(),
                "avg_session_length": lambda t: t.user_watch_duration_seconds.mean()
            }
        )
        
        # 3. Content Performance Model
        self.content_performance_model = SemanticModel(
            table=self.table,
            dimensions={
                "show_name": lambda t: t.show_name,
                "genre": lambda t: t.show_genre,
                "content_type": lambda t: t.show_type
            },
            measures={
                "performance_index": lambda t: (
                    (t.user_watch_duration_seconds.sum() / 3600) * # Total hours watched
                    t.user_id.nunique() * # Unique viewers
                    (t.completion_rate.mean() / 100) # Average completion rate
                ),
                "total_watch_hours": lambda t: t.user_watch_duration_seconds.sum() / 3600,
                "unique_viewers": lambda t: t.user_id.nunique(),
                "avg_completion_rate": lambda t: t.completion_rate.mean()
            }
        )
        
        # 4. Peak Viewing Time Model
        self.viewing_time_model = SemanticModel(
            table=self.table,
            dimensions={
                "viewing_hour": lambda t: t.viewing_hour,
                "timezone": lambda t: t.timezone
            },
            measures={
                "session_count": lambda t: t.count(),
                "total_watch_time": lambda t: t.user_watch_duration_seconds.sum(),
                "avg_session_length": lambda t: t.user_watch_duration_seconds.mean(),
                "peak_score": lambda t: t.count() * t.user_watch_duration_seconds.mean()
            }
        )
        
        # 5. Daily Completion Rate Trend Model
        self.daily_trend_model = SemanticModel(
            table=self.table,
            dimensions={
                "created_date": lambda t: t.created_date,
                "date_formatted": lambda t: t.created_date  # For proper date formatting
            },
            measures={
                "daily_avg_completion_rate": lambda t: t.completion_rate.mean(),
                "daily_session_count": lambda t: t.count(),
                "daily_total_watch_time": lambda t: t.user_watch_duration_seconds.sum(),
                "daily_avg_watch_duration": lambda t: t.user_watch_duration_seconds.mean()
            }
        )

    def get_completion_rate_by_content_type(self):
        """Metric 1: Watch Completion Rate by Content Type"""
        return self.completion_model.query(
            dimensions=["content_type"],
            measures=["avg_completion_rate", "total_sessions", "avg_watch_duration"]
        )
    
    def get_engagement_by_region(self):
        """Metric 2: User Engagement Score by Geographic Region"""
        return self.geographic_model.query(
            dimensions=["timezone", "state"],
            measures=["avg_engagement_score", "total_watch_time", "session_count", "unique_users"]
        )
    
    def get_content_performance_by_genre(self):
        """Metric 3: Content Performance Index by Genre"""
        return self.content_performance_model.query(
            dimensions=["genre"],
            measures=["performance_index", "total_watch_hours", "unique_viewers", "avg_completion_rate"]
        )
    
    def get_peak_viewing_analysis(self):
        """Metric 4: Peak Viewing Time Analysis"""
        return self.viewing_time_model.query(
            dimensions=["viewing_hour"],
            measures=["session_count", "total_watch_time", "avg_session_length", "peak_score"]
        )
    
    def get_detailed_content_performance(self):
        """Detailed view of content performance by individual shows"""
        return self.content_performance_model.query(
            dimensions=["show_name", "genre", "content_type"],
            measures=["performance_index", "total_watch_hours", "unique_viewers", "avg_completion_rate"]
        )
    
    def get_daily_completion_rate_trend(self):
        """Metric 5: Daily Completion Rate Trend"""
        return self.daily_trend_model.query(
            dimensions=["created_date"],
            measures=["daily_avg_completion_rate", "daily_session_count", "daily_total_watch_time"]
        )

def main():
    """Main function to demonstrate the metrics"""
    print("Loading streaming data...")
    df = load_streaming_data()
    print(f"Loaded {len(df)} streaming sessions")
    
    print("\nCreating Ibis table...")
    table = create_ibis_table(df)
    
    print("\nInitializing streaming metrics...")
    metrics = StreamingMetrics(table)
    
    print("\n" + "="*60)
    print("STREAMING ANALYTICS METRICS")
    print("="*60)
    
    # Metric 1: Watch Completion Rate by Content Type
    print("\n1. WATCH COMPLETION RATE BY CONTENT TYPE")
    print("-" * 45)
    completion_data = metrics.get_completion_rate_by_content_type().execute()
    print(completion_data)
    
    # Metric 2: User Engagement by Region
    print("\n2. USER ENGAGEMENT SCORE BY GEOGRAPHIC REGION")
    print("-" * 48)
    engagement_data = metrics.get_engagement_by_region().execute()
    print(engagement_data.head(10))  # Show top 10 regions
    
    # Metric 3: Content Performance by Genre
    print("\n3. CONTENT PERFORMANCE INDEX BY GENRE")
    print("-" * 40)
    performance_data = metrics.get_content_performance_by_genre().execute()
    print(performance_data)
    
    # Metric 4: Peak Viewing Time Analysis
    print("\n4. PEAK VIEWING TIME ANALYSIS")
    print("-" * 32)
    peak_data = metrics.get_peak_viewing_analysis().execute()
    print(peak_data)
    
    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
