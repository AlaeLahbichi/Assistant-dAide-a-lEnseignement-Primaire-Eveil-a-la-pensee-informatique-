# 🏠 Smart Home OS – Habitat Intelligent avec IoT et LLM

## 📌 Description du projet

**Smart Home OS** est une plateforme de maison intelligente combinant l’**Internet des Objets (IoT)**, les **LLMs** et une **interface web moderne** afin d’améliorer le confort, la sécurité et la supervision d’un habitat connecté.

Le projet repose sur un microcontrôleur **ESP32**, plusieurs capteurs environnementaux et de sécurité, un système de communication **MQTT**, un backend web et une couche d’intelligence artificielle basée sur un modèle de langage comme **Mistral via Ollama**.

L’objectif principal est de permettre à l’utilisateur de surveiller son habitat en temps réel, contrôler des équipements connectés, recevoir des alertes en cas d’anomalie et interagir avec une IA capable de générer des suggestions contextuelles.

---

## 🎯 Objectifs du projet

Ce projet vise à :

- Concevoir une solution de **smart home connectée**.
- Collecter des données environnementales à l’aide de capteurs.
- Superviser la maison en temps réel via une interface web.
- Détecter les situations dangereuses comme le gaz, la fumée ou les intrusions.
- Piloter des équipements connectés à distance.
- Intégrer un **LLM** pour fournir des réponses intelligentes et contextuelles.
- Utiliser MQTT pour assurer une communication légère entre les composants IoT et le backend.
- Simuler le prototype sous **Wokwi** avant un éventuel déploiement physique.

---

## 🧠 Problématique

Les solutions domotiques classiques permettent souvent de contrôler certains appareils, mais elles manquent d’intelligence contextuelle et d’interaction naturelle avec l’utilisateur.

La problématique principale du projet est donc :

> Comment concevoir un système IoT intelligent capable de concilier confort, sécurité et interaction en langage naturel dans un habitat connecté ?

---

## 🏗️ Architecture générale

Le système est organisé autour de plusieurs couches principales :

### 1. Couche IoT

Cette couche est basée sur un microcontrôleur **ESP32** connecté à plusieurs capteurs et actionneurs.

Elle permet de collecter les données physiques de l’environnement et d’envoyer ces informations vers le système central via MQTT.

### 2. Couche communication

La communication entre l’ESP32, le backend et l’interface est assurée par le protocole **MQTT**.

MQTT est adapté aux projets IoT car il est léger, rapide et fonctionne selon le modèle publication/abonnement.

### 3. Couche backend

Le backend repose principalement sur :

- **Node.js**
- **Express.js**
- **Python**
- **FastAPI**

Node.js et Express.js gèrent la logique principale de l’application, tandis que FastAPI peut être utilisé pour l’intégration des modèles LLM.

### 4. Couche intelligence artificielle

Le projet intègre un modèle de langage, notamment **Mistral 7B via Ollama**, afin de générer des suggestions intelligentes à partir des données collectées.

Exemple : génération d’une suggestion de repas en fonction des conditions climatiques mesurées dans la maison.

### 5. Couche données

Le projet utilise deux types de bases de données :

- **PostgreSQL** : stockage des données structurées.
- **MongoDB** : stockage des événements, logs et données liées à la surveillance.

### 6. Interface web

L’interface web est développée avec :

- HTML
- CSS
- JavaScript

Elle permet de visualiser les données, contrôler les équipements, consulter les alertes et interagir avec les fonctionnalités IA.

---

## 🧩 Technologies utilisées

| Technologie | Rôle |
|-----------|------|
| ESP32 | Microcontrôleur principal |
| Wokwi | Simulation du circuit IoT |
| MQTT | Communication entre les composants |
| Node.js | Backend principal |
| Express.js | API backend |
| Python | Intégration IA et services complémentaires |
| FastAPI | API pour les modèles LLM |
| Ollama | Exécution locale du modèle IA |
| Mistral 7B | Modèle de langage utilisé |
| PostgreSQL | Base de données relationnelle |
| MongoDB | Stockage des logs et événements |
| HTML | Structure de l’interface |
| CSS | Design de l’interface |
| JavaScript | Interactions côté client |
| Font Awesome | Icônes de l’interface |

---

## 🔌 Composants matériels

### Microcontrôleur

- **ESP32**

