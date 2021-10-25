# Brokerhelper

#### Video Demo: [LINK TO YOUTUBE](https://youtu.be/rQTsMa52rlk)

#### Description:

My final project for CS50 2021. A mobile app that helps me organize my trading.
I am now able to load my trades from my broker (justtrade) as a CSV file and load it into the apps database.
I can automatically create containers that combine buys and sells into a "trade" so I can see how much profit it made.

In the future there can be so much more functions but for now the app works well for me.

The programm is coded with python and uses the kivy(md) framework for the GUI.
To manage data in the database I use SQLite.

I have four screens. The first screen is the start screen. There is only a welcome message and the skull-icon at the bottom. The skull is for dropping the tables from the apps database. Later there can be statistics and diagrams on this screen but that would be too much work at this point.

The second screen is the loadCSVScreen. There you can load any properly formatef CSV into the BrokerHelper. The App automatically adds every new item from the csv that is not already in the database. So no duplicates are possible.

The third screen is the depot. There you can see the the current active values by name and amount. Later I want to manually delete things from the depot.

The fourth screen is the history. The history is created from the database and shows all buys and sells in €.

The fifth and last screen is the container screen. It can generate containers by clicking on the little brick in the bottom right. Containers are first created by combining all buys and sells with equal amounts. After that the rest of buys and sells are combined in a contianer that is specific to a single product like Bitcoin or special stock. When the containers are created, you have to refresh the screen. Later I want to manually manage the containers.

For the design of the app I used kivyMD. To be honest, the framework was not that great. So if i would make another app with python, I would use another framework. The kivy-file includes all designs and the architecture of the screens.

The database consists of three tables. First there is the product table, second there is the history table, and last there is the container table. The product table stores data to a specific product, may it be crypto currency, stock or derivatives. The history table stores data for every action like sell or buy and holds a reference to the product table. At last there is the container table. It stores data for the container creation and references the history table in two ways: once for the buy items and second for the sell items.

#### Containing Files:

-   CSV-Files(bin): stores the csv-files to execute (later temporarily)
    -   CSVrowNames.txt: just to know which index holds which value
    -   justtrade.csv_small: all data from the broker (testCSV)
-   .gitignore: needed a gitignore because I worked at different PCs and would have to change the settings all the time otherwise
-   brokerhelper.py: Main entry point. All code for creating the app, loading and refreshing screens
-   database_structure.PNG: is a picture of my database and table structure
-   datamanager.py: all functions regarding database querys and csv-files
-   README.md: the readme
-   requirements.txt: necessary libs and extensions to install
-   screens.kv: the kivy file that holds all the designs for the app
-   trades.db: the databank to store the users trades
