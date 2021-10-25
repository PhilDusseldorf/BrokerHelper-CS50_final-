
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from datamanager import deleteDatabase, setFilePath, autogenContainer, createList, createTables, insertCSV, createListHistory


# TODO just for development;
# This line has to be removed when compiling the final app
Window.size = (300, 500)


class StartScreen(Screen):
    pass


class ConScreen(Screen):
    pass


class LoadCSVScreen(Screen):
    pass


class HistoryScreen(Screen):
    pass


class DepotScreen(Screen):
    pass


# Manager
sm = ScreenManager()

dialog = None

class Brokerhelper(MDApp):
    
    def fileSelect(self, *args):
        filePath = args[1][0]
        setFilePath(filePath)

    def autogenerate_container(self, *args):
        global dialog
        dialog.text = "Generating containers. Please wait."
        autogenContainer()
        dialog.dismiss(force=True)


    def delete_database(self, *args):
        global dialog
        dialog.text = "Deleting database. Please wait."
        deleteDatabase()
        dialog.dismiss(force=True)


    def btnCancel(self, *args):
        global dialog
        dialog.dismiss(force=True)


    def startAutogenDialog(self):
        global dialog
        dialog = MDDialog(
            text="Autogenerate containers?",
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color,
                    on_release=self.btnCancel
                ),
                MDFlatButton(
                    text="GENERATE", text_color=self.theme_cls.primary_color,
                    on_release=self.autogenerate_container
                ),
            ]
        )
        dialog.open()

    def startDeletionDialog(self):
        global dialog
        dialog = MDDialog(
            text="Clear database completely?",
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color,
                    on_release=self.btnCancel
                ),
                MDFlatButton(
                    text="DELETE", text_color=self.theme_cls.primary_color,
                    on_release=self.delete_database
                ),
            ]
        )
        dialog.open()

    def change_screen(self, screen):
        sm.current = screen

    def btn_insertCSV(self):
        insertCSV()

    def load_screen(self, screen):
        global sm
        if not sm.has_screen(screen):
            checkScreenName(screen)
        else:
            self.refresh(screen)
        self.change_screen(screen)

    def refresh(self, screen):
        global sm
        # print("AT START: Screen_names: ", sm.screen_names, " | Screen to remove: ", screen, " | Current_screen: ", sm.current_screen.name)
        sm.remove_widget(sm.get_screen(screen))
        # print("AFTER REMOVING: Screen_names: ", sm.screen_names, " | Screen to remove: ", screen, " | Current_screen: ", sm.current_screen.name)
        if not sm.has_screen(screen):
            checkScreenName(screen)
        # print("AFTER ADDING: Screen_names: ", sm.screen_names, " | Screen to remove: ", screen, " | Current_screen: ", sm.current_screen.name)
        self.change_screen(screen)


    def build(self):
        # changes color theme to green
        self.theme_cls.primary_palette = "Green"
        # load the apps kv-file
        self.root = Builder.load_file("screens.kv")

        # screenManager without transition-effects
        sm.transition = NoTransition()

        # The Screens without extra widgets
        loadCSVScreen = LoadCSVScreen()
        startScreen = StartScreen()

        # add all screens(pages) to the screenmanager
        sm.add_widget(startScreen)
        sm.add_widget(loadCSVScreen)

        return sm


createTables()


def checkScreenName(screen):
    if screen == "conScreen":
        smContainer()
    if screen == "depot":
        smDepot()
    if screen == "history":
        smHistory()
    if screen == "start":
        startScreen = StartScreen()
        sm.add_widget(startScreen)
    if screen == "loadCSV":
        loadCSVScreen = LoadCSVScreen()
        sm.add_widget(loadCSVScreen)


def smContainer():
    global sm
    container = createContainer()
    # make a new conScreen
    conScreen = ConScreen()
    # create container from container list
    for i in container:
        conScreen.ids.container.add_widget(ThreeLineListItem(text=f"{(i[1])[:10] + '..' if len(i[1]) > 12 else i[1]} | {i[7] if i[4] != 0 else i[6]} | Profit: {'aktiv' if i[4] == 0 else round(i[5] - i[3], 2)} €", secondary_text=f"[b]Buy[/b] Amount: {i[2]} | Value: {i[3]}", tertiary_text=f"[b]Sell[/b] Amount: {i[4]} | Value: {i[5]}"))
    sm.add_widget(conScreen)


def smHistory():
    global sm
    table_history = createHistory()
    historyScreen = HistoryScreen()
    # add the table to the screen
    historyScreen.add_widget(table_history)
    sm.add_widget(historyScreen)


def smDepot():
    global sm
    depot = createDepot()
    depotScreen = DepotScreen()
    # add depot to depotScreen
    depotScreen.add_widget(depot)
    sm.add_widget(depotScreen)


def createContainer():
    conList = createList("createContainer")
    allContainers = []
    for i in range(len(conList) + 1):
        newContainer = [0, None, 0, 0, 0, 0, None, None]
        for item in conList:
            if i == item[1]:
                newContainer = [item[1], item[2], newContainer[2] + item[3], newContainer[3] + item[4], newContainer[4] + item[5], newContainer[5] + item[6], item[7], item[8]]
        if newContainer[1] is not None:
            allContainers.append(newContainer)
    return allContainers


def createDepot():
    listItems = createList("createDepot")
    depotList = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                            size_hint=(0.9, 0.6),
                            use_pagination=True,
                            rows_num=20,
                            column_data=[
                                ("[size=15]Product[/size]", dp(20)),
                                ("[size=15]Amount[/size]", dp(15))
                            ],
                            row_data=listItems)
    return depotList


def createHistory():
    list_history = formatListHistory(createListHistory())
    # create the history table
    table_history = MDDataTable(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                size_hint=(0.9, 0.6),
                                use_pagination=True,
                                rows_num=20,
                                column_data=[
                                    ("[size=12]Date[/size]", dp(12)),
                                    ("[size=12]Name[/size]", dp(15)),
                                    ("[size=12]Action[/size]", dp(10)),
                                    ("[size=12]€[/size]", dp(10))
                                ],
                                row_data=list_history)
    return table_history


def formatListHistory(listHis):
    '''This function changes the fontsize of every item and adds decimals to amount'''
    # create a newList to store all the changed items
    newList = []
    for row in listHis:
        itemList = []
        for item in row:
            # make item to string
            itemStr = str(item)
            # check if it is the name-item of the row
            if item == row[1]:
                # then cut it if it is too long
                if len(itemStr) > 12:
                    itemStr = itemStr[:10] + '..'
            # check if it is the last item of the row
            if item == row[-1]:
                # then add missing decimal place
                index = itemStr.find('.')
                if index != -1:
                    if index == len(itemStr) - 2:
                        itemStr += "0"
            # add the new fontsize and store it to itemList
            newItem = "[size=10]"+itemStr+"[/size]"
            itemList.append(newItem)
        # convert the itemList into tuple then add it to newList
        newList.append(tuple(itemList))
    return newList


if __name__ == '__main__':
    Brokerhelper().run()
