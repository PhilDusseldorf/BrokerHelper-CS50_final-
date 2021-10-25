import csv
import sqlite3
from sqlite3 import Error

# global vars
NullTuple = (0, 0, "Verkauf", "ausgefÃ¼hrt", "empty", 0, 0, "00.00.0000", "00:00:00", 0)
filePath = ""


def setFilePath(path):
    '''Sets the filePath for the CSV'''
    global filePath
    filePath = path
    print("Set path to: ", filePath)


def createListHistory():
    '''App-function to create the list for the user's history to load into table later'''
    return __databaseAction(r"trades.db", "createHistory")


def insertCSV():
    '''App-function to insert a specific CSV into the db'''
    __databaseAction(r"trades.db", "insertCSV")


def createTables():
    '''App-function to create tables'''
    __databaseAction(r"trades.db", None)


def createList(listName):
    '''App-function to create a specific list'''
    return __databaseAction(r"trades.db", listName)


def createNewContainer():
    '''Create a new Container'''


def autogenContainer():
    '''Automatically sort existing data into containers'''
    __databaseAction(r"trades.db", "autogenCon")


def deleteDatabase():
    '''Completely deletes all tables in database'''
    __databaseAction(r"trades.db", "delTables")

def __databaseAction(db, action):
    """make a connection to SQL database and execute an action"""
    connection = None
    output = None
    try:
        # first try to connect
        connection = sqlite3.connect(db)
        # if possible create the necessary tables if they do not exist yet
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS `product` (`id` INTEGER PRIMARY KEY, `isin` VARCHAR(45) NOT NULL UNIQUE, `product_name` VARCHAR(45) NOT NULL, `product_type` VARCHAR(45) NOT NULL);')
        cursor.execute('CREATE TABLE IF NOT EXISTS `history` (`id` INTEGER PRIMARY KEY, `order_number` VARCHAR(24) NOT NULL UNIQUE, `direction` VARCHAR(45) NOT NULL, `order_status` VARCHAR(45) NOT NULL, `trading_place` VARCHAR(45) NOT NULL, `count` FLOAT NOT NULL, `price` FLOAT NOT NULL, `date` VARCHAR(10) NOT NULL, `time` VARCHAR(8) NOT NULL, `product_id` INTEGER NOT NULL, FOREIGN KEY (`product_id`) REFERENCES `product` (`id`));')
        cursor.execute('CREATE TABLE IF NOT EXISTS `container` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `container_number` INTEGER NOT NULL, `buy` INTEGER, `sell` INTEGER, FOREIGN KEY (`buy`) REFERENCES `history` (`id`), FOREIGN KEY (`sell`) REFERENCES `history` (`id`));')
        # adds the Null Sell Item if needed
        __addNullSellItem(cursor)
        # then execute a specific action
        output = __chooseAction(connection, cursor, action)
    except Error as error:
        print("Failed to load database ", error)
    finally:
        if connection:
            connection.close()
        return output


def __chooseAction(connection, cursor, action):
    '''Chooses the correct action and triggers it'''
    if action == "insertCSV":
        if __checkCSV(filePath):
            __readCSVintoDB(filePath, cursor, connection)
            connection.commit()
        return None
    if action == "createHistory":
        list_history = __createHistoryList(cursor)
        return list_history
    if action == "createDepot":
        list_depot = __createDepotList(cursor)
        return list_depot
    if action == "createContainer":
        list_con = __createContainerList(cursor)
        return list_con
    if action == "autogenCon":
        __sortContainer(cursor, connection)
        connection.commit()
        return None
    if action == "delTables":
        __deleteTables(cursor)
        connection.commit()
        return None
    else:
        print(sqlite3.version)
        return None

def __deleteTables(cursor):
    cursor.execute('DROP TABLE IF EXISTS container;')
    cursor.execute('DROP TABLE IF EXISTS products;')
    cursor.execute('DROP TABLE IF EXISTS history;')
    print("dropped tables")


def __calculateConNumber(cursor):
    '''Calculates a container number that does not exist yet'''
    cursor.execute('SELECT container_number FROM container;')
    con_count = cursor.fetchall()
    # create a con_list with all container numbers
    con_list = []
    for i in con_count:
        con_list.append(i[0])
    x = 0
    con_num = 0
    # find a not yet used container number
    while True:
        if x not in con_list:
            con_num = x
            break
        x += 1
    return con_num


def __insertCon(cursor, connection, buyItem, sellItem, con_number):
    '''Insert the data into the container table'''
    # get the count of the rows to have a unique new container
    # con_number = __calculateConNumber(cursor)
    # start query to insert this new container to container table
    query = '''INSERT INTO container (container_number, buy, sell) VALUES (?, ?, ?);'''
    cursor.execute(query, (con_number, buyItem[0], sellItem[0]))
    connection.commit()


