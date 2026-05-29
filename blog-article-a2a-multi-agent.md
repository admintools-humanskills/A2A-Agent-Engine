# Protocole A2A : orchestrer 7 agents IA spécialisés pour un concierge de voyage autonome

## Un seul agent IA ne suffit pas

Aujourd'hui, la majorité des projets d'intelligence artificielle reposent sur un modèle simple : **1 agent = 1 LLM + des outils + un contexte**. Ce schéma fonctionne remarquablement bien tant que le périmètre reste circonscrit — un chatbot de support, un assistant de rédaction, un outil de recherche documentaire. Mais dès qu'on cherche à couvrir un parcours utilisateur complet — réserver un hôtel, un vol, un train, trouver un restaurant, acheter des billets de spectacle, souscrire une assurance — les limites apparaissent brutalement. Le contexte sature, les instructions se contredisent, et l'agent généraliste finit par produire des réponses approximatives parce qu'il essaie de tout faire sans exceller dans aucun domaine. C'est le problème du **context overflow** : plus on empile de compétences dans un seul agent, plus sa performance se dégrade sur chacune d'entre elles.

Le constat est le même que dans n'importe quelle organisation humaine. **Aucune entreprise performante ne confie l'intégralité de ses opérations à un employé unique.** On recrute des spécialistes — un revenue manager pour l'hôtellerie, un agent de réservation pour les vols, un sommelier pour la restauration — et on les coordonne via un chef d'orchestre qui comprend le besoin global du client et délègue chaque tâche au bon expert. C'est précisément cette logique que le protocole A2A permet de reproduire dans le monde des agents IA : une équipe de spécialistes autonomes, coordonnés par un concierge intelligent qui sait à qui parler et quoi demander. Le problème, c'est qu'aucun framework actuel ne propose de mécanisme natif de délégation entre agents développés avec des technologies différentes. LangGraph ne sait pas parler à CrewAI, CrewAI ne sait pas parler à Google GenAI. Chaque écosystème reste cloisonné — jusqu'à A2A.

---

## A2A : le "HTTP des agents IA"

Le protocole **A2A (Agent-to-Agent)**, développé par Google en open source, est un standard de communication inter-agents conçu pour être aussi universel que HTTP l'est pour le web. Son principe est simple : **n'importe quel agent, quel que soit le framework qui l'a produit, peut découvrir, contacter et collaborer avec n'importe quel autre agent** dès lors qu'ils implémentent le même protocole. C'est la promesse d'une interopérabilité totale, et elle fonctionne en production.

Le protocole repose sur quatre concepts fondamentaux. L'**AgentCard** est la carte d'identité de l'agent : un fichier JSON exposé sur l'endpoint standard `/.well-known/agent.json` qui décrit son nom, ses compétences, son URL et ses capacités. C'est le mécanisme de **Discovery** — n'importe quel agent peut scanner un réseau et découvrir automatiquement les agents disponibles, exactement comme un navigateur découvre les services d'un domaine. Le **SendMessage** est le format de communication : une requête JSON-RPC contenant un `messageId`, un `contextId` et le contenu du message, envoyée en POST à l'agent cible. Enfin, la **Task** est l'unité de travail : chaque requête crée une tâche avec un statut (`submitted`, `working`, `completed`) et des **Artifacts** — les résultats structurés que l'agent renvoie une fois son travail terminé. C'est aussi simple que ça : Discovery → SendMessage → Task + Artifacts. **Pas de SDK propriétaire, pas de couplage fort, pas de dépendance à un framework spécifique.** Un agent LangGraph, un agent CrewAI et un agent Google GenAI peuvent collaborer sur la même requête utilisateur sans même savoir quel framework les autres utilisent.

---

## L'architecture : un concierge orchestrant 7 spécialistes

L'**Elevate Concierge** est une implémentation complète du protocole A2A qui orchestre **7 agents spécialisés** développés avec **3 frameworks différents**, déployés sur **Google Cloud Run** et coordonnés par un concierge central propulsé par **Gemini 2.5 Flash** sur **Vertex AI Agent Engine**. L'architecture se découpe en trois couches distinctes.

