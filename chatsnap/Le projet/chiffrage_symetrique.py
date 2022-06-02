#chiffrement symétrique
#au début, nous voulions utiliser le module pédagogique sympy,
# mais nous avons choisi le module cryptography avec la classe Fernet
#qui permet un chiffrement symétrique très sécurisé de par la complexité des clefs générées.
from cryptography.fernet import Fernet#pour le chiffrement symétrique
import unidecode#pour enlever les accents des messages car source de conflit en passant en bytes

def traduit_en_bytes(message):
    """convertit en bytes le message, auquel on a enlevé les accents, passé en paramètre"""
    return message.encode('utf-8','replace')

def traduit_en_utf_8(message):
    """convertit le message en bytes passé en paramètre en utf-8"""
    return message.decode('utf-8','replace')


def genere_cle_Fernet():
    """génère une clé de chiffrement Fernet (symétrique) """
    return Fernet.generate_key()


class Symetrique:
    """toutes les méhodes nécessaires à un chiffremen symétrique
    paramètres:
    f : un objet fernet
    key : une clé à chiffrement symétrique
    ++++++++++++++++
    méthodes :
    chiffre : prend en paramètre un message en 'utf-8' et renvoie le message chiffré, convertit en bytes, grâce à la clé
    dechiffre : prend en paramètre un message chiffré en bytes et renvoie le message déchiffré en utf-8
    ++++++++++++++++
    Rendre des attributs PRIVÉS ?
    si oui besoin de getters"""
    def __init__(self,key=genere_cle_Fernet()):
        self.f=Fernet(key)
        self.key=key

    def chiffre(self,message):
        return self.f.encrypt(traduit_en_bytes(message))

    def dechiffre(self,message):
        return traduit_en_utf_8(self.f.decrypt(message))



if __name__=='__main__':

    messages=["bonjour le mÉtèôrónâ","je bois de l'eau et de l'eau et encore de l'eau","ç'ést dômmàgè dé dëvóír éñlèvêr les accents"]
    for message in messages:
        symetrique=Symetrique()
        code=symetrique.chiffre(message)
        decode=symetrique.dechiffre(code)
        print("message original = ",message,"\n message decode = ",decode)


# exemple de code pour faire transiter la clé de chiffrement symétrique vers les clients :
# .send(bytes(str(symetrique.key)[2:-1],'utf-8'))