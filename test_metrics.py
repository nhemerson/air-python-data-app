"""
Test script for streaming metrics
"""

import sys
import traceback

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import json
        import pandas as pd
        print("✓ pandas imported successfully")
        
        import ibis
        print("✓ ibis imported successfully")
        
        from boring_semantic_layer import SemanticModel
        print("✓ boring_semantic_layer imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_loading():
    """Test loading the streaming data"""
    try:
        import json
        import pandas as pd
        
        with open('/Users/hoytemerson/Documents/Applications/air-python/data/streaming-data.json', 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        print(f"✓ Data loaded successfully: {len(df)} records")
        
        # Check data structure
        expected_columns = ['user_id', 'created_date', 'created_at', 'timezone', 'state', 
                          'show_duration_seconds', 'user_watch_duration_seconds', 'show_id',
                          'show_name', 'show_type', 'show_genre', 'show_rating', 'show_description']
        
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            print(f"⚠ Missing columns: {missing_cols}")
        else:
            print("✓ All expected columns present")
        
        # Basic data validation
        print(f"✓ Date range: {df['created_date'].min()} to {df['created_date'].max()}")
        print(f"✓ Content types: {df['show_type'].unique()}")
        print(f"✓ Genres: {df['show_genre'].unique()}")
        print(f"✓ Timezones: {df['timezone'].unique()}")
        
        return df
    except Exception as e:
        print(f"✗ Data loading error: {e}")
        return None

def test_basic_metrics():
    """Test basic metric calculations without semantic layer"""
    try:
        import pandas as pd
        
        df = test_data_loading()
        if df is None:
            return False
        
        # Convert duration columns to numeric (they come as strings from JSON)
        df['show_duration_seconds'] = pd.to_numeric(df['show_duration_seconds'], errors='coerce')
        df['user_watch_duration_seconds'] = pd.to_numeric(df['user_watch_duration_seconds'], errors='coerce')
        
        # Basic calculations
        df['completion_rate'] = (df['user_watch_duration_seconds'] / df['show_duration_seconds']) * 100
        
        # Metric 1: Completion rate by content type
        completion_by_type = df.groupby('show_type').agg({
            'completion_rate': 'mean',
            'user_id': 'count'
        }).round(2)
        print("\n📊 COMPLETION RATE BY CONTENT TYPE:")
        print(completion_by_type)
        
        # Metric 2: Engagement by region
        engagement_by_region = df.groupby('timezone').agg({
            'user_watch_duration_seconds': 'mean',
            'completion_rate': 'mean',
            'user_id': ['count', 'nunique']
        }).round(2)
        print("\n📊 ENGAGEMENT BY TIMEZONE:")
        print(engagement_by_region.head())
        
        # Metric 3: Performance by genre
        performance_by_genre = df.groupby('show_genre').agg({
            'user_watch_duration_seconds': 'sum',
            'user_id': 'nunique',
            'completion_rate': 'mean'
        }).round(2)
        print("\n📊 PERFORMANCE BY GENRE:")
        print(performance_by_genre)
        
        # Metric 4: Peak viewing times
        df['viewing_hour'] = pd.to_datetime(df['created_at']).dt.hour
        peak_viewing = df.groupby('viewing_hour').agg({
            'user_id': 'count',
            'user_watch_duration_seconds': 'sum'
        }).round(2)
        print("\n📊 VIEWING BY HOUR:")
        print(peak_viewing.head(10))
        
        return True
    except Exception as e:
        print(f"✗ Basic metrics error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Streaming Metrics Implementation")
    print("=" * 50)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing data loading and basic metrics...")
    metrics_ok = test_basic_metrics()
    
    print("\n" + "=" * 50)
    if imports_ok and metrics_ok:
        print("✅ All tests passed! Ready to use Boring Semantic Layer.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the full metrics: python streaming_metrics.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
        if not imports_ok:
            print("   - Install missing packages: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
