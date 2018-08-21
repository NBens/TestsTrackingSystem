# TestsTrackingSystem

### Platform for analysing & tracking NetBSD tests results
### A Google Summer of Code 2018 Project


# Milestones:

* Create and test a database schema (suitable for multiple architectures, and later migration to Kuya)
* Create a tool to read the ATF xml data and insert it into a database
* Create a web site providing basic browsing/search options for the database
* Enhance the upload tool (or create a second variant) for Kuya output
* Document the database schema, web site setup, and tool created.

## Database Schema:

![DB Schema](https://raw.githubusercontent.com/NBens/TestsTrackingSystem/master/initial.png)


## Installation:

### Requirements:

* Python 3.5 or higher
* PostgreSQL 10

#### Step 1: Install Python Modules:

To install the required modules, run the command:
``` pip install -r requirements.txt ```

#### Step 2: Setting the database up:

First of all, create a database:

``` psql -U (POSTGRESQL_USERNAME) 
CREATE DATABASE (DATABASE_NAME);
```

Then connect to the database:
``` \c (DATABASE_NAME) ```

Then run the sql file which contains tables creation queries:
``` \i (PATH_TO_-DB_SQL.sql-_FILE) ```

And that should create the tables and their relations in your postgreql server,
You could also use one command to do the same thing:

``` psql -U USERNAME -d DATABASE_NAME -a -f DB_SQL.sql_FILE_PATH ```

## Configuration:

Open config.py file, and edit the database information.

## Usage:

``` push -f (FILE_PATH: XML or DB files only) ```



