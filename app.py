import pandas as pd
from datetime import datetime, timedelta, date
from tkinter import *
from tkcalendar import Calendar


def fichier_planning():  # Ouverture du fichier avec création de celui-ci pour la première utilisation.
    try:
        df = pd.read_parquet("planning.parquet")
    except FileNotFoundError:
        colonnes = ["date", "heure_deb", "heure_fin", "lieu", "duree"]
        df = pd.DataFrame(columns=colonnes)
        df["date"] = pd.to_datetime(df["date"])
        df["heure_deb"] = pd.to_datetime(df["heure_deb"], format="%H:%M")
        df["heure_fin"] = pd.to_datetime(df["heure_fin"], format="%H:%M")
        df["duree"] = df["heure_fin"] - df["heure_deb"]
        df.to_parquet("planning.parquet", index= False)
        print("Un nouveau fichier à été créé.")
    return df

def bouton_ajouter():
    global df
    date_selec = (datetime.strptime(calendrier.get_date(), "%m/%d/%y")).date()  # Récupère la sélection avec get_date, transforme la str en datetime puis juste en date.
    heure_deb = int(spin_heures_deb.get()) # Récupère l'heure de début et la transforme en entier, un spin renvoi un string.
    minutes_deb = int(spin_minutes_deb.get())
    horaire_debut = datetime(25, 1, 1, heure_deb, minutes_deb)  # Crée un objet datetime avec une date arbitraire car il faut une date.
    heure_fin = int(spin_heures_fin.get())
    minutes_fin = int(spin_minutes_fin.get())
    horaire_fin = datetime(25, 1, 1, heure_fin, minutes_fin)
    if horaire_fin < horaire_debut:  # Gère si l'heure de fin est plus petite que l'heure de début, (trabail de nuit).
        horaire_fin += timedelta(days= 1)  # Ajoute 1 jour à l'horaire de fin.
    duree = horaire_fin - horaire_debut
    if choix.get() == "Autre":
        lieu = nouveau_lieu.get()
    else:
        lieu = choix.get()
    nouvelle_mission = pd.DataFrame([{"date": date_selec,  # Création d'un dataframe avec la nouvelle mission.
                                      "heure_deb": horaire_debut,
                                      "heure_fin": horaire_fin,
                                      'lieu': lieu,
                                      "duree": duree}])
    df = pd.concat([df, nouvelle_mission], ignore_index=True)  # Concataine les deux dataframe.
    df.to_parquet("planning.parquet", index= False)

def mois_precedent(): # Calcul du mois précédent. Pas de timedelta month - 1 donc petite magouille.
    aujourdhui = date.today()
    mois_temp = aujourdhui.replace(day= 1)
    mois_precedent = mois_temp - timedelta(days=1)
    return mois_precedent