La **couche client** est une interface pixel art interactive — un village NES animé avec un panneau de chat — qui communique en temps réel via WebSocket avec le backend. La **couche backend** repose sur FastAPI pour le serveur web et sur Google ADK (Agent Development Kit) pour la logique d'orchestration du concierge. Enfin, la **couche agents** comprend les 7 services spécialisés, chacun déployé comme un container indépendant sur Cloud Run, communiquant exclusivement via le protocole A2A.

Les **7 agents** couvrent l'ensemble du parcours voyage et conciergerie :

- **Hotel Agent** (LangGraph) — Réservations hôtelières dans 5 villes européennes, 3 à 5 étoiles, avec prix et disponibilités
- **Train Agent** (LangGraph) — Billets de train Eurostar, TGV, AVE, en 1ère ou 2nde classe
- **Flight Agent** (CrewAI) — Réservations de vols sur plus de 20 routes européennes, Economy, Business ou First
- **Events Agent** (CrewAI) — Billetterie concerts, football, théâtre
- **Restaurant Agent** (Google GenAI) — Restaurants étoilés Michelin et tables gastronomiques
- **Boutique Agent** (Google GenAI) — Merchandising et tenues formelles (chemises, costumes, smokings, cravates, nœuds papillon, pochettes, chaussures de ville)
- **Insurance Agent** (Google GenAI) — Produits BNP Paribas Cardif (assurance emprunteur, habitation, prévoyance, épargne retraite)

**3 frameworks, 7 agents, 1 protocole = interopérabilité totale.** C'est la démonstration concrète que A2A tient sa promesse : le framework de chaque agent est un choix d'implémentation interne, invisible pour les autres agents et pour le concierge.

---

## Les briques technologiques

L'ensemble de la plateforme repose sur une stack cloud-native entièrement managée, sans infrastructure à provisionner manuellement.

Au cœur du système, le **concierge** est construit avec **Google ADK** (Agent Development Kit) et propulsé par **Gemini 2.5 Flash**. C'est lui qui analyse chaque requête utilisateur, identifie le ou les agents pertinents, enrichit le contexte de la tâche (nom complet du client, ville, dates, nombre de voyageurs, préférences), et synthétise les réponses des agents en une réponse cohérente pour l'utilisateur. Il est déployé sur **Vertex AI Agent Engine**, le service managé de Google pour l'hébergement d'agents en production.

Côté agents spécialisés, trois frameworks se répartissent le travail selon leurs forces respectives. **LangGraph** — le framework de LangChain pour les agents à état — gère les agents Hotel et Train, qui nécessitent des machines à états avec checkpointing pour suivre les étapes de réservation. **CrewAI** — un framework d'orchestration par équipes — propulse les agents Flight et Events, qui bénéficient de sa logique de délégation intra-crew. **Google GenAI** — l'API directe vers Gemini — alimente les agents Restaurant, Boutique et Insurance, qui fonctionnent en mode appel-réponse simple sans état intermédiaire.

L'interface utilisateur repose sur **FastAPI** pour le serveur backend, **WebSocket** pour le streaming temps réel des événements, et un **Canvas HTML5** en JavaScript vanilla pour le rendu pixel art — sprites, animations de marche, bâtiments, PNJ réactifs. Le tout sans aucune dépendance frontend (pas de React, pas de framework CSS), dans un style **palette NES authentique** de 35 couleurs.

L'infrastructure de déploiement utilise **Google Cloud Run** pour les 7 agents (conteneurs Docker avec auto-scaling et pay-per-request) et **Vertex AI** pour le concierge. Le script `deploy_agents_cloudrun.sh` déploie les 7 agents en une commande, et `deploy_to_agent_engine.py` publie le concierge sur Vertex AI.

---

## Le workflow de bout en bout

Le processus d'exécution d'une requête utilisateur se déroule en **6 étapes**, du message initial à la réponse finale, en **2 à 5 secondes**.

**Étape 1 — Discovery.** Au démarrage, le concierge récupère les AgentCards de tous les agents disponibles via l'`A2ACardResolver`. Il connaît désormais les compétences, les URLs et les capacités de chaque spécialiste. Cette découverte est automatique et standardisée : ajouter un nouvel agent revient à déployer un service qui expose son `/.well-known/agent.json`.

