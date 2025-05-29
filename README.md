# Finance Assistant

A multi-source, multi-agent finance assistant that provides real-time market data, financial news, and portfolio analysis.

## Features

- **Real-time Market Data**: Get data from Yahoo Finance, Google Finance, MarketWatch, and Investing.com
- **Financial News**: Scrape news from multiple sources including CNBC, Reuters, Yahoo Finance, and Investing.com
- **Portfolio Analysis**: Analyze portfolio holdings, sector allocation, and performance
- **SEC Filings**: Access company filings and reports
- **Voice Interface**: Speak to the assistant and get voice responses
- **Web Interface**: User-friendly Streamlit interface

## Architecture

The system uses a multi-agent architecture:

- **API Agent**: Handles data retrieval from financial APIs
- **Scraping Agent**: Extracts data from financial websites
- **Analysis Agent**: Processes financial data and generates insights
- **Language Agent**: Handles natural language processing
- **Voice Agent**: Manages speech-to-text and text-to-speech
- **Retriever Agent**: Accesses stored data and documents

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finance-assistant.git
cd finance-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
SEC_API_KEY=your_sec_api_key
HUGGINGFACE_API_KEY=your_huggingface_key
```

### Running the Application

1. Start the application:
```bash
python start.py
```

2. Open the web interface:
Open your browser and navigate to `http://localhost:8501`

## Usage

### Web Interface

The Streamlit interface provides the following features:
- Market overview
- Stock search
- Portfolio analysis
- News feed
- Company filings
- Voice interaction

### API Endpoints

The application also provides API endpoints:
- `/api/market-data`: Get real-time market data
- `/api/news`: Get financial news
- `/api/portfolio`: Analyze portfolio data
- `/api/filings`: Get company filings

## Data Sources

- Yahoo Finance
- Google Finance
- MarketWatch
- Investing.com
- CNBC
- Reuters
- SEC EDGAR

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data provided by various sources
- Built with Python, Streamlit, and various libraries 