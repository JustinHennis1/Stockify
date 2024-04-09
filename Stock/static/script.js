     
        document.addEventListener('DOMContentLoaded', function() {
            

            const availableStocksTable = document.getElementById('availableStocksTable');
            availableStocksTable.addEventListener('click', function(event) {
                const clickedElement = event.target;
                if (clickedElement.tagName === 'TD') {
                    const ticker = clickedElement.textContent.trim();
                    if (ticker) {
                        retrieveStockInfo(ticker);
                       
                    }
                }
            });
        });


        const form = document.getElementById('tickerForm');
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const ticker = document.getElementById('tickerInput').value.trim();
            await retrieveStockInfo(ticker);
        });
    
        async function retrieveStockInfo(ticker) {
            if (ticker) {
                const response = await fetch(`/search?ticker=${ticker}`);
                const data = await response.text();
                document.getElementById('stockInfo').innerHTML = data;
                await updateAvailableStocks();
                
                hideLoadingIndicator();
            } else {
                alert('Please enter a valid ticker symbol.');
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('clearButton').addEventListener('click', function() {
                clearCSVFile();
            });
        });
        
        function clearCSVFile() {
            fetch('/clear_csv', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error clearing CSV file');
                }
                console.log('CSV file cleared successfully.');
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        

    
        async function displayAvailableStocks() {
            const response = await fetch('/available_stocks');
            const data = await response.json();
            const availableStocksBody = document.getElementById('availableStocksBody');
           
            availableStocksBody.innerHTML = ''; // Clear existing content
            let row = document.createElement('tr');
            let count = 0;
            data.forEach(stock => {
                if (count >= 15) {
                    availableStocksBody.appendChild(row);
                    row = document.createElement('tr');
                    count = 0;
                }
                const cell = document.createElement('td');
                cell.textContent = stock;
                row.appendChild(cell);
                count++;
            });
            availableStocksBody.appendChild(row); // Append the last row if it's not already added
        }
    
        async function updateAvailableStocks() {
            await displayAvailableStocks();
        }
    
        async function getNewWatchlistData() {
            await fetch('/refresh');
            await updateAvailableStocks();
        }

        // Function to call getNewWatchlistData and set up the timeout to call it again after 2 minutes
        function updateWatchlistPeriodically() {
            getNewWatchlistData(); // Call the function initially when the page loads

            // Set up a timeout to call the function again after 2 minutes (120,000 milliseconds)
            setTimeout(function() {
                updateWatchlistPeriodically(); // Call the function again after 2 minutes
            }, 600000); // 10 minutes in milliseconds
        }

        // Call the function to start the periodic updates when the page loads
        window.addEventListener('load', function() {
            updateWatchlistPeriodically();
        });


        function showLoadingIndicator() {
            document.getElementById('loadingOverlay').style.display = 'block';
        }


        // Function to hide the loading overlay
        function hideLoadingIndicator() {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
        
        async function retrieveProgress() {
            try {
                const response = await fetch('/retrieve_progress', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (!response.ok) {
                    throw new Error('Failed to retrieve progress');
                }
                const data = await response.json();
                console.log('Progress:', data.progress);
                showLoadingIndicator();
                document.getElementById('loadingOverlay').innerText = `Loading Data... ${data.progress}%`;
        
                if (data.progress === 100) {
                    clearInterval(progressInterval); // Stop retrieving progress once it reaches 100%
                    hideLoadingIndicator(); // Hide loading indicator when progress is complete
                }
        
            } catch (error) {
                console.error('Error retrieving progress:', error);
            }
        }
        
        // Call retrieveProgress function periodically or upon user request
        const progressInterval = setInterval(retrieveProgress, 5000); // Example: Retrieve progress every 5 seconds
        
        
    
        displayAvailableStocks(); // Call the function to display available stocks when the page loads
    