**Étape 2 — Routing.** L'utilisateur envoie sa requête : *"Réserve-moi un hôtel 4 étoiles à Madrid pour 2 personnes du 15 au 17 mars."* Le LLM du concierge (Gemini 2.5 Flash) analyse le message, identifie qu'il s'agit d'une réservation hôtelière, et sélectionne le `hotel_agent` comme destinataire.

**Étape 3 — Delegation.** Le concierge appelle sa fonction `send_task` qui envoie une requête JSON-RPC POST à l'URL du hotel_agent sur Cloud Run. Le message contient toutes les informations nécessaires : nom du client, ville, dates de check-in/check-out, nombre de voyageurs, préférences. L'agent distant est **stateless** — chaque appel est complet et autonome, sans dépendance à un historique de conversation.

**Étape 4 — Execution.** Le hotel_agent reçoit la tâche via A2A, exécute sa logique LangGraph (recherche dans le catalogue, calcul des prix, vérification des disponibilités), et produit un résultat structuré : 3 options d'hôtels avec noms, étoiles, prix par nuit et coût total.

**Étape 5 — Response.** L'agent renvoie une Task avec le statut `completed` et des Artifacts contenant les détails de réservation. Le concierge extrait le texte, le synthétise et formule une réponse naturelle pour l'utilisateur.

**Étape 6 — UI Stream.** Tout au long du processus, des événements WebSocket sont envoyés au frontend en temps réel : `agent_thinking` (le LLM analyse), `agent_call` (délégation en cours vers un agent spécifique), `agent_response` (résultats reçus), `final` (réponse complète). Ces événements alimentent à la fois le panneau de chat et les animations du village pixel art.

---

## L'UI Pixel Art : rendre l'invisible visible

L'orchestration multi-agents pose un problème fondamental d'expérience utilisateur : **c'est une boîte noire.** L'utilisateur envoie un message, attend quelques secondes, et reçoit une réponse — sans jamais comprendre ce qui s'est passé entre les deux. Quel agent a travaillé ? Combien de temps ? Pourquoi celui-ci et pas un autre ? Cette opacité est un frein à l'adoption et à la confiance, particulièrement auprès des décideurs non techniques qui doivent valider l'investissement dans ce type d'architecture.

La solution : **transformer l'orchestration en une scène visuelle interactive.** L'Elevate Concierge rend chaque étape du processus visible à travers un village pixel art en style NES, affiché en temps réel à côté du panneau de chat. Chaque agent spécialisé est représenté par un **bâtiment** dans le village — un hôtel, un aéroport, une gare, un restaurant, une boutique, un bureau d'assurance. Le personnage du concierge se tient au centre de la place, et lorsqu'une requête arrive, **il marche physiquement jusqu'au bâtiment de l'agent contacté.** Le PNJ de l'agent réagit avec un indicateur **"!"** lorsque la tâche est terminée. En parallèle, le panneau de chat affiche chaque étape : analyse en cours → délégation vers hotel_agent → réponse reçue.

L'impact est immédiat : **même un public non technique comprend instantanément quel agent a travaillé, pourquoi, et combien de temps ça a pris.** L'orchestration cesse d'être un concept abstrait pour devenir un spectacle visuel, intuitif et engageant. C'est un outil de démonstration redoutable pour convaincre des parties prenantes de la valeur d'une architecture multi-agents.

---

## Pourquoi ça change tout

Les bénéfices de cette architecture dépassent largement le cadre d'un POC de voyage. Le protocole A2A résout un problème structurel de l'écosystème IA actuel : **le cloisonnement des frameworks.** Aujourd'hui, choisir LangGraph, CrewAI ou Google GenAI pour un agent, c'est s'enfermer dans un écosystème. Avec A2A, ce choix devient un détail d'implémentation — on utilise le meilleur framework pour chaque cas d'usage, et le protocole garantit l'interopérabilité. C'est la fin du vendor lock-in pour les agents IA.

Les agents étant **stateless**, chaque appel est indépendant et complet. Cela offre une **scalabilité native** — Cloud Run auto-scale chaque agent indépendamment en fonction de la charge — et une **résilience** par conception : si un agent est temporairement indisponible, les autres continuent de fonctionner. Le concierge peut même **déléguer en parallèle** à plusieurs agents simultanément quand la requête le justifie (par exemple : "Réserve un hôtel et un vol pour Madrid" déclenche hotel_agent et flight_agent en même temps).

