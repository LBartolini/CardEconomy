from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang.builder import  Builder

import socket
import threading
from datetime import datetime
import time

ip = '52.203.130.214'
port = 3000

class MyBoxLayout(BoxLayout):
    pass

Builder.load_string('''

<MyMDLabel>:
    theme_text_color: "Error"
    font_style: "H6"
    halign: "center"

<TransactionItem>:
    cols: 3
    size_hint_y: 0.2

    MyMdLabel:
        id: label_importo

    MyMdLabel:
        id: label_data

    MyMdLabel:
        id: label_descrizione

''')

class MyMdLabel(MDLabel):
    pass

class TransactionItem(GridLayout):
    def __init__(self, descrizione, importo, data, **kwargs):
        super().__init__(**kwargs)
        self.ids.label_descrizione.text = descrizione
        self.ids.label_importo.text = f"{importo} $"
        self.ids.label_data.text = data

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = "Dark"
        super().__init__(**kwargs)
        self.connectToServer()
        self.counter_item_transaction = 3
        self.transInList = []

    def connectToServer(self):
        print("Connecting...")
        try:
            sock.connect((ip, port))
            print("Connected!")
        except OSError:
            exit()


    def build(self):
        self.window = Builder.load_file('main.kv')
        self.refresh()
        return self.window

    def on_start(self, **kwargs):
        self.window.ids.spesa.state = "down"

    def refresh(self):
        sock.send(f"refresh".encode())
        data = sock.recv(5000).decode()
        data = data.split("|")
        data.pop() # drop last cause always empty
        saldo = data.pop(0)
        n = data.pop(0)

        for item in self.transInList:
            self.window.ids.list_transazioni.remove_widget(item)

        self.transInList = [] # CLEAR
        self.counter_item_transaction = 0 # CLEAR

        for _ in range(int(n)):
            trans = [] # empty transaction
            if data.pop(1) == '+': # drop operazione
                trans = data[:3]
                trans[0] = '+' + trans[0]
            else:
                trans = data[:3]
                trans[0] = '-' + trans[0]

            for _ in range(3):
                data.pop(0) #TO DROP ITEMS  ALREADY TAKEN

            #[{'id': 2, 'importo': 107.78, 'operazione': '+', 'data': '20/02/20', 'descrizione': 'sync Excel DB', 'saldoAttuale': 107.78}]

            tmp = TransactionItem(trans[2], trans[0], trans[1])
            self.transInList.append(tmp)

        for i in range(len(self.transInList), 0, -1):
            j = i - 1
            self.counter_item_transaction += 1
            self.window.ids.list_transazioni.add_widget(self.transInList[j], index=0) # descrizione importo data

        self.window.ids.label_saldo.text = saldo + ' $'

    def load_old(self):
        sock.send(f"loadOlder{self.counter_item_transaction}".encode())
        data = sock.recv(5000).decode()
        data = data.split("|")
        n = data.pop(0) # drop numbers of transaction received

        toAdd = []

        for _ in range(int(n)):
            trans = [] # empty transaction
            if data.pop(1) == '+': # drop operazione
                trans = data[:3]
                trans[0] = '+' + trans[0]
            else:
                trans = data[:3]
                trans[0] = '-' + trans[0]

            for _ in range(3):
                data.pop(0) #TO DROP ITEMS  ALREADY TAKEN

            tmp = TransactionItem(trans[2], trans[0], trans[1])
            toAdd.append(tmp)

        for i in range(len(toAdd), 0, -1):
            j = i - 1
            self.window.ids.list_transazioni.add_widget(toAdd[j], index=0)
            self.transInList.append(toAdd[j])
            self.counter_item_transaction += 1

    def upload_transazione(self):
        if self.window.ids.text_importo.text != "" and self.window.ids.text_descrizione.text != "":
            try:
                float(self.window.ids.text_importo.text)
                ok = True
            except:
                ok = False

            if ok:
                if self.window.ids.spesa.active:
                    operazione = '-'
                else:
                    operazione = '+'

                now = datetime.now()
                data = now.strftime("%d")+"/"+now.strftime("%m")+"/"+now.strftime("%y")

                sock.send(f"upload{self.window.ids.text_importo.text}|{operazione}|{data}|{self.window.ids.text_descrizione.text}".encode())

            #CLEAR
            self.window.ids.spesa.state = "down"
            self.window.ids.ricarica.state = "normal"
            self.window.ids.text_importo.text = ""
            self.window.ids.text_descrizione.text = ""

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    MainApp().run()
