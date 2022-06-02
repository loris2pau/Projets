from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os,sys
# from client_secure import *
from converter import convert_ui
convert_ui("chat.ui")
from chat import *
import socket

def affiche(txt):
    print(txt)

class chatsnap(QWidget,Ui_fenetre):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(parent)
        # self.pushButton.setText("test");
        self.pushButton_2.clicked.connect(self.envoie)
    def envoie(self):
        # if self.thread.ouvert:
            entree=self.lineEdit.text()
            self.thread.connexion.send(self.thread.chiffrement.chiffre(entree))
            print(entree)
            self.ajout(entree,"(vous)")
            self.lineEdit.clear()
            self.ajout("discution fermée → message non envoyé","/!\ ")
        # else:
        #     self.lineEdit.clear()

    def ajout(self,message,personne=""):
        self.listWidget.addItem(f"{personne} {message}")
        # print(f"{message} → ajouté({personne})")
def lancement_fenetre(args):
    a=QApplication(args)
    f=QWidget()
    c=chatsnap(f)
    f.show()
    r=a.exec_()
    return r,c


if __name__=="__main__":
    chat=lancement_fenetre(sys.argv)[1]

# print ("Fermeture de la connexion ")

