#chiffrement assymétrique
#on a choisi de coder ces fonctions à la main et non
#de réutiliser celles du module cryptography préalablement
#sélectionné car il y avait sans cesses des erreurs lors de
#l'installation de ce module et de la récupération des
#différentes informations.
#
#
#si cela apparaît encore c'est que l'algorithme n'est pas fiable à 100% :
#certaines fois le cryptage décryptage fonctionne parfaitement et d'autres
#fois des erreurs se glissent... Peut-être des nombres trop gros ?
#NOOOON : en fait le chiffrement n'est plus bijectif si n<255=3*5*17 alors,
#pour empêcher cela, la liste des nombres premiers commence à 17.
#
#
#enfin, petite réflexion : d'après l'article
#www.commentcamarche.net/contents/208-algorithme-de-chiffrement-rsa,
#pour facoriser un enier de 768 bits soit un nombre supérieur à 10**231
#au maximum, il a fallu plus de deux ans et demi  et plus de 10**20 calculs
#à l'INRIA pour réussir à le factoriser.
#dans notre cas, le plus grand nombre n que l'on peut produire est
#1051*1049=1 102 499 pour rester dans la limite du domaine de la table ASCII

from random import randint
class Assymetrique:
    """classe représentant un système de chiffrement ASsymétrique
    ATTRIBUTS :
     - p : premier nombre premier à choisir (soi-m^me ou aléatoirement)
     - q : deuxième nombre premier à choisir (soi-m^me ou aléatoirement)
     - n : p*q doit être inférieur à 1 114 112 limite des codes ASCII)
     - M : (p-1)*(q-1)
     - publique : clé publique (à faire passer au serveur pour qu'il chiffre la clé symétrique
     -privee : clé privée (pour déchiffrer l'information venue du serveur)
     +++++++++++++++
     MÉTHODES :
     - genere_cle_publique() : cherche 4 nombres e premiers et en séletionne un au hasard avec M et renvoie le tuple (e,n)
     - genere_cle_privee() : cherche le premier entier d tel que d*e congru à 1 [M]
     - chiffre(message) : chiffre le message passé en paramètre
     - dechiffre(message) : déchiffre le message passé en paramètre
     +++++++++++++++
     SOURCES pour la generation des clés :
     https://jpq.pagesperso-orange.fr/divers/rsa/rsa.pdf
     """

    def __init__(self,p=None,q=None):
        """constructeur de la classe Assymetrique,
        prend en paramètre deux nombres premiers et génère les clés publique et privée asociée
        ou si les entiers ne sont pas renseignés ou pas premiers, ils sont générés aléatoirement"""
        if p==None or q==None or not(est_premier(p)) or not(est_premier(q)):
            liste_premiers=nbr_premiers()
            #print("les indices de la liste vont de 0 à ",len(liste_premiers)-1)
            if p==None:
                ind_p=randint(0,len(liste_premiers)-1)#on choisit aléatoirement l'indice du nombre p parmi les indices de la liste de nombre premiers
                #print("indice de p= ",ind_p)
                p=liste_premiers[ind_p]
                liste_premiers.remove(p)#on enlève p pour éviter de le rechoisir
            if q==None:
                if p in liste_premiers:
                    liste_premiers.remove(p)#on enlève p de la liste mais on verifie qu'il y est sinon erreur
                ind_q=randint(0,len(liste_premiers)-1)#on choisit aléatoirement l'indice du nombre q parmi les indices de la liste de nombre premiers
                #print("indice de q= ",ind_q)
                q=liste_premiers[ind_q]
        #on affecte les valeurs dont on a besoin pour calculer les clés aux attributs p, q, n, M
        self.p=p
        self.q=q
        #print(f"p={p} et q ={q}")
        self.n=self.p*self.q
        self.M=(self.p-1)*(self.q-1)
        #on genere les clés
        self.publique=self.genere_cle_publique()
        #print("cle_publique ok")
        self.privee=self.genere_cle_privee()
        #print("cle privee ok")



    def genere_cle_publique(self):
        e=5#e ne peut être qu'impair
        j=e+2#on essaie donc tous les nombres impairs de 7 à 6*M exclu
        b=True # et on s'arrête au 3ème e trouvé mais on pourrait continuer
        i=0
        e_possibles=[]
        while b and j<6*self.M:
            #print("j= ",j)
            i1=self.M#on applique l'algorithme d'euclide à (p-1)(q-1) et j
            j1=j
            k=i1%j1
            while k>1:
                k=i1%j1
                i1=j1
                j1=k
                #print("k= ",k)
            if k==0:
                j+=2#k=0 ça ne va pas
            else:
                i+=1
                e_possibles.append(j)
                j=j+2
                #print(e_possibles)
                if i==4:
                    b=False
        if b:
            print("pas de e dans l'intervalle [7;3M[")
        else:
            #print(e_possibles)
            #e=e_possibles[randint(0,len(e_possibles)-1)]#cle publique semi-aléatoire
            e=e_possibles[-1]
            #print(e)
        return (int(e),self.n)

    def genere_cle_privee(self):
        """recherche le premier entier d =k*M+1 divisible par e"""
        i=1
        e=self.publique[0]
        while i%e!=0:
            i=i+self.M
        d=i/e
        return (int(d),self.n)

    def chiffre(self,message):
        """prend un message en paramètre et le retourne chiffré"""
        #print("+++++on chiffre+++++")
        e=self.publique[0]
        n=self.n
        message_code=""
        for lettre in message:
            code_lettre=(ord(lettre)**e)%n
            #print(f"code {lettre} = {code_lettre}")
            #print(f"{ord(lettre)}->{code_lettre}")
            message_code+=chr(int(code_lettre))
        return message_code

    def dechiffre(self,message_code):
        """prend un message chiffré en paramètre et le retorne déchiffré"""
        #print("+++++on déchiffre+++++")
        d=self.privee[0]
        n=self.n
        message_en_clair=""
        for lettre in message_code:
            decode_lettre=(ord(lettre)**d)%n
            #print(f"decode {lettre} = {decode_lettre} ")
            #print(f"{ord(lettre)}->{decode_lettre}")
            message_en_clair+=chr(decode_lettre)
        return message_en_clair



