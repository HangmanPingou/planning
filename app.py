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
        df["nb_heures_pause"] = pd.Series(dtype= "int64")
        df["nb_minutes_pause"] = pd.Series(dtype= "int64")
        df.to_parquet("planning.parquet", index= False)
        print("Un nouveau fichier à été créé.")
    return df

def bouton_ajouter():
    global df
    date_selec = pd.to_datetime(calendrier.get_date(), format="%m/%d/%y").normalize() # Le normalize mets les heures à 00:00 mais pandas ne gère pas de date mais du datetime.
    heure_deb = int(spin_heures_deb.get()) # Récupère l'heure de début et la transforme en entier, un spin renvoi un string.
    minutes_deb = int(spin_minutes_deb.get())
    horaire_debut = datetime(25, 1, 1, heure_deb, minutes_deb)  # Crée un objet datetime avec une date arbitraire car il faut une date.
    heure_fin = int(spin_heures_fin.get())
    minutes_fin = int(spin_minutes_fin.get())
    horaire_fin = datetime(25, 1, 1, heure_fin, minutes_fin)
    if horaire_fin < horaire_debut:  # Gère si l'heure de fin est plus petite que l'heure de début, (trabail de nuit).
        horaire_fin += timedelta(days= 1)  # Ajoute 1 jour à l'horaire de fin.
    heure_pause = int(spin_heures_pause.get())
    minutes_pause = int(spin_minutes_pause.get())
    duree = horaire_fin - horaire_debut - timedelta(hours= heure_pause, minutes= minutes_pause)
    if choix.get() == "Autre":
        lieu = nouveau_lieu.get()
    else:
        lieu = choix.get()
    nouvelle_mission = pd.DataFrame([{"date": date_selec,  # Création d'un dataframe avec la nouvelle mission.
                                      "heure_deb": horaire_debut,
                                      "heure_fin": horaire_fin,
                                      'lieu': lieu,
                                      "duree": duree,
                                      "nb_heures_pause" : heure_pause,
                                      "nb_minutes_pause" : minutes_pause}])
    df = pd.concat([df, nouvelle_mission], ignore_index=True)  # Concataine les deux dataframe.
    df = df.sort_values(by="date") # Trie par ordre de date de la mission et non par ordre d'entrée.
    df.to_parquet("planning.parquet", index= False)
    lb__heures_mois_precedent.configure(text= f"{calculer_duree_mois(df, mois_precedent().month, annee)}")
    lb_heures_mois_actuel.configure(text=  f"{calculer_duree_mois(df, date.today().month, date.today().year)}")

def mois_precedent(): # Calcul du mois précédent. Pas de timedelta month - 1 donc petite magouille.
    aujourdhui = date.today()
    mois_temp = aujourdhui.replace(day= 1)
    mois_precedent = mois_temp - timedelta(days=1)
    return mois_precedent

