import os
from analyse_avancee import AnalyseQuittance
from analyse_batch import analyser_dossier

def menu():
    print("\n" + "="*60)
    print("🔍 ANALYSEUR DE QUITTANCES")
    print("="*60)
    print("1. Analyser une seule quittance")
    print("2. Analyser un dossier entier")
    print("3. Quitter")
    print("="*60)
    
    choix = input("\nVotre choix : ")
    
    if choix == '1':
        chemin = input("Chemin du PDF : ")
        if os.path.exists(chemin):
            analyse = AnalyseQuittance(chemin)
            analyse.extraire_infos()
            analyse.valider_infos()
            analyse.afficher_rapport()
        else:
            print("❌ Fichier non trouvé !")
    
    elif choix == '2':
        dossier = input("Chemin du dossier : ")
        if os.path.exists(dossier):
            analyser_dossier(dossier)
        else:
            print("❌ Dossier non trouvé !")
    
    elif choix == '3':
        print("👋 Au revoir !")
        exit()
    
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    while True:
        menu()