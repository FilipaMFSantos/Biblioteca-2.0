# Biblioteca 2.0

### Interactive Book Discovery Platform built with Python and Streamlit

An interactive web application that allows users to discover, explore
and analyse books through an intuitive interface and interactive
visualizations.

Developed as part of the **Data Analysis and Visualization** course of
the **Master's in Data Science Applied to Social Sciences** (University
of Aveiro).

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas)
![Apache ECharts](https://img.shields.io/badge/Apache-ECharts-orange)
![PyDeck](https://img.shields.io/badge/PyDeck-Maps-success)

------------------------------------------------------------------------

# Project Overview

Biblioteca 2.0 is an interactive digital library built with **Python**
and **Streamlit**.

Users can:

-   Search books by title, author or ISBN
-   Browse books by genre
-   Discover the most popular books
-   Find hidden gems
-   Explore interactive visualizations
-   Locate Portuguese public libraries through OpenStreetMap
-   Compare purchase options from online bookstores

The application combines data exploration with modern visualization
techniques to provide an engaging reading discovery experience.

------------------------------------------------------------------------

# Features

  Feature             Description
  ------------------- ---------------------------------------------
  Smart Search        Search by title, author or ISBN
  Genre Explorer      Browse books by literary genre
  Popular Books       Ranking of the most popular books
  Hidden Gems         Highly rated books with fewer reviews
  Insights & Trends   Interactive ECharts visualizations
  Library Map         Portuguese public libraries (OpenStreetMap)
  External Links      Goodreads, Wook, Bertrand and Fnac

------------------------------------------------------------------------

# Dataset

The original application was developed using the **Goodreads 100k Books
Dataset**.

To keep this repository lightweight and easy to clone, this public
version includes a representative subset of approximately **20,000
books**.

This reduction preserves every application feature while significantly
reducing repository size.

------------------------------------------------------------------------

# Technologies

-   Python
-   Streamlit
-   Pandas
-   Apache ECharts
-   PyDeck
-   OpenStreetMap (Overpass API)

------------------------------------------------------------------------

# Project Structure

``` text
Biblioteca-2.0/
│
├── app.py
├── requirements.txt
├── GoodReads_20k_books.csv
├── source/
│   ├── data.py
│   └── functions.py
├── notebook/
│   └── Biblioteca.ipynb
└── README.md
```

------------------------------------------------------------------------

# Installation

``` bash
git clone https://github.com/<your-user>/biblioteca-2.0.git

cd biblioteca-2.0

pip install -r requirements.txt

streamlit run app.py
```

------------------------------------------------------------------------

# Future Improvements

-   Book recommendation engine
-   User accounts
-   Reading lists
-   Machine learning recommendations
-   Library availability search

------------------------------------------------------------------------

# Author

**Filipa Santos**

Master's in Data Science Applied to Social Sciences

University of Aveiro

Finance • Data Analytics • Business Intelligence

GitHub: https://github.com/`<your-user>`{=html}

------------------------------------------------------------------------

## License

This project was developed for academic purposes as part of the Master's
programme at the University of Aveiro.
