# GEMINI.md

## Project Overview

This is a Streamlit application that serves as a multi-page dashboard. The application is built with Python and uses libraries like `pandas`, `plotly`, and `requests`. The main entry point is `app.py`. The application has several pages, each demonstrating a different aspect of Streamlit's capabilities.

- **Bio:** A personal bio page.
- **Visualization:** Interactive charts with widgets.
- **Pie:** A page that displays a pie chart.
- **LiveAPI:** A page that fetches and displays live data from a weather API.
- **CoinGecko:** A page that fetches and displays live cryptocurrency data from the CoinGecko API.
- **Dashboard:** A multi-page dashboard with a custom sidebar and different data views.

## Building and Running

To run this project, you need to have Python and the required libraries installed.

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## Development Conventions

- The application is structured with a main `app.py` file and additional pages in the `pages` directory.
- Data files are stored in the `data` directory.
- Static assets like images are stored in the `assets` directory.
- The code uses f-strings for string formatting.
- Type hints are used in some function definitions.
- The `@st.cache_data` decorator is used to cache data and improve performance.
