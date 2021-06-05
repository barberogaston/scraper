# Scraping apartment rentals

Scraping apartment rentals in [**Nueva Córdoba, Córdoba, Argentina.**](https://goo.gl/maps/nYE87CUEyFGnZf8z9)

## Components

This project is composed of various building blocks, each of which is inside its own folder and has its own **Dockerfile**.

### [`/database`](./database)

**MySQL** database where all the scraped data is saved.

### [`/notebooks`](./notebooks)

Folder which contains notebooks for:

- Data cleaning
- Exploratory data analysis
- Modeling

### [`/scraper`](./scraper)

Application written in **Python** that scrapes apartment rental data and saves it to the database.

> **Note:** Since the website from which the data is scraped uses cloudflare and can't currently be scraped, I switched to using `Selenium` temporarly. The downside of this is that it the scraper can't be run with Docker and you'll need to configure the webdriver in your local environment.

## Execution

Since all components are dockerized, the most convenient way to execute any component is by running:

```bash
docker-compose up [component]
```

> **Note:** You should run the **database** container before running both the **scraper** and **notebooks** ones.

## Report

[Report](./notebooks/Report.md) with some plots describing the rentals' data
