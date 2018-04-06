# taillessmag
A small search engine. Made with Flask and SQLite, uses Page Rank.

## Build the database
The website database is not included. You need to run the web spider to have the database in order to run the search engine.

To initialize the database, run init.py. You'll be asked to give the initial URL to be in the database. If the initialization fails, remove the database file generated and start over.

Then, run scrap.py. A 2-day session will give you a ~6GB database but it may run so slow that most browsers will timeout. A ~400MB database is enough for demonstration purposes.

## Running
website.py contains the Flask application that handles the website. use it as a standard Flask application.

## Algorithm
The ranking algorithm is the one from http://dpk.io/pagerank.