def traduction_mois(nombre):  # Evite de passer par des langues locales, ce qui ne fonctionne pas toujours notamment avec des machines virtuelle.
    mois_francais = ["janvier", "février", "mars", "avril", "mai", "juin",
                    "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return mois_francais[nombre - 1]


df = fichier_planning()
print(df.dtypes)
print(df)

# Fenêtre principale.
window_principale = Tk()  # Création de la fenêtre principale.
window_principale.title("Planning.") # Titre de la fenêtre principale.
window_principale.geometry("720x480") # Taille de la fenêtre lors de l'ouverture.
window_principale.minsize(480, 360) # Taille minimum de la fenêtre.

# Création d'une zone de travail prenant toute la place.
frame_contenair = Frame(window_principale)
frame_contenair.pack(expand= YES, fill= "both") # Expand permet d'occuper la place disponible et fill="both" force d'occuper l'espace disponible

# Création de la zone de travail de gauche.
frame_gauche = Frame(frame_contenair, bg="#1518C0")
frame_gauche.pack(side= "left", expand= YES, fill= "both")

# Création de la zone de travail de droite.
frame_droite = Frame(frame_contenair, bg="#E77B15")
frame_droite.pack(side= "right", expand= YES, fill= "both")

# ZONE DE GAUCHE.
lb_titre = Label(frame_gauche, text= "BIENVENUE")
lb_titre.pack(expand= YES)
lb_mois_dernier = Label(frame_gauche, text= f"Heures du mois {"d'" if traduction_mois(mois_precedent().month) == "octobre" else "de"}{traduction_mois(mois_precedent().month)} {mois_precedent().year} :")
lb_mois_dernier.pack(expand= YES)
lb_mois_actuel = Label(frame_gauche, text= f"Heures du mois {"d'" if traduction_mois(date.today().month) == "octobre" else "de"} {traduction_mois(date.today().month)} {date.today().year} :")
lb_mois_actuel.pack(expand= YES)

# ZONE DE DROITE.
    # Calendrier.
calendrier = Calendar(frame_droite)
calendrier.pack(expand= YES)
date = calendrier.get_date()  # A mettre dans la fonction du bouton ajouter
print(type(date))
    # Horloge.
frame_horloge = Frame(frame_droite, bd= 1)
frame_horloge.pack(expand= YES)
        # Horloge de début.
            # Frame pour les spinbox.
frame_horloge_gauche = Frame(frame_horloge)
frame_horloge_gauche.pack(side="left", padx=5)
lb_heure_deb = Label(frame_horloge_gauche, text= "Heure de début.")
lb_heure_deb.pack(expand= YES)
frame_heure_deb = Frame(frame_horloge_gauche, bg="red")
frame_heure_deb.pack(side="left", padx=5)
            # Spinbox pour les heures (0 à 23).
spin_heures_deb = Spinbox(frame_heure_deb, from_=0, to=23, wrap=True, # wrap : revient à 0 après 23.
                    width=3, font=("Courier", 20), justify="center",
                    state="readonly", format="%02.0f") # state empêche la saisie manuelle.  format pour toujour avoir 2 chiffres (ex: 02)
spin_heures_deb.pack(side="left", padx=5)
            # Label séparateur.
Label(frame_heure_deb, text=":", bg= "white", font=("Courier", 20)).pack(side="left")
            # Spinbox pour les minutes (0 à 59).
spin_minutes_deb = Spinbox(frame_heure_deb, from_=0, to=59, wrap=True,
                              width=3, font=("Courier", 20), justify="center",
                              state="readonly", format="%02.0f")
spin_minutes_deb.pack(side="left", padx=5)
        # Horloge de fin.
            # Frame pour les spinbox.
frame_horloge_droite = Frame(frame_horloge)
frame_horloge_droite.pack(side="left", padx=5)
lb_heure_fin = Label(frame_horloge_droite, text= "Heure de fin.")
lb_heure_fin.pack(expand= YES)
frame_heure_fin = Frame(frame_horloge_droite, bg="red")
frame_heure_fin.pack(side="left", padx=5)
            # Spinbox pour les heures (0 à 23).
spin_heures_fin = Spinbox(frame_heure_fin, from_=0, to=23, wrap=True,
                    width=3, font=("Courier", 20), justify="center",
                    state="readonly", format="%02.0f")
spin_heures_fin.pack(side="left", padx=5)
            # Label séparateur.
Label(frame_heure_fin, text=":", bg= "white", font=("Courier", 20)).pack(side="left")
            # Spinbox pour les minutes (0 à 59).
spin_minutes_fin = Spinbox(frame_heure_fin, from_=0, to=59, wrap=True,
                              width=3, font=("Courier", 20), justify="center",
                              state="readonly", format="%02.0f")
spin_minutes_fin.pack(side="left", padx=5)
    # Lieu de la mission.
frame_lieu = Frame(frame_droite)
frame_lieu.pack(expand= YES)
lb_lieu = Label(frame_lieu, text= "Lieu de la mission")
lb_lieu.pack(expand= YES)
frame_lieu_widgets = Frame(frame_lieu) # Nouvelle frame pour mettre les 2 widgets l'un à coté de l'autre.
frame_lieu_widgets.pack(side="left", padx=5)
        # Liste des lieux déjà faits.
liste_lieu = ["Autre"] + (df["lieu"].unique().tolist()) # Récupère dans le dataframe la liste des lieux différents et en plus le AUTRE pour pouvoir ajouter un nouveau lieu.
choix = StringVar() # Dédinie une variable TK liée à un widget.
choix.set("Autre") # Valeur par défaut.
menu_lieu = OptionMenu(frame_lieu_widgets, choix, *liste_lieu) # Ne pas oublier le * devant la liste sinon ça n'en fait qu'une seule et unique str.
menu_lieu.pack(side="left", padx=5)
        # Ajout d'un nouveau lieu "INPUT"
nouveau_lieu = StringVar()
input_lieu = Entry(frame_lieu_widgets, textvariable= nouveau_lieu)
input_lieu.pack(side="left", padx=5)
    # Bouton.
btn_ajouter = Button(frame_droite, text="Ajouter la mission.", font=("Arrial", 15), bg= "white", fg="Yellow", command= bouton_ajouter)
btn_ajouter.pack(expand= YES)




window_principale.mainloop()