L’ESP32 a été choisi pour son Wi-Fi intégré, son faible coût, sa consommation modérée et sa compatibilité avec Arduino et MicroPython.

---

## 📡 Capteurs utilisés

### 1. DHT22

Capteur utilisé pour mesurer :

- La température
- L’humidité

Il offre une meilleure précision que le DHT11 et convient bien aux applications domotiques.

### 2. Photorésistance

Capteur utilisé pour mesurer la luminosité ambiante.

Il permet d’adapter l’éclairage selon le niveau de lumière détecté.

### 3. MQ2 Gas Sensor

Capteur utilisé pour détecter :

- Le gaz
- La fumée
- Les fuites dangereuses

Il permet de renforcer la sécurité de l’habitat.

### 4. Capteur PIR

Capteur utilisé pour détecter les mouvements.

Il peut être utilisé pour identifier une présence ou une intrusion.

### 5. Capteur sonore

Capteur utilisé pour détecter certains bruits ambiants ou événements sonores.

---

## 💡 Actionneurs utilisés

### LEDs

Les LEDs permettent d’indiquer visuellement l’état du système :

- Activation d’un appareil
- Détection d’un danger
- Confirmation d’une commande
- Signal d’alerte

### Buzzer

Le buzzer permet d’émettre une alerte sonore en cas de danger, comme une fuite de gaz ou une détection suspecte.

---

## 📊 Fonctionnalités principales

### 1. Tableau de bord en temps réel

Le dashboard affiche les données environnementales de la maison :

- Température
- Humidité
- Luminosité
- Qualité de l’air
- Consommation énergétique

---

### 2. Gestion des équipements

L’utilisateur peut contrôler les équipements connectés depuis l’interface web :

- Climatiseur
- Lampe
- Télévision
- Réfrigérateur
- Système de sécurité

Chaque équipement peut être activé ou désactivé via un bouton de type toggle.

---

### 3. Synchronisation avec la maquette IoT

Les commandes envoyées depuis l’interface web sont transmises à l’ESP32.

Par exemple, lorsqu’un utilisateur active une lampe depuis le dashboard, la LED correspondante s’allume sur la maquette.

---

### 4. Surveillance de sécurité

Le système peut détecter :

- Une présence suspecte
- Une fuite de gaz
- Une mauvaise qualité de l’air
- Une situation anormale

Les alertes peuvent être affichées dans l’interface et signalées par les LEDs ou le buzzer.

---

### 5. Caméra de surveillance

L’interface comprend une section dédiée à la surveillance vidéo.

Elle permet de :

- Voir le flux caméra en temps réel
- Capturer une image
- Redémarrer la caméra
- Suivre les événements de sécurité

---

### 6. Journal de détection

Le système conserve un historique des événements détectés.

Exemples :

- Individu non identifié
- Personne autorisée
- Capture associée à un événement
- Heure de détection
- Type d’alerte

Ces logs peuvent être stockés dans MongoDB.

---

### 7. Suggestion intelligente par IA

Le projet intègre un LLM capable de générer des suggestions contextuelles.

Exemple :

L’utilisateur clique sur **“Générer une suggestion”** et le modèle IA analyse les conditions de la maison pour proposer une idée adaptée, comme une suggestion de repas.

La réponse peut contenir :

- Le nom du plat
- Les ingrédients
- Les étapes de préparation
- Le temps de cuisson
- Le niveau de difficulté

---

## 🔄 Fonctionnement global

1. Les capteurs collectent les données environnementales.
2. L’ESP32 lit les valeurs des capteurs.
3. Les données sont publiées vers un broker MQTT.
4. Le backend récupère les données MQTT.
5. Les données sont stockées dans PostgreSQL ou MongoDB.
6. L’interface web affiche les informations en temps réel.
7. L’utilisateur peut contrôler les équipements depuis le dashboard.
8. Les commandes sont envoyées vers l’ESP32.
9. Le LLM peut analyser le contexte et générer des suggestions intelligentes.
10. Les alertes sont affichées et enregistrées dans le journal de détection.

---

## 📡 Exemple de topics MQTT

Voici un exemple d’organisation possible des topics MQTT :

```txt
smart_home/temperature
smart_home/humidity
smart_home/light
smart_home/gas
smart_home/motion
smart_home/sound
smart_home/devices/lamp
smart_home/devices/ac
smart_home/devices/tv
smart_home/devices/fridge
smart_home/alerts
