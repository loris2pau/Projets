#définition d'un client réseau gérant en parallèle l'émission et la réception des messages (utilisation de 2 THREADS)
HOST='localhost'#adresse du serveur
PORT=17000
import socket,sys,threading,unidecode,time
from chiffrage_symetrique import *
from chiffrage_assymetrique import *
from ath_Chat import *
#chemin_maison='C:/Users/cleme/Bureau/clement/travail/tle/nsi/cours/reseaux/projet'







CHIFFREMENT=Assymetrique()#chiffrement du client
#print(CHIFFREMENT.publique,CHIFFREMENT.privee)#ne PAS DECOMMENTER sinon la clé publique et le clé privee seront affichée


class ThreadReception(threading.Thread):
    """Dérivation d'un objet thread gérant la reception des messages issus du serveur
    ATTRIBUTS :
    - connexion : objet socket permettant de lier le seveur et la partie reception du client
    - ouvert : True si le canal de reception est ouvert False sinon
    - chiffrement : chiffrement du canal de réception
    - symetrique : True si le chiffrement est symetrique, False sinon
    ++++++++++++++
    MÉTHODES :
    - __init__(conn) : constructeur de la classe
    - run() : grosse méthode de la classe qui régit la réception, le déchiffrement et l'affichage des messages recus
    - recupere_cle_symetrique(message_cle_symetrique_codee) : extrait la cle symetrique du serveur depis le message en paramètre
    - change_chiffrement(cle_dechiffree) : change le chiffrement de la partie reception de Assymetrique vers Symetrique
    """

    def __init__(self,conn):
        """initialise les attributs de la classe ThreadReception"""
        threading.Thread.__init__(self)
        self.connexion=conn#recoit le socket permettant de faire communiquer le thread
        self.ouvert=True#le canal de réception est initialement ouvert
        self.chiffrement=CHIFFREMENT#Assymetrique au début
        self.symetrique=(type(self.chiffrement)==Symetrique)#false au début

    def run(self):
        """la grosse méthode qui gère la reception des messages et les affiches"""
        while self.ouvert:#tant que je suis ouvert
            if self.symetrique:#si le chiffrement est symetrique
                assert type(self.chiffrement)==Symetrique,"le chiffrement du client n'est pas symétrique"
                message_recu=self.connexion.recv(1024)#je récupère le message codé en bytes
                message_recu=self.chiffrement.dechiffre(message_recu)#je déchiffre ce message en bytes et il est aussi transformé en utf-8
                print("*"+message_recu+"*")#je l'affiche
                chat.ajout(message_recu)
                if message_recu=='' or message_recu.upper()=='FIN':#si c'est un message de fin alors je me ferme
                    self.ouvert=False
            else:#si mon chiffrement est assymétrique
                message_recu=traduit_en_utf_8(self.connexion.recv(100000000))#je recoit ici la clé symétrique codee précédée de la mention C.C.S.( et je traduit ce message chiffré en utf-8
                #print("message recu par le serveur",message_recu)
                if message_recu[:7]=='C.C.S.(':#je vérifie que je recois bien la C.C.S.(
                    #print("cle chiffree recue=",message_recu)
                    cle_dechiffree=self.recupere_cle_symetrique(message_recu)#je déchiffre la clé contenue dans le message et elle est traduite en bytes
                    self.change_chiffrement(cle_dechiffree)#je change le chiffrement
        #le thread <reception> se termine ici
        #on force la fermeture du thread <émission> :
        self.connexion.close()
        th_E._Thread__stop()
        print("Client arrêté et connexion interrompue")

    def recupere_cle_symetrique(self,message_cle_symetrique_code):
        """déchiffre avec la méthode dechiffre du chiffrement assymetrique, la cle_symetrique_codee envoyee par le serveur"""
        #print("cle symetrique récupérée",message_cle_symetrique_code,"test = ",message_cle_symetrique_code[:7]=='C.C.S.(')
        assert message_cle_symetrique_code[:7]=='C.C.S.(',"le message en paramètre n'est pas une clé de chiffrage symétrique"
        cle_dechiffree=message_cle_symetrique_code[7:]#je sélectionne la clé symétrique en paramètre
        #print(f"message_cle_symetrique_code[7:]={message_cle_symetrique_code[7:]}")#la clé recue et la clé émise par le serveur sont les mêmes
        cle_dechiffree=self.chiffrement.dechiffre(cle_dechiffree)#je decode la cle_symetrique en paramètre
        #print(cle_dechiffree)
        cle_dechiffree=traduit_en_bytes(cle_dechiffree)#je la traduit en bytes car c'est le format d'une clé de fernet
        #print("cle symetrique dechiffrée = ",cle_dechiffree)
        print("cle symetrique reçue")
        return cle_dechiffree#je renvoie la clé déchiffrée


    def change_chiffrement(self,cle_dechiffree):
        """modifie en place les attributs chiffrement et symetrique pour les transformer en chiffrement Symetrique de clé passée en paramètre et en True"""
        cle=cle_dechiffree
        ancien_chiffrement=self.chiffrement
        self.chiffrement=Symetrique(cle)
        nouveau_chiffrement=self.chiffrement
        self.symetrique=(type(self.chiffrement)==Symetrique)
        #print("chiffrement de reception = ",type(self.chiffrement))
        #print("chiffrement reception changé = ",ancien_chiffrement==nouveau_chiffrement)

