def chiffre_avec_cle_pb(cle_pb,message):
    """connaissant une clé publique, on code le message entré en paramètre"""
    e=cle_pb[0]
    n=cle_pb[1]
    rep=""
    for lettre in message:
        code_lettre=(ord(lettre)**e)%n
        lettre_codee=chr(code_lettre)
        rep+=lettre_codee
    return rep





def nbr_premiers(n=1052):
    """prend en paramètre un nombre entier n et retourne la liste des nombres_premiers infèrieurs à n
    ici n est utilisé avec la valeur 1052 car sinon on sort du domaine de définition de la table ASCII"""
    l=[]
    for i in range(17,n,2):#2on avance de 2 en 2 car les nombres premiers sont tous impairs
        if est_premier(i):
            l.append(i)
    return l

def est_premier(n):
    """vérifie si le nombre entier passé en paramètre est premier, True si oui False sinon"""
    for i in range(2,n):
        if n%i==0:
            return False
    return True
##
if __name__=='__main__':
    chiffrement=Assymetrique()
    print(chiffrement.publique)
    print(chiffrement.privee)
    print(f"p={chiffrement.p} et q={chiffrement.q}")
    messages=["bonjour le monde","moi je vais très bien","EEEEETTTTT toi ?","ééééé"]
    for message in messages:
        code=chiffrement.chiffre(message)
        decode=chiffrement.dechiffre(code)
        assert(len(message)==len(code)and len(message)==len(decode))
        print(message,decode)
    #assert message==decode
