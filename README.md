# Overview of execution algorithm design

Typically, an execution algorithm has three layers:

- The macrotrader: This highest level layer decides how to slice the order: when
the algorithm should trade, in what size and for roughly how
long.
-   The microtrader: Given a slice of the order to trade (a child order), this level
decides whether to place market or limit orders and at what
price level(s)
- The smart order router: Given a limit or market order, which venue should this order be
sent to?
  
# TO READ: 

- [Market impact models and optimal execution algorithms](https://www.imperial.ac.uk/media/imperial-college/research-centres-and-groups/cfm-imperial-institute-of-quantitative-finance/events/Lillo-Imperial-Lecture3.pdf)

- [Optimal execution strategies in limit order books with general shape functions](https://arxiv.org/abs/0708.1756)
  
- [Three models of market impact](https://mfe.baruch.cuny.edu/wp-content/uploads/2017/05/Chicago2016OptimalExecution.pdf)