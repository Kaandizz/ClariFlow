from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from ..services.insight_service import InsightService
from ..models.insights import (
    InsightQuery, InsightResponse, DataSourceList, DataSourceType
)
from ..utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)
router = APIRouter()

# Initialize service
insight_service = InsightService()

@router.post("/insights/query", response_model=InsightResponse)
async def generate_insight(query: InsightQuery):
    """
    Generate business insights from data using natural language queries.
    
    This endpoint accepts a natural language question and data source,
    then uses AI to analyze the data and provide actionable insights.
    
    Example:
    - Question: "What are the sales trends over the last quarter?"
    - Data Source: "sales_data.csv"
    - Returns: Analysis with trends, recommendations, and visualization data
    """
    try:
        logger.info(f"Generating insight for question: {query.question[:50]}...")
        
        # Validate data source exists
        if query.data_source_type in [DataSourceType.CSV, DataSourceType.EXCEL]:
            # Check if file exists in uploads directory
            import os
            file_path = f"uploads/{query.data_source}"
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Data source '{query.data_source}' not found. Please upload the file first."
                )
        
        # Generate insight
        response = await insight_service.generate_insight(query)
        
        logger.info(f"Insight generated successfully with confidence: {response.confidence_score}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insight: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insight: {str(e)}"
        )

@router.get("/insights/data-sources", response_model=DataSourceList)
async def get_data_sources():
    """
    Get list of available data sources for analysis.
    
    Returns information about CSV, Excel, and other data files
    that can be used for business insights.
    """
    try:
        logger.info("Getting available data sources")
        
        data_sources = await insight_service.get_available_data_sources()
        
        logger.info(f"Found {data_sources.total_count} data sources")
        return data_sources
        
    except Exception as e:
        logger.error(f"Error getting data sources: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get data sources: {str(e)}"
        )

@router.get("/insights/supported-formats")
async def get_supported_formats():
    """
    Get list of supported data formats for analysis.
    
    Returns information about file types and formats that can be analyzed.
    """
    try:
        supported_formats = {
            "file_types": [
                {
                    "extension": ".csv",
                    "name": "Comma-Separated Values",
                    "description": "Tabular data in CSV format",
                    "max_size_mb": 50
                },
                {
                    "extension": ".xlsx",
                    "name": "Excel Spreadsheet",
                    "description": "Microsoft Excel files",
                    "max_size_mb": 50
                },
                {
                    "extension": ".xls",
                    "name": "Excel Legacy",
                    "description": "Legacy Excel format",
                    "max_size_mb": 50
                }
            ],
            "data_sources": [
                {
                    "type": "database",
                    "name": "Database Connection",
                    "description": "Direct database connections (coming soon)",
                    "status": "planned"
                },
                {
                    "type": "api",
                    "name": "API Integration",
                    "description": "External API data sources (coming soon)",
                    "status": "planned"
                },
                {
                    "type": "dashboard",
                    "name": "Dashboard Integration",
                    "description": "Connect to business dashboards (coming soon)",
                    "status": "planned"
                }
            ]
        }
        
        return supported_formats
        
    except Exception as e:
        logger.error(f"Error getting supported formats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported formats: {str(e)}"
        )

