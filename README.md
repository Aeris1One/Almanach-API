# Almanach API
API des horaires, tracés, lignes, arrêts et tout ce qui a trait aux
transports en commun de France.

## Présentation
Almanach API récupère les flux GTFS de plusieurs réseaux français depuis
transport.data.gouv.fr, les compile et rends accessible les données de ces
réseaux via une API REST.

Le projet fonctionne de pair avec un serveur [Motis](https://motis-project.de/),
logiciel de routage multimodal, qui récupère le flux GTFS unifié que cette API
lui fournit.

## Fonctionnement
Deux composants fonctionnent de pair pour permettre le fonctionnement de l'API :
- L'API en elle-même, qui expose les informations contenues dans une base Postgresql
- Le système de mise à jour, qui s'occupe de la récupération périoqique des flux GTFS
  pour les intégrer à la base de données

### L'API
L'API est une application FastAPI, écrite en Python. Elle expose les données
contenues dans une base de données Postgresql. 
Elle expose les endpoints suivants (la case à cocher indique si l'endpoint est implémenté) :
- [x] : `/admin` : Interface d'administration basique (ajout, suppression, liste des flux récupérés)
- [ ] : `/agency` : Agences (réseaux)
- [ ] : `/route` : Lignes (avec leur tracé)
- [ ] : `/stop` : Arrêts
- [ ] : `/stop_time` : Horaires aux arrêts

### Le système de mise à jour
Nous utilisons Celery pour gérer les tâches de fond. Le système a besoin d'un serveur
Redis ou RabbitMQ. Plusieurs tâches peuvent tourner en parallèle :
- `scheduler` : Exécuté toutes les 15 minutes. Récupère depuis l'API de transport.data.gouv.fr la liste des flux GTFS
   disponibles, vérifie si un des flux que l'API suit a été mis à jour, et si c'est le cas,
   déclenche une tâche `updater` pour le mettre à jour.
- `updater` : Exécuté sur demande du `scheduler`. Récupère un flux GTFS, effectue les transformations paramétrées pour celui-ci
    (par exemple, renommer/supprimer des arrêts, des lignes, générer les formes, etc.), et 
    met à jour la base de données.
- `exporter` : Exécuté périodiquement (à définir). Exporte les données de la base de données dans un flux GTFS unique, pour
    être utilisé par Motis.

Ce système de mise à jour en arrière-plan permet de ne pas bloquer l'API lors de la mise à jour,
ainsi que de ne mettre à jour que lorsque c'est nécessaire. 

## Installation
### Prérequis
- Python 3.12
- Un serveur Postgresql
- Un serveur Redis ou RabbitMQ

### Installation
1. Cloner le dépôt
2. Installer les dépendances : `pip install -r requirements.txt`
3. Faites en sorte que les variables d'environnement suivantes soient définies :
    ```env
    DATABASE_URL=postgresql://user:password@host:port/database
    REDIS_URL=redis://host:port
    ADMIN_API_KEY=your_api_key
    ```
4. Utiliser les commandes suivantes pour démarrer les différents composants (elles doivent être allumées
   en même temps) :
    - API : `fastapi dev app/main.py`
    - Tâches de fond : `./celery_start.sh local`
    - (optionnel) Interface de supervision des tâches de fond : `./celery_start.sh flower`

### Installation via Docker
Il est également possible d'utiliser le fichier `docker-compose.yml` pour démarrer l'API et les tâches de fond
dans des conteneurs Docker sans aucune autre dépendance.
Ce stack déploie aussi un conteneur Postgresql et un conteneur Redis.
Il n'est pas prévu pour un déploiement en production.

### Déploiement en SaaS
Il est possible de déployer l'API et les tâches de fond sur un service SaaS, les images Docker sont fournies
[ici](https://github.com/Aeris1One/Almanach-API/pkgs/container/almanach-api).

Notons que pour un déploiement en production, contrairement à un déploiement en développement, le `worker` (qui effectue
les tâches de fond) et le `beat` (qui planifie les évènements récurrents) doivent être séparés. Il est possible d'avoir 
plusieurs workers pour paralléliser les tâches de fond, mais SURTOUT, il ne faut jamais avoir plus d'un beat.