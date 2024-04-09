from flask import Flask, request, render_template, jsonify
import csv

from flask_cors import CORS
from scraper import get_stocks_and_scrape
from scraper import get_stock_and_scrape


app = Flask(__name__)
CORS(app)
count = 0
progress = 0

def search_stock(ticker):
    with open('stocks.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['ticker'] == ticker:
                return row
        return None

@app.route('/')
def index():
    return render_template('stocks.html')

@app.route('/refresh')
def refresh():
    stocks = list_all_tickers()
    get_stocks_and_scrape(stocks)
    return ''

@app.route('/update_progress', methods=['POST'])
def update_progress():
    global progress
    # Update progress value based on the POST request data
    progress = request.json['progress']
    return 'Progress updated successfully', 200

@app.route('/retrieve_progress', methods=['GET'])
def retrieve_progress():
    global progress
    return jsonify({'progress': progress}), 200

@app.route('/available_stocks')
def available_stocks():
    available_stocks = list_all_tickers()
    return jsonify(available_stocks)

def list_all_tickers():
    tickers = []
    with open('stocks.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tickers.append(row['ticker'])
    return tickers

@app.route('/search')
def search():
    global count
    ticker = request.args.get('ticker', '').strip()
    if not ticker:
        return 'Please provide a ticker symbol.'
    
    stock_info = search_stock(ticker)
    if stock_info:
        return render_template('stock_info.html', stock=stock_info)
    else:
        if count == 0:
            count += 1
            get_stock_and_scrape(ticker)
            return 'Searching for stock information. Please refresh the page after a moment.'
        else:
            return 'We tried searching, but no luck. The stock may not be available.'
        
@app.route('/clear_csv', methods=['POST'])
def clear_csv():
    try:
        # Open the CSV file in read mode
        with open('stocks.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Read the first line (column headers)
            first_line = next(reader)
        
        # Open the CSV file in write mode to clear its contents
        with open('stocks.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write back the first line (column headers)
            writer.writerow(first_line)
        
        return 'CSV file cleared successfully', 200
    except Exception as e:
        return f'Error clearing CSV file: {e}', 500

if __name__ == '__main__':
    app.run(debug=True)
