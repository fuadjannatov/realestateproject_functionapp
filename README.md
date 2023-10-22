# Baku Real Estate Market Analysis

The repository contains Baku Real Estate Market Analysis project, explaining the current real estate market trends, price dynamics and areas with the highest PPSM (Price Per Square Meter). The data is scrapped from one of the most popular real estate selling websites.
The project gathers ads of aparments for both on sale and rent.

## Technologies
[![My Skills](https://skillicons.dev/icons?i=python,azure,mysql,vscode,git)](https://skillicons.dev)


## The project flow
* Timer triggered script at  Azure Function App
* Generates 10 links for scraping
* Scrapes, cleans and prepares the collected data using bs4, regex and pandas accordingly
* Authenticates with Azure SQL server, inserts collected data points row by row

## Power BI Dashboard collects the data from Azure SQL server
* The report has 2 dashboards: for apartments on sale (page 1) and for rent (page 2)
* <img src="https://i.postimg.cc/bv5vvjJy/PBI.png" width="700" height="400" alt="Power BI Dashboard">
* [Link to the dashboard](https://app.powerbi.com/view?r=eyJrIjoiNTc5MjJiNmUtZWJmMC00NTNmLTgyZmQtMjNkNTkxYzU3MzM3IiwidCI6Ijg2NzI4NzZhLWMwNWYtNDVhMC1iN2Y5LTgxMjRiN2JjZjU0YSIsImMiOjl9)

## Contributing
Contributions are welcome! Please follow our [contribution guidelines](CONTRIBUTING.md).
