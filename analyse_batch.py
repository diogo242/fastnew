import os
import json
import pandas as pd
from datetime import datetime
from analyse_avancee import AnalyseQuittance

def analyser_dossier(dossier_quittances, regles=None):
    """Analyse toutes les quittances dans un dossier"""
    
    resultats = []
    
    # Parcourir tous les fichiers PDF
    for fichier in os.listdir(dossier_quittances):
        if fichier.endswith('.pdf'):
            chemin = os.path.join(dossier_quittances, fichier)
            print(f"\n📄 Analyse de : {fichier}")
            
            try:
                # Analyser la quittance
                analyse = AnalyseQuittance(chemin)
                infos = analyse.extraire_infos()
                anomalies = analyse.valider_infos(regles)
                falsifications = analyse.detecter_falsifications()
                
                # Stocker les résultats
                resultat = {
                    'fichier': fichier,
                    'chemin': chemin,
                    'statut': 'VALIDÉ' if not anomalies else 'REJETÉ',
                    'numero': infos.get('numero'),
                    'nom': infos.get('nom'),
                    'prenom': infos.get('prenom'),
                    'montant': infos.get('montant'),
                    'date': infos.get('date'),
                    'reference': infos.get('reference'),
                    'anomalies': '; '.join(anomalies) if anomalies else 'Aucune',
                    'falsifications': '; '.join(falsifications) if falsifications else 'Aucune',
                    'date_analyse': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                resultats.append(resultat)
                
                # Afficher un résumé
                print(f"  ✅ Statut : {resultat['statut']}")
                print(f"  📝 Numéro : {infos.get('numero', 'Non trouvé')}")
                print(f"  💰 Montant : {infos.get('montant', 'Non trouvé')} FCFA")
                
            except Exception as e:
                print(f"  ❌ Erreur : {str(e)}")
                resultats.append({
                    'fichier': fichier,
                    'statut': 'ERREUR',
                    'erreur': str(e)
                })
    
    return resultats

# ====== UTILISATION ======

# 1. Analyser toutes les quittances d'un dossier
dossier = "quittances/"  # Mets le chemin de ton dossier
regles = {
    'montant_min': 1000,
    'montant_max': 5000000,
    'annee_min': 2024,
    'annee_max': 2026,
    'forcer_numero': True,
    'forcer_nom': True
}

resultats = analyser_dossier(dossier, regles)

# 2. Exporter en CSV
df = pd.DataFrame(resultats)
df.to_csv('rapport_quittances.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Rapport exporté dans 'rapport_quittances.csv'")

# 3. Exporter en JSON
with open('rapport_quittances.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)
print(f"✅ Rapport exporté dans 'rapport_quittances.json'")

# 4. Afficher les statistiques
print("\n" + "="*60)
print("📊 STATISTIQUES")
print("="*60)
print(f"Total : {len(resultats)}")
print(f"Validé : {sum(1 for r in resultats if r.get('statut') == 'VALIDÉ')}")
print(f"Rejeté : {sum(1 for r in resultats if r.get('statut') == 'REJETÉ')}")
print(f"Erreur : {sum(1 for r in resultats if r.get('statut') == 'ERREUR')}")