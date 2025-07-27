import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime
import json
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from ..core.config import settings
from ..utils.logger import setup_logger
from .ai_client import ai_client
from ..models.insights import (
    InsightQuery, InsightResponse, DataSourceInfo, DataSourceList,
    DataSourceType, InsightType
)

logger = setup_logger(__name__)

class InsightService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.supported_extensions = ['.csv', '.xlsx', '.xls']
        
    async def generate_insight(self, query: InsightQuery) -> InsightResponse:
        """
        Generate business insights from data using OpenAI and pandas analysis.
        
        Args:
            query: InsightQuery containing the question and data source info
            
        Returns:
            InsightResponse with analysis results
        """
        try:
            logger.info(f"Generating insight for question: '{query.question[:50]}...'")
            
            # Load and prepare data
            df = await self._load_data_source(query.data_source, query.data_source_type)
            if df is None:
                raise ValueError(f"Could not load data source: {query.data_source}")
            
            # Auto-detect KPIs and key metrics
            kpis = self.auto_detect_kpis(df)
            
            # Apply filters if provided
            if query.filters:
                df = self._apply_filters(df, query.filters)
            
            # Perform advanced analysis if requested
            advanced_analysis = {}
            if hasattr(query, 'analysis_type') and query.analysis_type:
                advanced_analysis = self.perform_advanced_analysis(df, query.analysis_type)
            
            # Analyze data and generate insight
            analysis_result = await self._analyze_data(df, query.question, kpis, advanced_analysis)
            
            # Determine insight type
            insight_type = self._determine_insight_type(query.question, analysis_result)
            
            # Generate visualization data if requested
            visualization_data = None
            if query.visualization_type:
                visualization_data = self._generate_visualization_data(df, query.visualization_type, analysis_result, advanced_analysis)
            
            # Create response
            response = InsightResponse(
                question=query.question,
                answer=analysis_result['answer'],
                insight_type=insight_type,
                data_source=query.data_source,
                confidence_score=analysis_result['confidence'],
                visualization_data=visualization_data,
                supporting_data={
                    **analysis_result['supporting_data'],
                    'kpis': kpis,
                    'advanced_analysis': advanced_analysis
                },
                recommendations=analysis_result['recommendations']
            )
            
            logger.info(f"Insight generated successfully with confidence: {response.confidence_score}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating insight: {str(e)}")
            raise
    
    async def get_available_data_sources(self) -> DataSourceList:
        """
        Get list of available data sources for analysis.
        
        Returns:
            DataSourceList with available sources
        """
        try:
            sources = []
            
            # Check upload directory for CSV/Excel files
            if os.path.exists(self.upload_dir):
                for filename in os.listdir(self.upload_dir):
                    if any(filename.lower().endswith(ext) for ext in self.supported_extensions):
                        file_path = os.path.join(self.upload_dir, filename)
                        file_info = os.stat(file_path)
                        
                        # Determine file type
                        if filename.lower().endswith('.csv'):
                            file_type = DataSourceType.CSV
                        else:
                            file_type = DataSourceType.EXCEL
                        
                        # Get basic file info
                        source_info = DataSourceInfo(
                            id=filename,
                            name=filename,
                            type=file_type,
                            file_size=file_info.st_size,
                            last_updated=datetime.fromtimestamp(file_info.st_mtime)
                        )
                        
                        # Try to get column information
                        try:
                            df = await self._load_data_source(filename, file_type)
                            if df is not None:
                                source_info.columns = df.columns.tolist()
                                source_info.row_count = len(df)
                                source_info.description = f"{len(df)} rows, {len(df.columns)} columns"
                        except Exception as e:
                            logger.warning(f"Could not read file {filename}: {str(e)}")
                        
                        sources.append(source_info)
            
            return DataSourceList(sources=sources, total_count=len(sources))
            
        except Exception as e:
            logger.error(f"Error getting data sources: {str(e)}")
            raise
    
    async def _load_data_source(self, source_id: str, source_type: DataSourceType) -> Optional[pd.DataFrame]:
        """Load data from various sources."""
        try:
            if source_type in [DataSourceType.CSV, DataSourceType.EXCEL]:
                file_path = os.path.join(self.upload_dir, source_id)
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    return None
                
                if source_type == DataSourceType.CSV:
                    df = pd.read_csv(file_path)
                else:  # Excel
                    df = pd.read_excel(file_path)
                
                # Clean the data
                df = self._clean_dataframe(df)
                return df
                
            elif source_type == DataSourceType.DATABASE:
                # TODO: Implement database connection
                logger.warning("Database data sources not yet implemented")
                return None
                
            else:
                logger.error(f"Unsupported data source type: {source_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading data source {source_id}: {str(e)}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe for analysis."""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert date columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the dataframe."""
        filtered_df = df.copy()
        
        for column, filter_value in filters.items():
            if column in filtered_df.columns:
                if isinstance(filter_value, dict):
                    # Range filter
                    if 'min' in filter_value:
                        filtered_df = filtered_df[filtered_df[column] >= filter_value['min']]
                    if 'max' in filter_value:
                        filtered_df = filtered_df[filtered_df[column] <= filter_value['max']]
                elif isinstance(filter_value, list):
                    # List filter
                    filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
                else:
                    # Exact match filter
                    filtered_df = filtered_df[filtered_df[column] == filter_value]
        
        return filtered_df
    
    async def _analyze_data(self, df: pd.DataFrame, question: str, kpis: Dict[str, Any], advanced_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data using OpenAI and pandas."""
        try:
            # Prepare data summary for OpenAI
            data_summary = self._prepare_data_summary(df)
            
            # Create analysis prompt
            prompt = f"""
            You are a business intelligence analyst. Analyze the following data and answer the user's question.
            
            Data Summary:
            {data_summary}
            
            User Question: {question}
            
            KPIs and Key Metrics:
            {json.dumps(kpis)}
            
            Advanced Analysis:
            {json.dumps(advanced_analysis)}
            
            Please provide:
            1. A clear, actionable answer to the question
            2. Supporting statistics and insights
            3. Confidence level (0-1) in your analysis
            4. Recommendations based on the findings
            
            Format your response as JSON with the following structure:
            {{
                "answer": "Your detailed answer here",
                "confidence": 0.85,
                "supporting_data": {{
                    "key_statistics": {{}},
                    "trends": [],
                    "insights": []
                }},
                "recommendations": ["recommendation 1", "recommendation 2"]
            }}
            """
            
            # Get response from AI client
            response = await ai_client.insights_response(question, data_summary, max_tokens=1500, temperature=0.3)
            
            # Parse response
            content = response["content"]
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis_result = {
                    "answer": content,
                    "confidence": 0.7,
                    "supporting_data": {"key_statistics": {}, "trends": [], "insights": []},
                    "recommendations": []
                }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
            raise
    
    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare a summary of the dataframe for analysis."""
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset has {len(df)} rows and {len(df.columns)} columns")
        summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # Data types
        summary_parts.append(f"Data types: {dict(df.dtypes)}")
        
        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary_parts.append("Numeric columns statistics:")
            for col in numeric_cols:
                stats = df[col].describe()
                summary_parts.append(f"  {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")
        
        # Sample data
        summary_parts.append("Sample data (first 3 rows):")
        summary_parts.append(df.head(3).to_string())
        
        return "\n".join(summary_parts)
    
    def _determine_insight_type(self, question: str, analysis_result: Dict[str, Any]) -> InsightType:
        """Determine the type of insight based on the question and analysis."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['trend', 'over time', 'growth', 'decline']):
            return InsightType.TREND
        elif any(word in question_lower for word in ['correlation', 'relationship', 'connection']):
            return InsightType.CORRELATION
        elif any(word in question_lower for word in ['outlier', 'anomaly', 'unusual']):
            return InsightType.OUTLIER
        elif any(word in question_lower for word in ['forecast', 'predict', 'future']):
            return InsightType.FORECAST
        elif any(word in question_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return InsightType.COMPARISON
        elif any(word in question_lower for word in ['pattern', 'cycle', 'seasonal']):
            return InsightType.PATTERN
        else:
            return InsightType.SUMMARY
    
    def _generate_visualization_data(self, df: pd.DataFrame, viz_type: str, analysis_result: Dict[str, Any], advanced_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for visualizations with advanced chart types."""
        try:
            viz_data = {
                "type": viz_type,
                "data": {},
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {"display": True},
                        "tooltip": {"enabled": True}
                    }
                }
            }
            
            if viz_type == "line_chart":
                # Generate time series data
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    viz_data["data"] = {
                        "labels": df.index.tolist(),
                        "datasets": [{"label": col, "data": df[col].tolist(), "borderColor": f"rgb({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)})", "fill": False} for col in numeric_cols[:5]]
                    }
                    
            elif viz_type == "bar_chart":
                # Generate bar chart data
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    col = categorical_cols[0]
                    value_counts = df[col].value_counts().head(10)
                    viz_data["data"] = {
                        "labels": value_counts.index.tolist(),
                        "datasets": [{"label": col, "data": value_counts.values.tolist(), "backgroundColor": f"rgba({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)},0.8)"}]
                    }
                    
            elif viz_type == "pie_chart":
                # Generate pie chart data
                categorical_cols = df.select_dtypes(include=['object']).columns
                if len(categorical_cols) > 0:
                    col = categorical_cols[0]
                    value_counts = df[col].value_counts().head(8)
                    colors = [f"rgb({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)})" for _ in range(len(value_counts))]
                    viz_data["data"] = {
                        "labels": value_counts.index.tolist(),
                        "datasets": [{"data": value_counts.values.tolist(), "backgroundColor": colors}]
                    }
                    
            elif viz_type == "scatter_plot":
                # Generate scatter plot data
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    viz_data["data"] = {
                        "datasets": [{"label": f"{numeric_cols[0]} vs {numeric_cols[1]}", "data": [{"x": x, "y": y} for x, y in zip(df[numeric_cols[0]], df[numeric_cols[1]])], "backgroundColor": f"rgba({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)},0.6)"}]
                    }
                    
            elif viz_type == "heatmap":
                # Generate correlation heatmap
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    viz_data["data"] = {
                        "labels": numeric_cols.tolist(),
                        "datasets": [{"label": "Correlation", "data": corr_matrix.values.tolist()}]
                    }
                    
            elif viz_type == "table":
                # Generate table data
                viz_data["data"] = {
                    "headers": df.columns.tolist(),
                    "rows": df.head(20).values.tolist(),
                    "total_rows": len(df)
                }
                
            elif viz_type == "kpi_dashboard":
                # Generate KPI dashboard data
                kpis = analysis_result.get('supporting_data', {}).get('kpis', {})
                viz_data["data"] = {
                    "kpis": kpis.get('potential_kpis', []),
                    "summary_stats": kpis.get('summary_stats', {}),
                    "column_types": {
                        "numeric": kpis.get('numeric_columns', []),
                        "categorical": kpis.get('categorical_columns', []),
                        "date": kpis.get('date_columns', [])
                    }
                }
                
            elif viz_type == "regression_plot":
                # Generate regression visualization
                if 'regression' in advanced_analysis:
                    reg_data = advanced_analysis['regression']
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        viz_data["data"] = {
                            "actual": df[numeric_cols[-1]].tolist(),
                            "predicted": reg_data.get('predictions', []),
                            "r_squared": reg_data.get('r_squared', 0),
                            "coefficients": reg_data.get('coefficients', [])
                        }
                        
            elif viz_type == "clustering_plot":
                # Generate clustering visualization
                if 'clustering' in advanced_analysis:
                    cluster_data = advanced_analysis['clustering']
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        viz_data["data"] = {
                            "x": df[numeric_cols[0]].tolist(),
                            "y": df[numeric_cols[1]].tolist(),
                            "clusters": cluster_data.get('cluster_labels', []),
                            "centers": cluster_data.get('cluster_centers', [])
                }
            
            return viz_data
            
        except Exception as e:
            logger.error(f"Error generating visualization data: {str(e)}")
            return None 
    
    def auto_detect_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Automatically detect KPIs and key metrics from the dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with detected KPIs and metrics
        """
        try:
            kpis = {
                "numeric_columns": [],
                "categorical_columns": [],
                "date_columns": [],
                "potential_kpis": [],
                "summary_stats": {}
            }
            
            # Detect column types
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    kpis["numeric_columns"].append(col)
                    # Calculate basic stats
                    kpis["summary_stats"][col] = {
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "std": float(df[col].std()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "sum": float(df[col].sum())
                    }
                elif df[col].dtype == 'object':
                    kpis["categorical_columns"].append(col)
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    kpis["date_columns"].append(col)
            
            # Detect potential KPIs based on column names and patterns
            kpi_keywords = ['revenue', 'sales', 'profit', 'cost', 'margin', 'growth', 'rate', 'percentage', 'ratio']
            for col in kpis["numeric_columns"]:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in kpi_keywords):
                    kpis["potential_kpis"].append({
                        "column": col,
                        "type": "financial" if any(word in col_lower for word in ['revenue', 'sales', 'profit', 'cost']) else "metric",
                        "current_value": float(df[col].iloc[-1]) if len(df) > 0 else 0,
                        "trend": "increasing" if len(df) > 1 and df[col].iloc[-1] > df[col].iloc[-2] else "decreasing"
                    })
            
            return kpis
            
        except Exception as e:
            logger.error(f"Error detecting KPIs: {str(e)}")
            return {}
    
    def perform_advanced_analysis(self, df: pd.DataFrame, analysis_type: str) -> Dict[str, Any]:
        """
        Perform advanced statistical analysis on the data.
        
        Args:
            df: DataFrame to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary with analysis results
        """
        try:
            results = {}
            
            if analysis_type == "regression":
                # Simple linear regression analysis
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    X = df[numeric_cols[:-1]].values
                    y = df[numeric_cols[-1]].values
                    
                    if len(X.shape) == 1:
                        X = X.reshape(-1, 1)
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    results["regression"] = {
                        "coefficients": model.coef_.tolist(),
                        "intercept": float(model.intercept_),
                        "r_squared": float(model.score(X, y)),
                        "predictions": model.predict(X).tolist()
                    }
            
            elif analysis_type == "clustering":
                # K-means clustering
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    X = df[numeric_cols].values
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    kmeans = KMeans(n_clusters=min(3, len(X)), random_state=42)
                    clusters = kmeans.fit_predict(X_scaled)
                    
                    results["clustering"] = {
                        "cluster_centers": kmeans.cluster_centers_.tolist(),
                        "cluster_labels": clusters.tolist(),
                        "inertia": float(kmeans.inertia_),
                        "n_clusters": len(kmeans.cluster_centers_)
                    }
            
            elif analysis_type == "forecasting":
                # Simple time series forecasting
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0 and len(df) > 5:
                    col = numeric_cols[0]
                    values = df[col].values
                    
                    # Simple moving average forecast
                    window = min(3, len(values) // 2)
                    if window > 0:
                        ma_forecast = np.convolve(values, np.ones(window)/window, mode='valid')
                        trend = np.polyfit(range(len(values)), values, 1)
                        
                        results["forecasting"] = {
                            "moving_average": ma_forecast.tolist(),
                            "trend_coefficients": trend.tolist(),
                            "next_prediction": float(values[-1] + trend[0]),
                            "confidence_interval": [float(values[-1] * 0.9), float(values[-1] * 1.1)]
                        }
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing advanced analysis: {str(e)}")
            return {} 