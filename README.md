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
  