class ThreadEmission(threading.Thread):
    """Dérivation d'un objet thread gérant l'émission des messages
    ATTRIBUTS:
    - connexion : recoit le socket permettant d'établir la liaison entre l'émission et le serveur
    - chiffrement : recoit le chifrement du client
    - symetrique : True si le chiffrement du client est symetrique, False sinon
    - ouvert : True si l'émission est ouverte, False sinon
    - envoi_pb : 0 si la cle publique du client est envoyée, 1 si elle est envoyée, 2 quand le chiffrement est changé en symétrique
    ++++++++++++++++
    MÉTHODES :
    - __init__(conn): initialise les attributs de la classe
    - run() : grosse méthode qui régit l'émission des messages (chiffrement + envoi)
    - envoi_cle_publique() : envoi la clé publique du client
    - change_chiffrement(thread_reception) : change le chiffrement du thread émission en chiffrement du hread reception"""
    def __init__(self,conn):
        """initialise les attributs"""
        threading.Thread.__init__(self)
        self.connexion=conn#initialise la connection au seveur
        self.chiffrement=CHIFFREMENT#chiffrement Assymétrique du client
        self.symetrique=(type(self.chiffrement)==Symetrique)#False
        self.ouvert=True#ouvert initialement
        self.envoi_pb=0#la clé pb n'est pas envoyée

    def run(self):
        """régit l'émission de messages"""
        i=0#entier qui va nous servir à savoir à partir de quel moment on peut envoyer nos messages
        while self.ouvert:#tant que l'émission est ouverte
            if self.envoi_pb==1:#si j'ai envoyé ma clé publique, le serveur a renvoyé la clé de chiffrement symetrique à th_R
                #print(f"chiffrement de th_R: {type(th_R.chiffrement)}")
                self.change_chiffrement(th_R)#donc l'émission prend le même chiffrement que la reception
                self.envoi_pb=2#et envoi_pb passe à 2 pour éviter de revenir à l'intérieur de ce if
                #print("self.envoi_pb=2")
            if self.symetrique:# si le chiffrement est symétrique
                if i==0:#si on a tjr pas envoyé de messages
                    print("vous pouvez taper vos messages")
                    i+=1
                message_emis=(input())#je demande un message et j'attends #à rajouter si bugg unidecode.unidecode
                chat.ajout(message_emis,"(vous)>")
                if message_emis=='' or message_emis.upper()=='FIN':#si c'est JE veux finir la conversation
                    self.ouvert=False#je me ferme
                self.connexion.send(self.chiffrement.chiffre(message_emis))#j'envoie le message chiffré au serveur
            else:#si le chiffrement est assymétrique
                if self.envoi_pb==0:#si la clé publique nest pas envoyée
                    self.envoie_cle_publique()#j'envoie ma clé publique
                else:
                    self.change_chiffrement(th_R)#si elle est envoyée, je change de chiffrement
        self.connexion.close()#je suis fermé donc je rompts la connexion
        print("client arrêté et connexion interrompue")#et je l'affiche

    def envoie_cle_publique(self):
        """envoie au serveur la clé publique repérée par C.P.B."""
        e=self.chiffrement.publique[0]
        n=self.chiffrement.publique[1]
        message_emis="C.P.B.("+str(e)+","+str(n)+")"#message caractéristique de la transmission de la clé publique
        self.connexion.send(traduit_en_bytes(message_emis))#à traduire en bytes pour envoyer
        self.envoi_pb=1
        print("le client a envoyé sa clé publique")


    def change_chiffrement(self,thread_reception):
        """modifie en place l'attribut chiffrement du thread emission pour le transformer en même chiffrement que celui du thread reception passé en paramètre"""
        time.sleep(20)#dors 20 secondes pour laisser (LARGEMENT ?) le temps au thred rception de changer son chiffrement
        assert type(thread_reception)==ThreadReception,"le thread en paramètre n'est pas un thread reception"
        #assert type(thread_reception.chiffrement)==Symetrique,"on ne change le chiffrement du client que de Assymetrique à Symetrique"
        #print("chiffrement initial de emission",self.chiffrement)
        self.chiffrement=thread_reception.chiffrement
        #print("chiffrement modifié de emission",self.chiffrement)
        self.symetrique=(type(self.chiffrement)==Symetrique)
        print("chiffrement emission changé")




##



#programme principal- Etablissement de la connexion :
print("ne PAS ENVOYER de messages avant que la mention 'vous pouvez taper votre message' ne soit affichée")
connexion=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#on iniialise l'objet de communication
try :
    connexion.connect((HOST,PORT))#on se connecte à la machine
except socket.error:
    print("la connexion a échoué")
    sys.exit()

print("Connexion établie avec le serveur")
th_E=ThreadEmission(connexion)#on initialise les threads
chat=lancement_fenetre(sys.argv)[1]
chat.thread=th_E
th_R=ThreadReception(connexion)
th_E.start()#et on les démarre
th_R.start()
