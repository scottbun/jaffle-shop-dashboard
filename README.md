## Jaffle Shop Dashboard
Streamlit dashboard for Jaffle Shop sales data (2019).

The dashboard is created using Python/Streamlit and fetches data from a Supabase PostgreSQL database. The application is deployed to the Streamlit Community Cloud and is available through the following link: https://jaffle-shop-dashboard-umsnssiqwf3tzacprmmzfq.streamlit.app/

The data is loaded and transformed using a dbt + PostgreSQL workflow. See https://github.com/scottbun/jaffle-shop-dbt for details.  
The raw data was generated using: https://github.com/dbt-labs/jaffle-shop-generator

## Local deployment
To run the application locally you need a PostgreSQL database with data in the expected format. 

Install the requirements, create a `.env` file where you specify the database URL, and start the application with the command
```bash
streamlit run app.py
```