def __clearList(list_usedBuy, list_buy):
    for idUsed in list_usedBuy:
        for item in list_buy:
            if idUsed == item[0]:
                list_buy.remove(item)
                break
    list_usedBuy.clear()


def __sortContainer(cursor, connection):
    '''get all data in a list, sort it and store it in the databases' container table'''
    # id at [0], product at [1], isin at [2], count at [3], money at [4], date at [5]
    # make the buy list
    list_buy = []
    cursor.execute('SELECT history.id AS id, product_name AS product, isin, count, count * price AS money, date FROM history JOIN product ON product.id = history.product_id WHERE direction = "Kauf" AND order_status = "ausgefÃ¼hrt" AND history.id NOT IN (SELECT DISTINCT buy FROM container WHERE buy NOT NULL) ORDER BY isin ASC;')
    list_buy = cursor.fetchall()
    # Make the sell list
    list_sell = []
    cursor.execute('SELECT history.id AS id, product_name AS product, isin, count, count * price AS money, date FROM history JOIN product ON product.id = history.product_id WHERE direction = "Verkauf" AND order_status = "ausgefÃ¼hrt" AND history.id NOT IN (SELECT DISTINCT sell FROM container WHERE sell NOT NULL) ORDER BY isin ASC;')
    list_sell = cursor.fetchall()
    # create a list to store the already used buy items
    list_usedBuy = []

    __clearList(list_usedBuy, list_buy)

    # go threw all buy items to find the single value combinations for a container
    # print("Start making 1:1 containers!")
    for buyItem in list_buy:
        # go threw every sell item
        for sellItem in list_sell:
            isSellFound = False
            # print("Check: ", buyItem[2], " == ", sellItem[2], " AND ", buyItem[3], " == ", sellItem[3])
            # see if there is a sell item that matches the buy item's name and amount
            if buyItem[2] == sellItem[2] and buyItem[3] == sellItem[3]:
                __insertCon(cursor, connection, buyItem, sellItem, __calculateConNumber(cursor))
                # remove the sell item from list
                list_sell.remove(sellItem)
                # store the buy item in the store list for already used buy items
                list_usedBuy.append(buyItem[0])
                isSellFound = True
                # print("one to one: ", len(list_sell))
            # stop search for one buy item if one sell was found
            if isSellFound:
                break

    # clear list_buy from used items
    __clearList(list_usedBuy, list_buy)

    # get all unique isins from list_buy in a new list
    list_isin = []
    for item in list_buy:
        isin = item[2]
        if isin not in list_isin:
            list_isin.append(isin)
    # print("list isin length: ", len(list_isin))

    # go threw all left buyItems to build containers with unique isin
    # print("Start making n:m isin containers!")
    for isin in list_isin:
        con_number = __calculateConNumber(cursor)
        # print("isin: ", isin)
        for buyItem in list_buy:
            seller = None
            # print("buyItem: ", buyItem[2])
            if buyItem[2] == isin:
                # check if a sell item matches the isin, then store it in table
                for sellItem in list_sell:
                    if sellItem[2] == isin:
                        seller = sellItem
                        list_sell.remove(sellItem)
                        # print("Stored item with seller. List_sell length: ", len(list_sell))
                        __insertCon(cursor, connection, buyItem, seller, con_number)

                # if there is no matching sell item just store the buyItem's data in table
                if seller is None:
                    seller = NullTuple
                    __insertCon(cursor, connection, buyItem, seller, con_number)
                    # print("Stored item without seller.")
                list_usedBuy.append(buyItem[0])
        __clearList(list_usedBuy, list_buy)


def __createContainerList(cursor):
    '''create the list for the container'''
    list_con = []
    cursor.execute('SELECT container.id as ID, container_number, buyprod.product_name as Product, buys.count as BuyAmount, buys.count * buys.price as BuyPrice, sells.count as SellAmount, sells.count * sells.price as SellPrice, buys.date as BuyDate, sells.date as SellDate FROM container JOIN history as buys on buys.id = container.buy JOIN history as sells on sells.id = container.sell JOIN product as buyprod on buys.product_id = buyprod.id GROUP BY container.id;')
    list_con = cursor.fetchall()
    return list_con