def traduction_mois(nombre):  # Evite de passer par des langues locales, ce qui ne fonctionne pas toujours notamment avec des machines virtuelles.
    mois_francais = ["janvier", "février", "mars", "avril", "mai", "juin",
                    "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return mois_francais[nombre - 1]

def calculer_duree_mois(df, mois, annee):
    filtre = (df["date"].dt.month == mois) & (df["date"].dt.year == annee)
    df_filtre = df.loc[filtre]
    duree_totale_mois = df_filtre["duree"].sum()
    duree_totale_seconde = int(duree_totale_mois.total_seconds())
    heures_totale_mois = int(duree_totale_seconde // 3600)
    minutes_totale_mois = int((duree_totale_seconde % 3600) // 60)
    return f"{heures_totale_mois:02d} h {minutes_totale_mois:02d} min"

def window_supprimer_mission():  # Nouvelle fenêtre ouverte par le choix du menu.
    window_suppr = Tk()
    window_suppr.title("Suppression d'une mission.")
    window_suppr.geometry("640x480")
    window_suppr.config(bg= couleur_fond)
    frame_contenair_suppr = Frame(window_suppr, bg= couleur_fond)
    frame_contenair_suppr.pack(expand= YES, fill= "both", padx= 10, pady= 10)
    frame_cadre = Frame(frame_contenair_suppr, bg= couleur_cadre, relief= "sunken", bd= 2)
    frame_cadre.pack(expand= YES, fill= "both", padx= 5, pady= 5)
    lb_titre_suppr = Label(frame_cadre, text= "Suppresion d'une mission", font= police_titre, bg= couleur_cadre, fg= couleur_texte, pady= 10)
    lb_titre_suppr.pack(pady= (20, 10))
    liste_affichage_suppr = ["Quelle mission ?"] + [f"{row['date'].strftime('%d/%m/%Y')} - " # Une liste de dictionnaire ne fonctionne pas à l'affichage, donc une liste plus simple.
            f"{row['lieu']} ({row['heure_deb'].strftime('%H:%M')}→{row['heure_fin'].strftime('%H:%M')})"
            for _, row in df.iterrows()]
    choix_suppr = StringVar(master= window_suppr, value=liste_affichage_suppr[0]) # Le paramètre master pour bien gérer les variables internes de cette fenêtre. Le value évite de faire un .set
    menu_suppr = OptionMenu(frame_cadre, choix_suppr, *liste_affichage_suppr)
    menu_suppr.config(bg= couleur_bouton, fg= "white", highlightthickness= 0, activebackground= couleur_bouton_survol)
    menu_suppr.pack(expand= YES, padx= 10)
    btn_suppr = Button(frame_cadre, text= "Supprimer la mission", bg=couleur_bouton, fg="white", activebackground=couleur_bouton_survol,
                command=lambda: supprimer_mission(df, choix_suppr, liste_affichage_suppr, window_suppr)) # Lance la fonction avec comme paramètres les différentes variables.
    btn_suppr.pack(pady=10)
    window_suppr.mainloop()

def supprimer_mission(df, choix_suppr, liste_affichage_suppr, window_suppr):
    selection = choix_suppr.get() # Récupère la sélection.
    index = liste_affichage_suppr.index(selection) - 1 # Lindex commence à 0.
    df.drop(df.index[index], inplace=True)  # Efface la ligne du dataframe.
    df.to_parquet("planning.parquet", index=False)  # Enregistre la suppression.
    df = pd.read_parquet("planning.parquet") # Remet à jour le dataframe en mémoire.
    lb__heures_mois_precedent.configure(text= f"{calculer_duree_mois(df, mois_precedent().month, annee)}")  # Met à jour le nombre d'heure.
    lb_heures_mois_actuel.configure(text=  f"{calculer_duree_mois(df, date.today().month, date.today().year)}")
    window_suppr.destroy() # Ferme la fenêtre.
    


df = fichier_planning()
print(df.dtypes)
print(df)

# Choix du thème.
couleur_fond = "#2e2e2e"
couleur_cadre = "#3c3c3c"
couleur_texte = "#f2f2f2"
couleur_accent = "#5c5c5c"
couleur_bouton = "#404040"
couleur_bouton_survol = "#606060"
police_titre = ("Helvetica", 16, "bold")
police_texte = ("Helvetica", 12)

# Fenêtre principale.
window_principale = Tk()  # Création de la fenêtre principale.
window_principale.title("Planning.") # Titre de la fenêtre principale.
window_principale.geometry("950x650") # Taille de la fenêtre lors de l'ouverture.
window_principale.minsize(600, 400) # Taille minimum de la fenêtre.
window_principale.config(bg= couleur_fond) # Couleur de fond de la fenêtre principale.

# Menu.
menu_bar = Menu(window_principale,   # Je laisse les paramètres de couleurs car celà fonctionne sous linux. Sous windows ou IOS, la barre faisant partie de l'os ne prend pas en compte les couleurs.
                bg= couleur_fond,          # Couleur de fond du menu principal
                fg= couleur_texte,          # Couleur du texte
                activebackground= couleur_bouton_survol,  # Fond au survol
                activeforeground="white",   # Texte au survol
                relief="flat",              # Pas de bordure épaisse
                borderwidth=0)             # Paramètre tearoff permet d'enlever des ----- à l'affichage.
# file_menu = Menu(menu_bar, tearoff=0)  # Paramètre tearoff permet d'enlever des ----- à l'affichage.
file_menu = Menu(menu_bar, tearoff=0, bg= couleur_cadre, fg= couleur_texte, activebackground= couleur_bouton_survol,  # Là c'est pris en compte.
                 activeforeground="white", relief="flat", borderwidth=0)
file_menu.add_command(label= ("Supprimer une mission"), command= window_supprimer_mission)
file_menu.add_command(label= "Quitter", command= window_principale.quit)
menu_bar.add_cascade(label= "Fichier", menu= file_menu)
window_principale.config(menu= menu_bar)

# Création d'une zone de travail prenant toute la place.
frame_contenair = Frame(window_principale, bg= couleur_fond)
frame_contenair.pack(expand= YES, fill= "both", padx= 10, pady= 10) # Expand permet d'occuper la place disponible et fill="both" force d'occuper l'espace disponible

# Création de la zone de travail de gauche.
frame_gauche = Frame(frame_contenair, bg= couleur_cadre, relief= "sunken", bd= 2)
frame_gauche.pack(side= "left", expand= YES, fill= "both", padx= 5, pady= 5)

# Création de la zone de travail de droite.
frame_droite = Frame(frame_contenair, bg= couleur_cadre, relief= "sunken", bd= 2)
frame_droite.pack(side= "right", expand= YES, fill= "both", padx= 5, pady= 5)

# ZONE DE GAUCHE.
lb_titre = Label(frame_gauche, text= "BIENVENUE", font= police_titre, bg= couleur_cadre, fg= couleur_texte, pady= 10)
lb_titre.pack(pady= (20, 10))
lb_mois_dernier = Label(frame_gauche, text= f"Heures du mois {"d'" if traduction_mois(mois_precedent().month) == "octobre" else "de"}{traduction_mois(mois_precedent().month)} {mois_precedent().year} :",
                        font= police_texte, bg= couleur_cadre, fg= couleur_texte)
lb_mois_dernier.pack(pady= 10)
if mois_precedent() == 12: # Ajoute le changement d'année. A vérifier que celà fonctionne en janvier.
    annee = date.today().year - timedelta(days= 365) # A tester car sinon je mets un timedelta(days= 40) mais ça fait moin propre je trouve.
else:
    annee = date.today().year
lb__heures_mois_precedent = Label(frame_gauche, text= f"{calculer_duree_mois(df, mois_precedent().month, annee)}",
                              font= police_texte, bg= couleur_cadre, fg= couleur_texte)
lb__heures_mois_precedent.pack(pady= 1)
lb_mois_actuel = Label(frame_gauche, text= f"Heures du mois {"d'" if traduction_mois(date.today().month) == "octobre" else "de"} {traduction_mois(date.today().month)} {date.today().year} :",
                       font= police_texte, bg= couleur_cadre, fg= couleur_texte)
lb_mois_actuel.pack(pady= 10)
lb_heures_mois_actuel = Label(frame_gauche, text= f"{calculer_duree_mois(df, date.today().month, date.today().year)}",
                              font= police_texte, bg= couleur_cadre, fg= couleur_texte)
lb_heures_mois_actuel.pack(pady= 1)

# ZONE DE DROITE.
    # Calendrier.
calendrier = Calendar(frame_droite, background= couleur_accent, disabledbackground= couleur_accent, bordercolor= couleur_accent,
                      headershackground= couleur_bouton, normalbackground= couleur_fond,
                      foreground= "white", normalforeground= "white", selectbackground= couleur_bouton_survol)
calendrier.pack(pady= 15)
date_selec = calendrier.get_date()  # A mettre dans la fonction du bouton ajouter
print(type(date))
    # Horloge.
frame_horloge = Frame(frame_droite, bg= couleur_cadre, pady= 10)
frame_horloge.pack(expand= YES, pady= 10)
        # Horloge de début.
            # Frame pour les spinbox.
frame_horloge_gauche = Frame(frame_horloge, bg= couleur_cadre)
frame_horloge_gauche.pack(side="left", padx= 10)
lb_heure_deb = Label(frame_horloge_gauche, text= "Heure de début.", bg= couleur_cadre, fg= couleur_texte, font= police_texte)
lb_heure_deb.pack(pady= 5)
frame_heure_deb = Frame(frame_horloge_gauche, bg= couleur_accent, relief= "sunken", bd= 1)
frame_heure_deb.pack(pady= 5)
            # Spinbox pour les heures (0 à 23).
spin_heures_deb = Spinbox(frame_heure_deb, from_=0, to=23, wrap=True, # wrap : revient à 0 après 23.
                    width=3, font=("Courier", 18), justify="center",
                    state="readonly", format="%02.0f") # state empêche la saisie manuelle.  format pour toujour avoir 2 chiffres (ex: 02)
spin_heures_deb.pack(side="left", padx= 2)
            # Label séparateur.
Label(frame_heure_deb, text=":", bg= couleur_accent, font=("Courier", 18)).pack(side="left")
            # Spinbox pour les minutes (0 à 59).
spin_minutes_deb = Spinbox(frame_heure_deb, from_=0, to=59, wrap=True,
                              width=3, font=("Courier", 18), justify="center",
                              state="readonly", format="%02.0f")
spin_minutes_deb.pack(side="left", padx=2)
        # Horloge de fin.
            # Frame pour les spinbox.
frame_horloge_milieu = Frame(frame_horloge, bg= couleur_cadre)
frame_horloge_milieu.pack(side="left", padx=10)
lb_heure_fin = Label(frame_horloge_milieu, text= "Heure de fin.", bg= couleur_cadre, fg= couleur_texte, font= police_texte)
lb_heure_fin.pack(pady= 5)
frame_heure_fin = Frame(frame_horloge_milieu, bg= couleur_accent, relief= "sunken", bd= 1)
frame_heure_fin.pack(pady= 5)
            # Spinbox pour les heures (0 à 23).
spin_heures_fin = Spinbox(frame_heure_fin, from_=0, to=23, wrap=True,
                    width=3, font=("Courier", 18), justify="center",
                    state="readonly", format="%02.0f")
spin_heures_fin.pack(side="left", padx=2)
            # Label séparateur.
Label(frame_heure_fin, text=":", bg= couleur_accent,fg= couleur_texte, font=("Courier", 18)).pack(side="left")
            # Spinbox pour les minutes (0 à 59).
spin_minutes_fin = Spinbox(frame_heure_fin, from_=0, to=59, wrap=True,
                              width=3, font=("Courier", 18), justify="center",
                              state="readonly", format="%02.0f")
spin_minutes_fin.pack(side="left", padx= 2)
        # Horloge de la pause non rémunérée..
            # Frame pour les spinbox.
frame_horloge_droite = Frame(frame_horloge, bg= couleur_cadre)
frame_horloge_droite.pack(side="left", padx=10)
lb_heure_pause = Label(frame_horloge_droite, text= "Pause non rémunérée.", bg= couleur_cadre, fg= couleur_texte, font= police_texte)
lb_heure_pause.pack(pady= 5)
frame_heure_pause = Frame(frame_horloge_droite, bg= couleur_accent, relief= "sunken", bd= 1)
frame_heure_pause.pack(pady= 5)
            # Spinbox pour les heures (0 à 23).
spin_heures_pause = Spinbox(frame_heure_pause, from_=0, to=23, wrap=True,
                    width=3, font=("Courier", 18), justify="center",
                    state="readonly", format="%02.0f")
spin_heures_pause.pack(side="left", padx=2)
            # Label séparateur.
Label(frame_heure_pause, text=":", bg= couleur_accent,fg= couleur_texte, font=("Courier", 18)).pack(side="left")
            # Spinbox pour les minutes (0 à 59).
spin_minutes_pause = Spinbox(frame_heure_pause, from_=0, to=59, wrap=True,
                              width=3, font=("Courier", 18), justify="center",
                              state="readonly", format="%02.0f")
spin_minutes_pause.pack(side="left", padx= 2)
    # Lieu de la mission.
frame_lieu = Frame(frame_droite, bg= couleur_cadre)
frame_lieu.pack(pady= 10)
lb_lieu = Label(frame_lieu, text= "Lieu de la mission", font= police_texte, bg= couleur_cadre, fg= couleur_texte)
lb_lieu.pack(pady= 5)
frame_lieu_widgets = Frame(frame_lieu, bg= couleur_cadre) # Nouvelle frame pour mettre les 2 widgets l'un à coté de l'autre.
frame_lieu_widgets.pack()
        # Liste des lieux déjà faits.
liste_lieu = ["Autre"] + (df["lieu"].unique().tolist()) # Récupère dans le dataframe la liste des lieux différents et en plus le AUTRE pour pouvoir ajouter un nouveau lieu.
choix = StringVar() # Dédinie une variable TK liée à un widget.
choix.set("Autre") # Valeur par défaut.
menu_lieu = OptionMenu(frame_lieu_widgets, choix, *liste_lieu) # Ne pas oublier le * devant la liste sinon ça n'en fait qu'une seule et unique str.
menu_lieu.config(bg= couleur_bouton, fg= "white", highlightthickness= 0, activebackground= couleur_bouton_survol)
menu_lieu.pack(side="left", padx=5)
        # Ajout d'un nouveau lieu "INPUT"
nouveau_lieu = StringVar()
input_lieu = Entry(frame_lieu_widgets, textvariable= nouveau_lieu, width= 15, bg= couleur_accent, fg= couleur_texte,
                   insertbackground= "white", relief= "sunken", bd= 1)
input_lieu.pack(side="left", padx=5)
    # Bouton.
btn_ajouter = Button(frame_droite, text="Ajouter la mission.", font=("Arrial", 14, "bold"), bg= couleur_bouton, fg= "white",
                     activebackground= couleur_bouton_survol, relief= "raised", bd= 2, command= bouton_ajouter)
btn_ajouter.pack(pady= 15, ipadx= 10, ipady= 5)




window_principale.mainloop()