L'**enrichissement automatique du contexte** par le concierge est un autre avantage décisif. Les agents distants n'ont pas accès à l'historique de la conversation — c'est le concierge qui se charge d'inclure toutes les informations pertinentes dans chaque tâche déléguée (nom du client, dates, ville, préférences). Cela élimine les allers-retours et les questions de clarification, accélérant considérablement le temps de résolution.

Enfin, le support **multilingue natif** — le concierge répond dans la langue de l'utilisateur (français, anglais, espagnol) — et le **temps de réponse de 2 à 5 secondes** pour une orchestration complète multi-agents rendent cette architecture directement exploitable en production.

---

## Passez à l'action

**A2A est production-ready dès aujourd'hui.** Le protocole est open source, maintenu par Google, et l'SDK Python (`a2a-sdk`) est disponible sur PyPI. L'Elevate Concierge démontre que le déploiement d'une architecture multi-agents complète — du développement au Cloud Run — est une affaire de jours, pas de mois. Et ce n'est que le début : les protocoles **ACP (Agent Commerce Protocol)** et **UCP (Universal Commerce Protocol)** arrivent pour permettre les paiements directement dans les workflows d'agents IA, ouvrant la voie à des transactions autonomes de bout en bout.

L'architecture multi-agents A2A s'applique à tous les secteurs :

- **Banque & Assurance** — Orchestrer souscription, conformité, tarification et gestion de sinistres entre agents spécialisés
- **Travel & Hospitality** — Concierge IA de bout en bout : vol + hôtel + activités + paiement
- **E-commerce & Retail** — Agents shopping + recommandation + logistique + support client

La roadmap recommandée est progressive. **Trimestre 1 : POC Multi-Agent** — implémenter A2A avec 2-3 agents métier sur un cas d'usage concret. **Trimestre 2 : Production** — ajouter monitoring, authentification et scaling. **Trimestre 3 : Commerce AI** — intégrer ACP/UCP pour les paiements autonomes. Les early adopters auront **12 à 18 mois d'avance** sur la compétition. La stack complète — **Google ADK + Gemini 2.5 Flash + A2A + Cloud Run + Vertex AI** — est prête à être déployée et adaptée à votre métier. Parlons-en : planifions un atelier de cadrage.

---

---

# Digest

**Et si vos agents IA pouvaient collaborer entre eux comme une équipe de spécialistes, quel que soit le framework qui les a produits ?** C'est exactement ce que permet le protocole A2A de Google, implémenté de bout en bout dans l'Elevate Concierge : un concierge de voyage propulsé par Gemini 2.5 Flash qui orchestre 7 agents spécialisés — hôtel, vol, train, événements, restaurant, boutique et assurance — développés avec 3 frameworks différents (LangGraph, CrewAI, Google GenAI) et déployés sur Cloud Run. Chaque agent expose sa carte d'identité (AgentCard) sur un endpoint standard, le concierge les découvre automatiquement, leur délègue des tâches enrichies avec le contexte complet du client, et synthétise les réponses en 2 à 5 secondes. Le tout est visualisé en temps réel dans une interface pixel art en style NES où le personnage du concierge marche physiquement vers le bâtiment de l'agent contacté — rendant l'orchestration invisible instantanément compréhensible, même pour un public non technique.

**A2A est le "HTTP des agents IA" : un standard ouvert, interopérable et production-ready.** Il résout le problème structurel du cloisonnement des frameworks — LangGraph, CrewAI, Google GenAI collaborent sans même savoir quel framework les autres utilisent. Les agents sont stateless par conception, ce qui offre une scalabilité native (Cloud Run auto-scale chaque agent indépendamment) et une résilience à toute épreuve. Le concierge peut déléguer en parallèle à plusieurs agents simultanément, enrichit automatiquement chaque tâche avec les informations de la conversation, et répond dans la langue de l'utilisateur. Avec l'arrivée prochaine des protocoles ACP et UCP pour les paiements autonomes, l'architecture multi-agents A2A est le socle sur lequel construire dès maintenant. Banque, travel, e-commerce : les early adopters auront 12 à 18 mois d'avance. La stack — Google ADK, Gemini 2.5 Flash, A2A, Cloud Run, Vertex AI — est prête. Parlons-en.