def __createDepotList(cursor):
    '''create the list for the current depot'''
    # Make the buy list
    list_buy = []
    cursor.execute('SELECT product_id, product_name, SUM(count) FROM product JOIN history ON product.id = history.product_id WHERE direction = "Kauf" AND order_status = "ausgefÃ¼hrt" GROUP BY isin ORDER BY product_id ASC;')
    list_buy = cursor.fetchall()
    # Make the sell list
    list_sell = []
    cursor.execute('SELECT product_id, product_name, SUM(count) FROM product JOIN history ON product.id = history.product_id WHERE direction = "Verkauf" AND order_status = "ausgefÃ¼hrt" GROUP BY isin ORDER BY product_id ASC;')
    list_sell = cursor.fetchall()
    # Create list that has subtracted sell from buy, stored in a tuple
    list_final = []
    for buyItem in list_buy:
        for sellItem in list_sell:
            if buyItem[0] == sellItem[0]:
                tupleItem = (buyItem[1], round(buyItem[2] - sellItem[2], 4))
                if tupleItem[1] != 0:
                    list_final.append(tupleItem)
    return list_final


def __createHistoryList(cursor):
    '''creates the list under the hood'''
    listhis = []
    cursor.execute('SELECT date, product_name, direction, round((history.count * history.price),2) AS Amount FROM product JOIN history ON product.id = history.product_id WHERE order_status = "ausgefÃ¼hrt" ORDER BY date DESC, time DESC;')
    listhis = cursor.fetchall()
    return listhis


def __checkCSV(filename):
    print("in Check: ", filename)
    print("Strings ending: ", filename[-4:])
    if filename[-4:] == '.csv':
        print("True!!!")
        return True
    else:
        return False


def __readCSVintoDB(csv_file, cursor, connection):
    """reads a CSV-file and stores it in db if it not already exists"""
    print("Filepath to open: ", csv_file)
    with open(csv_file, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', doublequote=True)
        # skip header
        next(csvfile)
        # read all rows of csv and store them in database if does not already exist
        for row in reader:
            # Insertion tuples
            tupleInsertProduct = (row[3], row[4], row[5])
            tupleInsertHistory = __createTupleInsertHistory(cursor, row)

            # get productID
            cursor.execute('SELECT id FROM product WHERE isin = ?', [row[3]])
            productID = cursor.fetchone()

            # see if ISIN is already in table and insert data
            if productID is None:
                productID = ()
            if len(productID) == 1:
                # if ISIN was in table, just add other information into history
                # print("ISIN was in table")
                __insertToHistoryTable(tupleInsertHistory, cursor)
            else:
                # if ISIN wasn't in table, insert into products and history table
                # print("ISIN wasn't in table")
                query = '''INSERT INTO product (isin, product_name, product_type) VALUES (?, ?, ?);'''
                cursor.execute(query, tupleInsertProduct)
                connection.commit()
                # update the tuple, then insert into table
                tupleInsertHistory = __createTupleInsertHistory(cursor, row)
                __insertToHistoryTable(tupleInsertHistory, cursor)


def __insertToHistoryTable(tupleInsertHistory, cursor):
    '''This function inserts the correct values into the histoty table'''
    cursor.execute('SELECT order_number FROM history WHERE order_number = ?;', [tupleInsertHistory[0]])
    order_number = cursor.fetchone()

    # here I have to check if I get an empty object
    if order_number is None:
        order_number = ()
    # here I check if the object was in the table already
    if len(order_number) == 1:
        # if it was in table, nothing happens
        pass
    else:
        # if it wasn't in table, the row gets inserted into the table
        query = '''INSERT INTO history (order_number, direction, order_status, trading_place, count, price, date, time, product_id) VALUES (?,?,?,?,?,?,?,?,?);'''
        cursor.execute(query, tupleInsertHistory)


def __addNullSellItem(cursor):
    '''This function creates a NullItem that is a blanco tuple for sells'''
    cursor.execute('INSERT OR IGNORE INTO history VALUES (0, 0, "Verkauf", "ausgefÃ¼hrt", "empty", 0, 0, "00.00.0000", "00:00:00", 0);')


def __createTupleInsertHistory(cursor, row):
    '''This function creates the history tuple with the correct productID'''
    cursor.execute('SELECT id FROM product WHERE isin = ?', [row[3]])
    productID = cursor.fetchone()
    if productID is None:
        productID = (0,)

    # Prepare the comma-separated floats to dot-separated
    count = prepareInput(row[11])
    price = prepareInput(row[12])

    tupleInsertHistory = (row[0], row[8], row[9], row[6], count, price, row[14], row[15], productID[0])
    return tupleInsertHistory


def prepareInput(input):
    stringList = list(input)
    if '.' in stringList:
        stringList[stringList.index('.')] = ''
    if ',' in stringList:
        stringList[stringList.index(',')] = '.'
    string = ''.join([str(x) for x in stringList])
    return string
