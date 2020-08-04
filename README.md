# overview

This repo contains code developed as part of the ESSNet Big Data - Online job vacancies.

Various functionality can be found here:
- code for web-scraping job vacancy counts (spiders based on Python Scrapy or Selenium)
- code for nowcasting job vacancy through time-series modelling
- TODO - code for matching entries based on company name
- TODO - code for location analysis

It is recommended that you read through this readme before using. If something is unclear, there
are more comments in the code.

# installation

* clone this repo
* recommended Python version --> 3.7 (3.6+ for sure)
* install chrome driver (http://chromedriver.chromium.org/downloads)
    * update `PATH` environmental variable so that typing "chromedriver" in terminal works
* use `pipenv` to install dependencies from `Pipfile`. Simply run `pipenv install`
    * if you don't have `pipenv`, install it first (https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv) 
* set PYTHONPATH to contain the root of the project (i.e. the path to the root directory containing e.g. the `scraping` folder)
* if using PyCharm:
    * set the project interpreter to point to the python from the virtual pipenv environment
        * (you can find the path to this Python interpreter by activating the Pipenv shell session -
        when you do this, it prints something like:

    ```shell
    ons21553@ons21553 ~/w/j/polished> pipenv shell
    Launching subshell in virtual environment…
    Welcome to fish, the friendly interactive shell
    Type help for instructions on how to use fish
    ons21553@ons21553 ~/w/j/polished>  source /home/ons21553/.local/share/virtualenvs/polished-pxOk2dlA/bin/activate.fish
    ```

    In my case, the path to Python is then `/home/ons21553/.local/share/virtualenvs/polished-pxOk2dlA/bin/Python`

* set relevant environment variables.
    * e.g. if you want to use Mailjet (https://www.mailjet.com/) to send emails from code
        * `MAILJET_KEY` and `MAILJET_SECRET` need to be set up

# content

### scraping

This contains demos of scrapers that can be extended.

All scrapers in this repo only scrape JV **counts** (number of JVs), i.e. not the details of the vacancies. 
Extensions to scrape other details are possible but the code was designed with focus on JV counts.

The base class for all spiders is `BaseSpider` (which inherits from Scrapy Spider). This 
`BaseSpider` class gives support for running multiple spiders,
retrying the spider's run (e.g. if it errors out) or provides hooks for storing data from the
spider (the scraped count).

The two types of spiders that are in this repo are:
- **Company website spiders** - for scraping JV count from a company websites, e.g. https://www.accenture.com/gb-en/careers/jobsearch.
Here one would create a new class for each new company website from which we want to get the JV count
- **Job board spiders** - for scraping all JV counts from a given job board, e.g. https://www.careerjet.co.uk/.
Here one would create a new class for each job board which, from which we want to get all
company JV counts

The `run.py` script enables you to control the program from command line (e.g. run selected spiders from command line).
It also makes it possible to run spiders in parallel, greatly speeding up the execution.


##### company websites

Simply run the `scraping/company_websites/spiders.py` file to do a demo.

Every company website (CW) spider has a separate Python class named by the company whose website we scrape. 
All of these are in the `spiders.py` file. Each of the spiders inherits from `BaseCwSpider` class, which 
contains code that would otherwise be the same for each of the CW spiders.

##### job boards

Simply run the `scraping/job_board/careerjet.py` file to do a demo (on a Careerjet portal).

Job board spider classes inherit from the `BaseJbSpider` class.


### nowcasting

This contains a jupyter notebook file that demos how nowcasting can be done. Also included are two mock files -
one is representing (mock) job vacancy survey (JVS) data time-series, the other mock online job vacancy data time series.
The latter was derived from the JVS using random perturbations on the data (of different scale for each industry),
including situations when the way OJV approximates JVS suddenly changes.

The jupyter notebook is commented and can be simply opened and run. If you wish to try it on your own datasets,
simply modify the paths/replace the mock files with your own, preserving the format of the data.


# Contacts

Fero Hajnovic - frantisek.hajnovic@ons.gov.uk, fhajnovic.ons@gmail.com