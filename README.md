# 📡 ITU Space Data Importer

Ce projet permet de télécharger automatiquement les données de l'ITU (International Telecommunication Union) sur les satellites et leurs bandes de fréquences, puis de les stocker dans une base de données SQL afin de conserver un historique exploitable à des fins d'analyse et de visualisation.

## 🧾 Fonctionnalités

- Téléchargement des données au format CSV depuis l'API publique de l'ITU.
- Stockage des informations dans une base de données SQL avec suivi des dates d'import.
- Schéma de base de données conçu pour permettre des analyses dans le temps (ex. : suivi des positions orbitales ou des plages de fréquences).
- Préparation pour des visualisations futures de type *waterfall chart* ou série temporelle.

## 📂 Contenu du dépôt

- `main.py` — Script principal pour télécharger les données et les insérer dans la base.
- `itu_data.csv` — Exemple de fichier CSV téléchargé (à jour au moment de l'import).
- `itu_space.db` — (généré automatiquement) Base de données SQLite contenant les données.

## 🛠️ Prérequis

- Python 3.8 ou plus
- Bibliothèques suivantes :
    - requests
    - sqlalchemy

```bash
pip install requests sqlalchemy
````

## ▶️ Utilisation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/votre-utilisateur/itu-sat-tracker.git
   cd itu-sat-tracker
   ```

2. Lancez le script :

   ```bash
   python main.py
   ```

3. Un fichier `itu_space.db` sera généré dans le répertoire courant, contenant les données du CSV.

## 🗃️ Structure de la base

* `import_sessions` : contient l'historique des imports (avec date/heure).
* `frequency_assignments` : enregistrements des fréquences utilisées par satellite, avec leur plage, date de réception, etc.

## 📊 Visualisation

Le schéma relationnel permet de construire des visualisations de type **waterfall chart** pour suivre l'évolution :

* des positions orbitales (`long_nom`)
* des fréquences (`freq_from` / `freq_to`)
* par satellite (`sat_name`) ou par pays (`adm`)

Une implémentation graphique sera ajoutée par la suite (matplotlib, Plotly, Dash...).

## 📄 Exemple d’interrogation SQL

```sql
SELECT sat_name, long_nom, freq_from, freq_to, d_rcv, imported_at
FROM frequency_assignments
JOIN import_sessions ON frequency_assignments.session_id = import_sessions.id
ORDER BY sat_name, d_rcv;
```

## 📘 Références

* [Base de données spatiale de l’UIT](https://www.itu.int/en/ITU-R/space/Pages/space-apps.aspx)

