# sports_analytics
This repo has a handful of selenium-based crawlers that scrape data from websites and stores them in a local PostgreSQL database for analysis.
Pipeline follow a simple 3 step pattern:
1. Crawl the source with selenium
2. Parse the data we pulled and transform it into a csv format for easy upload the database
3. Upload csv files to database

Sceduling and automation currently handled by a local Prefect server
