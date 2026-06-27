# Biblioteca 2.0

> **An interactive book discovery platform built with Python and
> Streamlit.**

Biblioteca 2.0 is an interactive web application developed as part of
the **Data Analysis and Visualization** course. The project allows users
to explore a large book catalogue through intuitive search tools,
interactive dashboards and modern data visualizations.

The application was designed to demonstrate practical skills in **data
processing, visualization, dashboard development and user experience
design** using Python.

------------------------------------------------------------------------

## Features

### Book Search

-   Search by title
-   Search by author
-   Search by ISBN

### Genre Explorer

-   Browse books by literary genre
-   Interactive filtering
-   Detailed book information

### Popular Books

-   Discover the most popular books based on community ratings.

### Hidden Gems

-   Find highly rated books with relatively few reviews.

### Book Details

Each book page includes:

-   Book cover
-   Description
-   Rating
-   Genres
-   Goodreads link
-   Purchase links (Wook, Bertrand and Fnac)
-   Interactive map of Portuguese public libraries (OpenStreetMap)

### Insights & Trends

Interactive visualizations including:

-   Genre popularity
-   Genre quality comparison
-   Volume vs Rating analysis
-   Popularity vs Rating scatter plot

### User Suggestions

Users can submit suggestions for new books directly from the
application.

------------------------------------------------------------------------

## Dataset

This project is based on the **Goodreads Books Dataset**.

The original implementation was developed using approximately **100,000
books**.

To keep this repository lightweight and easy to reproduce, the public
version includes a **representative subset of approximately 20,000
books**.

This reduction significantly decreases repository size while preserving
the application's functionality and analytical capabilities.

> **Note:** The dataset included in this repository is intended for
> demonstration purposes.

------------------------------------------------------------------------

## Technologies

-   Python
-   Streamlit
-   Pandas
-   Apache ECharts
-   PyDeck
-   OpenStreetMap (Overpass API)

------------------------------------------------------------------------

## Project Structure

``` text
Biblioteca-2.0/
├── app.py
├── requirements.txt
├── Notebook_Biblioteca2.0.ipynb
├── source/
│   ├── __init__.py
│   ├── data.py
│   ├── functions.py
│   └── GoodReads_100k_books.csv
└── README.md
```

------------------------------------------------------------------------

## Installation

``` bash
git clone https://github.com/FilipaMFSantos/Biblioteca-2.0.git
cd Biblioteca-2.0
pip install -r requirements.txt
streamlit run app.py
```

------------------------------------------------------------------------

## Learning Objectives

This project demonstrates practical applications of:

-   Data cleaning and preprocessing
-   Data exploration
-   Interactive dashboards
-   Information visualization
-   Geographic visualization
-   External API integration
-   User interface development
-   Data storytelling

------------------------------------------------------------------------

## Future Improvements

-   Personalized recommendation engine
-   User authentication
-   Personal reading lists
-   Advanced filtering
-   Library availability search
-   Machine Learning recommendations

------------------------------------------------------------------------

## Author

**Filipa Costa**

Master's in Data Science Applied to Social Sciences\
University of Aveiro

GitHub: https://github.com/FilipaMFSantos

------------------------------------------------------------------------

## License

This repository is intended for educational and portfolio purposes.
