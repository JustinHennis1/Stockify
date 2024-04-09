import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
import os
import csv
from selenium.common.exceptions import TimeoutException



def scrape_stock(driver, ticker_symbol):
    # build the URL of the target page
    url = f'https://finance.yahoo.com/quote/{ticker_symbol}'

    # visit the target page
    driver.get(url)

    try:
        # wait up to 3 seconds for the consent modal to show up
        consent_overlay = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.consent-overlay')))

        # click the 'Accept all' button
        accept_all_button = consent_overlay.find_element(By.CSS_SELECTOR, '.accept-all')
        accept_all_button.click()
    except TimeoutException:
        pass

    # initialize the dictionary that will contain
    # the data collected from the target page
    stock = { 'ticker': ticker_symbol }

    # scraping the stock data from the price indicators
    regular_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketPrice"]') \
        .text
    regular_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChange"]') \
        .text
    regular_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')

    post_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketPrice"]') \
        .text
    post_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChange"]') \
        .text
    post_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')

    stock['regular_market_price'] = regular_market_price
    stock['regular_market_change'] = regular_market_change
    stock['regular_market_change_percent'] = regular_market_change_percent
    stock['post_market_price'] = post_market_price
    stock['post_market_change'] = post_market_change
    stock['post_market_change_percent'] = post_market_change_percent

    # scraping the stock data from the "Summary" table
    previous_close = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PREV_CLOSE-value"]').text
    open_value = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="OPEN-value"]').text
    bid = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BID-value"]').text
    ask = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="ASK-value"]').text
    days_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DAYS_RANGE-value"]').text
    week_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="FIFTY_TWO_WK_RANGE-value"]').text
    volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="TD_VOLUME-value"]').text
    avg_volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="AVERAGE_VOLUME_3MONTH-value"]').text
    market_cap = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="MARKET_CAP-value"]').text
    beta = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BETA_5Y-value"]').text
    pe_ratio = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PE_RATIO-value"]').text
    eps = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EPS_RATIO-value"]').text
    earnings_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EARNINGS_DATE-value"]').text
    dividend_yield = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DIVIDEND_AND_YIELD-value"]').text
    ex_dividend_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EX_DIVIDEND_DATE-value"]').text
    year_target_est = driver.find_element(By.CSS_SELECTOR,
                                          '#quote-summary [data-test="ONE_YEAR_TARGET_PRICE-value"]').text

    stock['previous_close'] = previous_close
    stock['open_value'] = open_value
    stock['bid'] = bid
    stock['ask'] = ask
    stock['days_range'] = days_range
    stock['week_range'] = week_range
    stock['volume'] = volume
    stock['avg_volume'] = avg_volume
    stock['market_cap'] = market_cap
    stock['beta'] = beta
    stock['pe_ratio'] = pe_ratio
    stock['eps'] = eps
    stock['earnings_date'] = earnings_date
    stock['dividend_yield'] = dividend_yield
    stock['ex_dividend_date'] = ex_dividend_date
    stock['year_target_est'] = year_target_est

    return stock

def get_stocks_and_scrape(tickers):
    # if len(sys.argv) <= 1:
    #     print('Ticker symbol CLI argument missing!')
    #     sys.exit(2)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--log-level=3')
    print(f'Retrieving stock info...')
    progress = 0
    max = len(tickers)


    # initialize a web driver instance to control a Chrome window
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    # set up the window size of the controlled browser
    driver.set_window_size(1150, 1000)


    # the array containing all scraped data
    stocks = []

    # scraping all market securities

    for ticker_symbol in tickers:
        stocks.append(scrape_stock(driver, ticker_symbol))
        progress += 1
        update_loading_progress(progress,max)
        print(f'{progress} out of {max} stocks scraped')


    
    print(f'Info Retrieved! Closing Driver...')

    # close the browser and free up the resources
    driver.quit()

    # extract the name of the dictionary fields
    # to use it as the header of the output CSV file
    csv_header = stocks[0].keys()

    # Path to the CSV file
    csv_file_path = 'stocks.csv'

    # Check if the CSV file already exists
    # file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode ('a')
    # If the file doesn't exist, it will be created
    with open(csv_file_path, 'w', newline='') as output_file:
        print(f'Adding Financials to CSV...')

        # Initialize a DictWriter object
        dict_writer = csv.DictWriter(output_file, csv_header)
        
        dict_writer.writeheader()

        # Write the data to the CSV file
        dict_writer.writerows(stocks)

def update_loading_progress(progress, total):
    # Calculate progress percentage
    progress_percent = (progress / total) * 100
    
    # Make a POST request to update loading progress
    response = requests.post('http://127.0.0.1:5000/update_progress', json={'progress': progress_percent})
    
    # Check response status code
    if response.status_code != 200:
        raise RuntimeError("Failed to update loading progress")


def get_stock_and_scrape(ticker):
    # if len(sys.argv) <= 1:
    #     print('Ticker symbol CLI argument missing!')
    #     sys.exit(2)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--log-level=3')
    print(f'Retrieving stock info...')

    # initialize a web driver instance to control a Chrome window
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    # set up the window size of the controlled browser
    driver.set_window_size(1150, 1000)

    # the array containing all scraped data
    stocks = []

    # scraping all market securities
    
    stocks.append(scrape_stock(driver, ticker))

    print(f'Info Retrieved! Closing Driver...')

    # close the browser and free up the resources
    driver.quit()

    # extract the name of the dictionary fields
    # to use it as the header of the output CSV file
    csv_header = stocks[0].keys()

    # Path to the CSV file
    csv_file_path = 'stocks.csv'

    # Check if the CSV file already exists
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode ('a')
    # If the file doesn't exist, it will be created
    with open(csv_file_path, 'a', newline='') as output_file:
        # Initialize a DictWriter object
        print(f'Adding Financials to CSV...')

        dict_writer = csv.DictWriter(output_file, csv_header)

        # Write the header only if the file was just created
        if not file_exists:
            dict_writer.writeheader()

        # Write the data to the CSV file
        dict_writer.writerows(stocks)


# if __name__=="__main__":
#     tickers = sys.argv[1:]  # Get tickers from command-line arguments
#     get_stocks_and_scrape(tickers)