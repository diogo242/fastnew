import fitz
import re
from datetime import datetime

class AnalyseQuittance:
    def __init__(self, chemin_pdf):
        self.chemin = chemin_pdf
        self.texte = self._extraire_texte()
        self.infos = {}
        self.anomalies = []
        
    def _extraire_texte(self):
        """Extrait tout le texte du PDF"""
        doc = fitz.open(self.chemin)
        texte = ""
        for page in doc:
            texte += page.get_text()
        doc.close()
        return texte
    
    def extraire_infos(self):
        """Extrait toutes les informations structurées"""
        
        # 1. Numéro de quittance (format TP-AAAA-NNNNNN)
        match = re.search(r'(TP|QUITTANCE|N°|No\.?)\s*[:]?\s*([A-Z0-9\-]{6,20})', self.texte, re.IGNORECASE)
        if match:
            self.infos['numero'] = match.group(2).strip()
        else:
            self.infos['numero'] = None
            self.anomalies.append("Numéro de quittance non trouvé")
        
        # 2. Montant (plusieurs formats possibles)
        patterns_montant = [
            r'(\d+[\s]?\d+[\s]?\d*)\s*(FCFA|XOF|CFA)',  # 15 000 FCFA
            r'Montant\s*[:]?\s*(\d+[\s]?\d+[\s]?\d*)',   # Montant : 15000
            r'Total\s*[:]?\s*(\d+[\s]?\d+[\s]?\d*)'      # Total : 15000
        ]
        
        for pattern in patterns_montant:
            match = re.search(pattern, self.texte, re.IGNORECASE)
            if match:
                montant_brut = match.group(1).replace(' ', '')
                self.infos['montant'] = int(montant_brut)
                break
        else:
            self.infos['montant'] = None
            self.anomalies.append("Montant non trouvé")
        
        # 3. Date (format JJ/MM/AAAA ou JJ-MM-AAAA)
        match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', self.texte)
        if match:
            jour, mois, annee = match.groups()
            self.infos['date'] = f"{jour}/{mois}/{annee}"
            self.infos['date_obj'] = datetime(int(annee), int(mois), int(jour))
        else:
            self.infos['date'] = None
            self.infos['date_obj'] = None
            self.anomalies.append("Date non trouvée")
        
        # 4. Nom du payeur
        patterns_nom = [
            r'(?:M\.|Monsieur|Mme|Madame)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Payeur\s*[:]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Nom\s*[:]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in patterns_nom:
            match = re.search(pattern, self.texte, re.IGNORECASE)
            if match:
                self.infos['nom'] = match.group(1).strip()
                break
        else:
            self.infos['nom'] = None
            self.anomalies.append("Nom non trouvé")
        
        # 5. Prénom
        match = re.search(r'Pr[ée]nom\s*[:]?\s*([A-Z][a-z]+)', self.texte, re.IGNORECASE)
        if match:
            self.infos['prenom'] = match.group(1).strip()
        else:
            self.infos['prenom'] = None
        
        # 6. Référence ou identifiant
        match = re.search(r'(R[ée]f[ée]rence|ID)\s*[:]?\s*([A-Z0-9\-]{6,20})', self.texte, re.IGNORECASE)
        if match:
            self.infos['reference'] = match.group(2).strip()
        else:
            self.infos['reference'] = None
        
        # 7. Service ou département
        match = re.search(r'(Service|D[ée]partement|Direction)\s*[:]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', self.texte, re.IGNORECASE)
        if match:
            self.infos['service'] = match.group(2).strip()
        else:
            self.infos['service'] = None
        
        return self.infos
    
    def valider_infos(self, regles=None):
        """Valide les informations selon des règles métier"""
        
        # Règles par défaut
        if regles is None:
            regles = {
                'montant_min': 100,
                'montant_max': 10000000,
                'annee_min': 2020,
                'annee_max': datetime.now().year,
                'forcer_numero': True,
                'forcer_nom': True
            }
        
        # Validation du montant
        if self.infos.get('montant'):
            if self.infos['montant'] < regles['montant_min']:
                self.anomalies.append(f"Montant trop bas : {self.infos['montant']} FCFA (< {regles['montant_min']})")
            elif self.infos['montant'] > regles['montant_max']:
                self.anomalies.append(f"Montant trop élevé : {self.infos['montant']} FCFA (> {regles['montant_max']})")
        
        # Validation de la date
        if self.infos.get('date_obj'):
            annee = self.infos['date_obj'].year
            if annee < regles['annee_min'] or annee > regles['annee_max']:
                self.anomalies.append(f"Date hors plage : {self.infos['date']}")
        
        # Vérification des champs obligatoires
        if regles.get('forcer_numero') and not self.infos.get('numero'):
            self.anomalies.append("Numéro de quittance manquant")
        
        if regles.get('forcer_nom') and not self.infos.get('nom'):
            self.anomalies.append("Nom du payeur manquant")
        
        return self.anomalies
    
    def detecter_falsifications(self):
        """Détecte des indices de falsification"""
        
        indices = []
        
        # 1. Vérifier si le texte est cohérent (pas de caractères bizarres)
        caracteres_bizarres = re.findall(r'[^\w\s\.,;:!?\-\(\)\/]', self.texte)
        if len(caracteres_bizarres) > 10:
            indices.append("Présence de caractères inhabituels (possible OCR ou modification)")
        
        # 2. Vérifier les métadonnées du PDF
        doc = fitz.open(self.chemin)
        metadata = doc.metadata
        doc.close()
        
        if metadata.get('creator') and 'Adobe' not in metadata['creator'] and 'Microsoft' not in metadata['creator']:
            indices.append(f"Créé avec un logiciel non standard : {metadata.get('creator')}")
        
        if metadata.get('producer') and 'Adobe' not in metadata['producer'] and 'Microsoft' not in metadata['producer']:
            indices.append(f"Produit avec un logiciel non standard : {metadata.get('producer')}")
        
        # 3. Vérifier si le texte a été modifié (recherche de mots suspects)
        mots_suspects = ['faux', 'test', 'exemple', 'annulé', 'copie']
        for mot in mots_suspects:
            if re.search(rf'\b{mot}\b', self.texte, re.IGNORECASE):
                indices.append(f"Mot suspect trouvé : '{mot}'")
        
        return indices
    
    def generer_rapport(self):
        """Génère un rapport complet"""
        
        rapport = {
            'fichier': self.chemin,
            'informations': self.infos,
            'anomalies': self.anomalies,
            'falsifications': self.detecter_falsifications(),
            'statut': 'VALIDÉ' if not self.anomalies else 'REJETÉ'
        }
        
        return rapport
    
    def afficher_rapport(self):
        """Affiche le rapport de manière lisible"""
        
        rapport = self.generer_rapport()
        
        print("\n" + "="*60)
        print(f"📄 RAPPORT D'ANALYSE - {rapport['fichier']}")
        print("="*60)
        
        print("\n📋 INFORMATIONS EXTRAITES :")
        print("-"*40)
        for cle, valeur in rapport['informations'].items():
            if valeur:
                print(f"  {cle:12} : {valeur}")
        
        if rapport['anomalies']:
            print("\n⚠️ ANOMALIES DÉTECTÉES :")
            print("-"*40)
            for anomalie in rapport['anomalies']:
                print(f"  ❌ {anomalie}")
        else:
            print("\n✅ Aucune anomalie détectée")
        
        if rapport['falsifications']:
            print("\n🔍 INDICES DE FALSIFICATION :")
            print("-"*40)
            for indice in rapport['falsifications']:
                print(f"  ⚠️ {indice}")
        else:
            print("\n✅ Aucun indice de falsification")
        
        print("\n" + "="*60)
        print(f"📊 STATUT FINAL : {rapport['statut']}")
        print("="*60 + "\n")
        
        return rapport

# ====== UTILISATION ======

# 1. Analyser une quittance
analyse = AnalyseQuittance("quittance.pdf")  # Mets le chemin de ton PDF

# 2. Extraire les informations
infos = analyse.extraire_infos()

# 3. Valider selon des règles personnalisées
regles = {
    'montant_min': 1000,
    'montant_max': 5000000,
    'annee_min': 2024,
    'annee_max': 2026,
    'forcer_numero': True,
    'forcer_nom': True
}
anomalies = analyse.valider_infos(regles)

# 4. Afficher le rapport
rapport = analyse.afficher_rapport()