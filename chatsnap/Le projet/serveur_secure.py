#definition d'un serveur réseau gérant un système de CHAT simplifié.
#utilise les threads pour gérer les connexions clientes en parallèle.

HOST=''
PORT=17000 #nombre entre 1024 et 65535

import socket,sys,threading,unidecode
from chiffrage_symetrique import *
from chiffrage_assymetrique import *
CHIFFREMENT_SERVEUR=Symetrique()#chiffrement du serveur
class ThreadClient(threading.Thread):
    '''dérivation d'un objet thread pour gérer la connexion avec un client. A chaque client accepté, on associe un thread ce qui va permettre d'interagir avec chacun de façon indépendante
    ATTRIBUTS :
    - connexion : références du client connecté
    - ouvert : booléen True si la relation serveur client est ouverte, false sinon
    - cle_envoyee : true si la cle de chiffrement symetrique est envoyee au cient fallse sinon
    - chiffrement_serveur : objet Symetrique
    - cle_pb_client : recoit la cle publique du client, None au début
    ++++++++++++++++
    MÉTHODES :
    - __init__(conn) : constructeur de la classe ThreadClient
    - run() : la méthode principale de la classe qui fait fonctionner le chat
    - recoit_cle_publique(msgClient) : retire la clé publique du client contenue dans les msgClient passé en paramètre et du type C.P.B.(
    - envoie_cle_symetrique() : envoie la clé de chiffrement symetrique au client et codee avec sa clé publique'''

    def __init__(self,conn):
        """initialise les attributs de la classe"""
        threading.Thread.__init__(self)
        self.connexion=conn#id de la connexion du client
        self.ouvert=True#la liaison est ouverte
        self.cle_envoyee=False#la cle symetrique n'a pas été envoyée
        self.chiffrement_serveur=CHIFFREMENT_SERVEUR#on initialise le chiffrement
        self.cle_pb_client=None#la cle publique du client n'a pas été recue

    def run(self):
        """grosse méthode de la relation serveur client"""
        #dialogue avec le client
        nom=self.getName() #chaque thread possède un nom
        while self.ouvert:#tant que la liaison est ouverte
            msgClient=self.connexion.recv(1024)#je recoit le messsage du client
            if self.cle_pb_client==None:#si je n'ai pas de cle publique client
                msgClient=traduit_en_utf_8(msgClient)#le message que j'ai recu est cette clé publique et je la traduit en utf8
                self.recoit_cle_publique(msgClient)#je la récupère
                #print(self.cle_pb_client)
                self.envoie_cle_symetrique()#et j'envoie ma clé symétrique codee avec la cle publique

            else:#sinon (j'ai recu la clé publique)#les messages recus sont maintenant codés avec ma clé symetrique
                #print(msgClient.upper())
                if self.chiffrement_serveur.dechiffre(msgClient).upper()=='FIN' or self.chiffrement_serveur.dechiffre(msgClient)=="":#si je recoit un message de fin alors je ferme la liaison
                    self.ouvert=False
                if self.ouvert:#si je suis ouvert
                    message=f"{nom}>{self.chiffrement_serveur.dechiffre(msgClient)}"#le message recu est "nom du client>message_code_dechiffré"
                    print(message)#je l'affiche
                #on fait suivre le message à tous les clients (INITALEMENT PUIS AU CLIENT DÉSIRÉ)
                for client in conn_client:
                    if client!=nom:#on ne renvoie pas à l'émetteur
                        conn_client[client].send(self.chiffrement_serveur.chiffre(message))
        #fermeture de la connexion
        self.connexion.close()#coupe la connexion côté serveur
        del conn_client[nom]#supprime l'entrée de la connexion dans le dictionnaire
        print(f"Client {nom} déconnecté")
        #le thread se termine ici

    def recoit_cle_publique(self,msgClient):
        """prend en paramètre un message client de la forme 'C.P.B.(' et modifie l'attribut cle_pb_client par le tuple de la chaine de caractère"""
        assert(msgClient[:7]=='C.P.B.('),"le msgClient n'est pas une clé publique"#je vérifie que je recoit une clé publique
        e=""#j'initialise le e et le n de la cle publique
        virgule_passee=False#variable qui va servir à savoir si on est tjr dans le e ou si on est passé dans le n
        n=""
        for i in range(7,len(msgClient)):#commence à 7 car C.P.B.( au début
            lettre=msgClient[i]
            if lettre==',':#si je passe la virgule
                virgule_passee=True
            if not(virgule_passee) and est_un_chiffre(lettre):#si la virgule n'est pas passée et que ma lettre est aussi un chiffre alors, je suis dans le e et j'ajoute mon chiffre au e
                e+=lettre
            if virgule_passee and est_un_chiffre(lettre):# si la virgule est passée et que ma lettre est un chiffre alors je suis dans le n et j'ajoute ma lettre à n
                n+=lettre
        #print("clé publique =",e,n)
        try :
            e,n=int(e),int(n)
            self.cle_pb_client=(e,n)
            #print("la cle publique est reçue")
        except ValueError :
            print(" e ou n ne peut pas être convertit en entier")

    def envoie_cle_symetrique(self):
        """envoie la cle de chiffrement symetrique au client au format C.C.S.("""
        client=self.getName()#je récupère le nom du client auquel je dois adressé la clé
        cle=traduit_en_utf_8(self.chiffrement_serveur.key)#je la traduit en utf-8
        #print("cle symétrique decodee = ",cle)
        assert(type(self.cle_pb_client)!=None),"la clé publique du client est None"
        cle_codee=chiffre_avec_cle_pb(self.cle_pb_client,cle)#et je la code avec la cle publique du client
        msg_cle_codee="C.C.S.("+cle_codee #j'élabore le message pour que le client sache que ce qui suit est la Clé de Chiffrement Symétrique codee avec la cle publique
        #print("cle symétrique codee envoyée",msg_cle_codee)
        conn_client[client].send(traduit_en_bytes(msg_cle_codee))#j'envoie le message codé et traduit en bytes
        print(f"la clé de chiffrement symétrique a été envoyée au client {client}")


def est_un_chiffre(lettre):
    """renvoie true si la lettre en paramètre est un chiffrre, false sinon"""
    return lettre in ['0','1','2','3','4','5','6','7','8','9']






#initialisation du serveur - mise en place du serveur :
mySocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    mySocket.bind((HOST,PORT))
    mySocket.listen(5)#j'écoute jusqu'à 5 clients
except socket.error :
    print("la liaison du socket à l'adresse choisie a échoué")
    sys.exit()
print("serveur prêt, en attente de requêtes ...")
#attente et prise en charge des connexions demandées par les clients :
conn_client={}#dictionnire des connexions clients
while True:
    connexion,adresse=mySocket.accept()#j'accepte les clients
    #cree un nouvel objet thread pour gérer la connexion
    th=ThreadClient(connexion)
    #mémoriser la connexion dans le dictionnaire
    it=th.getName()
    conn_client[it]=connexion
    print(f"client {it} connecté, adresse IP {adresse[0]}, port {adresse[1]}")
    th.start()



    #connexion.send(bytes(unidecode.unidecode("vous êtes connecté : envoyez vos messages."),'utf-8'))