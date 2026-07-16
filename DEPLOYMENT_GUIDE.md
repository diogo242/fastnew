# Guide de déploiement sur Render

## Problème résolu
L'erreur `P1000: Authentication failed against database server` était causée par des identifiants de base de données locaux incorrects dans le fichier `.env`.

## Solution
Le fichier `render.yaml` a été créé pour configurer automatiquement le déploiement sur Render avec les bonnes informations de connexion à la base de données.

## Étapes de déploiement

### Étape 1 : Commit et push
```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

### Étape 2 : Configuration sur Render

#### Option A : Nouveau déploiement (recommandé)
1. Allez sur https://dashboard.render.com
2. Cliquez sur **"New +"** → **"Build and deploy"**
3. Sélectionnez votre repository GitHub/GitLab
4. Render détectera automatiquement le fichier `render.yaml`
5. Cliquez sur **"Connect"** pour créer le service

#### Option B : Mise à jour du service existant
1. Allez dans votre service existant **"unipay-verify-api"**
2. Cliquez sur **"Settings"**
3. Dans **"Build & Deploy"** :
   - **Build Command** : `npm install && npm run build`
   - **Start Command** : `npx prisma db push && npx tsx prisma/seed.ts && node dist/index.js`
4. Dans **"Environment Variables"**, ajoutez/modifiez :
   - `DATABASE_URL` : Cliquez sur **"Add from Database"** → sélectionnez `unipay_db_edh0`
   - `JWT_SECRET` : Générez une valeur sécurisée
   - `GEMINI_API_KEY` : `AQ.Ab8RN6KKAwSwdNQHiU8W_mPMT_M8EDV2x6pKTGxVDcfDXH8y3w`
   - `ADMIN_EMAIL` : `admin@uac.bj`
   - `ADMIN_PASSWORD` : `Admin@2026!`
   - `ADMIN_NOM` : `Administrateur UniPay`
   - `CORS_ORIGIN` : `https://unipay-verify-api.onrender.com`
   - `PORT` : `4000`
   - `UPLOAD_DIR` : `./uploads`

### Étape 3 : Vérifier la base de données
- Assurez-vous que la base de données PostgreSQL **unipay_db_edh0** existe sur Render
- Si elle n'existe pas : **"New +"** → **"PostgreSQL"** → nom : `unipay_db_edh0` → plan : Free

### Étape 4 : Déclencher le déploiement
- Cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**
- Ou faites un nouveau push sur GitHub pour un déploiement automatique

### Étape 5 : Surveiller le déploiement
- Regardez les logs en temps réel dans l'onglet **"Logs"**
- Le déploiement devrait maintenant réussir sans erreur d'authentification

## Vérification
Une fois déployé, testez l'API :
```bash
curl https://unipay-verify-api.onrender.com/health
```

## Notes importantes
- Le fichier `render.yaml` automatise toute la configuration
- La base de données sera automatiquement provisionnée si elle n'existe pas
- Les variables d'environnement sensibles (JWT_SECRET) sont générées automatiquement
- Le CORS est configuré pour le domaine de production