@router.get("/insights/analysis-types")
async def get_analysis_types():
    """
    Get list of available analysis types and their descriptions.
    
    Returns information about different types of business insights
    that can be generated.
    """
    try:
        analysis_types = {
            "trend": {
                "name": "Trend Analysis",
                "description": "Identify patterns and trends over time",
                "examples": [
                    "Sales growth over the last 6 months",
                    "Customer acquisition trends",
                    "Revenue patterns by quarter"
                ],
                "keywords": ["trend", "growth", "over time", "pattern", "increase", "decrease"]
            },
            "correlation": {
                "name": "Correlation Analysis",
                "description": "Find relationships between different variables",
                "examples": [
                    "Correlation between marketing spend and sales",
                    "Relationship between customer satisfaction and retention",
                    "Impact of pricing on demand"
                ],
                "keywords": ["correlation", "relationship", "connection", "impact", "effect"]
            },
            "outlier": {
                "name": "Outlier Detection",
                "description": "Identify unusual data points or anomalies",
                "examples": [
                    "Unusual sales spikes or drops",
                    "Anomalous customer behavior",
                    "Outlier transactions"
                ],
                "keywords": ["outlier", "anomaly", "unusual", "unexpected", "spike", "drop"]
            },
            "forecast": {
                "name": "Forecasting",
                "description": "Predict future trends and values",
                "examples": [
                    "Sales forecast for next quarter",
                    "Customer growth prediction",
                    "Revenue projection"
                ],
                "keywords": ["forecast", "predict", "future", "projection", "estimate"]
            },
            "comparison": {
                "name": "Comparative Analysis",
                "description": "Compare different groups, periods, or categories",
                "examples": [
                    "Sales comparison between regions",
                    "Performance comparison by product",
                    "Year-over-year growth analysis"
                ],
                "keywords": ["compare", "versus", "vs", "difference", "better", "worse"]
            },
            "summary": {
                "name": "Data Summary",
                "description": "Generate comprehensive data overview",
                "examples": [
                    "Overall business performance summary",
                    "Key metrics overview",
                    "Data quality assessment"
                ],
                "keywords": ["summary", "overview", "summary", "total", "average"]
            },
            "regression": {
                "name": "Regression Analysis",
                "description": "Statistical modeling and prediction",
                "examples": [
                    "Predict sales based on marketing spend",
                    "Model customer lifetime value",
                    "Forecast demand using historical data"
                ],
                "keywords": ["regression", "model", "predict", "relationship", "coefficient"]
            },
            "clustering": {
                "name": "Clustering Analysis",
                "description": "Group similar data points together",
                "examples": [
                    "Customer segmentation",
                    "Product categorization",
                    "Market segment identification"
                ],
                "keywords": ["cluster", "segment", "group", "category", "classification"]
            }
        }
        
        return analysis_types
        
    except Exception as e:
        logger.error(f"Error getting analysis types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis types: {str(e)}"
        )

@router.post("/insights/detect-kpis")
async def detect_kpis(data_source: str, data_source_type: DataSourceType):
    """
    Automatically detect KPIs and key metrics from a data source.
    
    Returns automatically identified KPIs, metrics, and data insights.
    """
    try:
        logger.info(f"Detecting KPIs for data source: {data_source}")
        
        # Load data
        df = await insight_service._load_data_source(data_source, data_source_type)
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Data source '{data_source}' not found or could not be loaded."
            )
        
        # Detect KPIs
        kpis = insight_service.auto_detect_kpis(df)
        
        logger.info(f"KPI detection completed for {data_source}")
        return {
            "data_source": data_source,
            "kpis": kpis,
            "detected_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting KPIs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect KPIs: {str(e)}"
        )

@router.post("/insights/advanced-analysis")
async def perform_advanced_analysis(
    data_source: str, 
    data_source_type: DataSourceType,
    analysis_type: str
):
    """
    Perform advanced statistical analysis on data.
    
    Supported analysis types: regression, clustering, forecasting
    """
    try:
        logger.info(f"Performing {analysis_type} analysis on {data_source}")
        
        # Load data
        df = await insight_service._load_data_source(data_source, data_source_type)
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Data source '{data_source}' not found or could not be loaded."
            )
        
        # Perform analysis
        results = insight_service.perform_advanced_analysis(df, analysis_type)
        
        logger.info(f"Advanced analysis completed for {data_source}")
        return {
            "data_source": data_source,
            "analysis_type": analysis_type,
            "results": results,
            "completed_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing advanced analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform advanced analysis: {str(e)}"
        )

@router.get("/insights/health")
async def insights_health_check():
    """
    Health check endpoint for insights service.
    
    Verifies that the insights service is working properly
    and can connect to required dependencies.
    """
    try:
        # Check if OpenAI is accessible
        import openai
        client = openai.OpenAI(api_key=insight_service.client.api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        # Check if pandas is available
        import pandas as pd
        
        health_status = {
            "status": "healthy",
            "services": {
                "openai": "connected",
                "pandas": "available",
                "data_processing": "ready"
            },
            "timestamp": insight_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "What time is it?"}],
                max_tokens=10
            ).choices[0].message.content
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Insights health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Insights service unhealthy: {str(e)}"
        ) 