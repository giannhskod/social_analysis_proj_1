# Social Network Analysis Project 1

## Full-Name: Giannis Kontogeorgos
## Student-Id: P3352807


## *Description*
The project contains 2 python scripts and 2 folders that will be described below.
It should be noted that for the second part the implementation has some extra features
as script arguments or multithreading.

* **hw1-1.py**: The script that covers the implementation of the first questions
 with the Euler graphs and circuits
 
* **hw1-2.py**: The script that covers the implementation of the *Watts-Strogatz* Graphs manipulation
 and metrics calculations.
 
* **plots/**: The folder that contains the plots that are generated from the scripts

* **temporary_grapsh**: The folder that contains the graphs that are saved in order to be loaded afterwards.


## *Instructions*

For the first script just run

  ```bash
  python hw1-1.py
  ```
  
The second script running is configurable. For example

* If you wan to run the script for **100** initial nodes, **10** maximum iterations, *100* extra nodes per iteration
 and **5** maximum minutes for centrality calculation then enter:
    ```bash
    python hw1-2.py -n 100 -i 10 -r 100 -m 300
    ``` 

* If you want to run only for one graph without waiting all the calculations then you can type:
    ```bash
    python hw1-2.py -n 100 -i 1
    ```
* For help type: 
    ```bash
    python hw1-2.py -h
  
    ```
* For default run type:
    ```bash
    python hw1-2.py
    ```
    
