# Tasks (for sina):
1. adding inventory check to Mofid interface
2. adding check for order fill (it can be done by checking inventory every time, every time inventory must equal to lastinventory + lastorder, so we need buffer to keep track of last order and inventory.)

# Algorithm For Making OHLCV Data
first of all we need a buffer for storing trade counts and ohlcv data 
we just need to cut, lxml parsed list from :counts
so, here we are, a simple approach is to make buffer from trade counts and just cut list with 
trade counts.


