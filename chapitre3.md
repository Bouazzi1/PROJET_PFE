\chapter{Méthodologie}
\label{chap:methodologie}

\section{Introduction}
\label{sec:methodo_intro}

À l'issue du chapitre précédent, les fondements théoriques et technologiques de Rihla-AI ont été établis, et les choix architecturaux ont été justifiés par rapport aux alternatives existantes. Le présent chapitre s'attache désormais à décrire la démarche méthodologique concrète mise en œuvre pour passer de ces choix conceptuels à un système fonctionnel. En suivant le cadre structurant de la méthodologie CRISP-DM, nous détaillerons successivement le workflow global du projet, la nature et la provenance des données mobilisées, les opérations de préparation et de transformation appliquées à ces données, puis les caractéristiques techniques des modèles d'intelligence artificielle retenus. Ce cheminement méthodologique garantit la traçabilité et la reproductibilité de l'ensemble du processus de développement.

\section{Workflow du projet}
\label{sec:methodo_workflow}

Le développement de Rihla-AI a été structuré selon un processus itératif en six phases, fidèle au cadre CRISP-DM introduit au chapitre précédent. Chaque phase a produit des livrables concrets, conditionnant l'entrée dans la phase suivante, tout en permettant des retours en arrière lors de la découverte de contraintes techniques imprévues — telle que l'incompatibilité de PaddleOCR avec le moteur d'inférence oneDNN en environnement Docker CPU, ayant conduit à substituer EasyOCR en cours de phase de modélisation.

\subsection{Phases du projet}
\label{subsec:phases_projet}

\begin{enumerate}
    \item \textbf{Compréhension métier} : Formalisation des cas d'usage prioritaires de l'agence Al-Rihla — réponse aux demandes WhatsApp et email, extraction automatique des données de passeport, recommandation personnalisée de programmes touristiques. Définition des critères de succès : temps de réponse inférieur à 5 secondes pour les requêtes conversationnelles, précision d'extraction OCR supérieure à 85\%, couverture omnicanale (WhatsApp + Email).

    \item \textbf{Compréhension des données} : Recensement des ressources informationnelles disponibles — catalogues de programmes touristiques, fiches de destinations, conditions de visa, exemples de passeports. Conception du schéma relationnel de la base de données PostgreSQL regroupant 12 tables et 11 programmes couvrant 8 destinations.

    \item \textbf{Préparation des données} : Structuration des textes de l'agence en segments exploitables par le pipeline RAG, vectorisation via \textbf{nomic-embed-text}, indexation dans Qdrant selon deux collections multilingues. Génération des données d'entraînement synthétiques pour le modèle de recommandation LightGBM.

    \item \textbf{Modélisation} : Implémentation des cinq composants intelligents — classificateur d'intentions, pipeline RAG, extracteur OCR, moteur de recommandation LightGBM, mémoire conversationnelle Redis. Exposition de ces services via une API FastAPI et orchestration par n8n.

    \item \textbf{Évaluation} : Campagne d'évaluation systématique couvrant les quatre axes du système — classification d'intentions (30 échantillons), pertinence RAG (métriques de relevance et de correspondance exacte), précision OCR (Field Accuracy, CER, MRZ Parse Rate), performance du recommandeur (NDCG@3, NDCG@5) et latences de bout en bout.

    \item \textbf{Déploiement} : Conteneurisation complète de l'écosystème via Docker Compose regroupant six services (FastAPI, Ollama, Qdrant, n8n, Redis, PostgreSQL), ainsi que la mise en service du tableau de bord Streamlit à destination du gestionnaire de l'agence.
\end{enumerate}

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_workflow_conversationnel.png
% Diagramme de flux : message client (WhatsApp/Email) → n8n → FastAPI →
% classificateur d'intentions → routage vers RAG / OCR / Recommandeur →
% réponse renvoyée via n8n au canal d'origine.
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:workflow_conversationnel} illustre le workflow de traitement d'un message entrant, depuis sa réception sur le canal d'origine jusqu'à la génération et l'acheminement de la réponse.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_workflow_conversationnel.png}
    \caption{Workflow de traitement d'un message Rihla-AI : du canal d'entrée (WhatsApp ou Email) à la réponse générée, via le classificateur d'intentions et les modules spécialisés.}
    \label{fig:workflow_conversationnel}
\end{figure}

\subsection{Planification temporelle}
\label{subsec:gantt}

La figure \ref{fig:gantt} présente le diagramme de Gantt du projet, détaillant la répartition des tâches et leur séquencement sur la durée du développement.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{diagramme_gantt_rihla.png}
    \caption{Diagramme de Gantt du projet Rihla-AI, illustrant les six phases CRISP-DM et les principaux livrables associés.}
    \label{fig:gantt}
\end{figure}

\section{Collection et description des données}
\label{sec:methodo_donnees}

Le système Rihla-AI mobilise trois catégories de données distinctes, chacune répondant à un besoin fonctionnel précis : des données textuelles non structurées alimentant le pipeline RAG, des données structurées gérées par la base de données relationnelle, et des données d'entraînement synthétiques destinées au modèle de recommandation.

\subsection{Données textuelles — Base de connaissances RAG}
\label{subsec:donnees_textuelles}

La base de connaissances RAG est constituée de l'ensemble des documents informatifs de l'agence Al-Rihla, rédigés en français et en arabe. Ces documents couvrent les quatre types de contenus suivants :

\begin{itemize}
    \item \textbf{Programmes touristiques} : descriptions détaillées des 11 programmes disponibles, incluant les itinéraires, les inclusions (vol, hébergement, visites), les tarifs par profil (adulte, enfant, groupe), les dates de départ et les conditions de réservation.
    \item \textbf{Fiches de destinations} : présentations des 8 destinations couvertes (pays, principales villes, sites d'intérêt, informations pratiques, météo, monnaie).
    \item \textbf{Conditions de visa et de voyage} : exigences documentaires par nationalité et par destination, délais d'obtention, coûts et procédures.
    \item \textbf{Hébergements et activités} : descriptions des hôtels partenaires et des activités proposées pour chaque programme.
\end{itemize}

L'ensemble de ces contenus a été segmenté en \textit{chunks} textuels, vectorisé et indexé dans deux collections Qdrant distinctes : \texttt{rihla\_fr} pour les contenus en français et \texttt{rihla\_ar} pour les contenus en arabe. Chaque collection contient 48 vecteurs, annotés par un champ de métadonnées \texttt{type} permettant le filtrage sémantique ciblé au moment de la récupération.

\subsection{Données structurées — Base de données PostgreSQL}
\label{subsec:donnees_postgresql}

Les données opérationnelles et transactionnelles de l'agence sont persistées dans une base de données relationnelle PostgreSQL 16, structurée autour de 12 tables. Le tableau \ref{tab:tables_postgresql} en présente l'inventaire et le rôle fonctionnel.

\begin{table}[H]
    \centering
    \caption{Inventaire des 12 tables de la base de données PostgreSQL de Rihla-AI.}
    \label{tab:tables_postgresql}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{3.5cm}|p{10cm}|}
    \hline
    \textbf{Table} & \textbf{Description} \\
    \hline
    \texttt{programmes} & Catalogue des 11 programmes touristiques avec tarifs, durée, destinations et conditions. \\
    \hline
    \texttt{destinations} & Fiches des 8 destinations (pays, villes, informations pratiques, monnaie). \\
    \hline
    \texttt{hotels} & Hébergements partenaires associés aux programmes (nom, catégorie, localisation). \\
    \hline
    \texttt{activites} & Activités proposées dans chaque programme (visite, excursion, loisir). \\
    \hline
    \texttt{conditions\_visa} & Exigences de visa par nationalité et par destination (type, délai, coût). \\
    \hline
    \texttt{programme\_destinations} & Table de liaison N-N entre programmes et destinations. \\
    \hline
    \texttt{clients} & Profils des voyageurs (nom, contact, langue, type, préférences). \\
    \hline
    \texttt{reservations} & Dossiers de réservation (programme, client, dates, statut, montant). \\
    \hline
    \texttt{conversations} & Sessions de conversation (identifiant, canal, horodatage, langue). \\
    \hline
    \texttt{messages} & Historique des échanges par conversation (contenu, rôle, horodatage). \\
    \hline
    \texttt{administrateurs} & Comptes du tableau de bord Streamlit (identifiant, rôle, droits). \\
    \hline
    \texttt{recommandations\_log} & Journal des recommandations émises (features utilisées, scores, résultat). \\
    \hline
    \end{tabular}
\end{table}

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_bdd_postgresql.png
% Diagramme Entité-Relation (ERD) représentant les 12 tables PostgreSQL,
% leurs clés primaires/étrangères et les cardinalités des relations.
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:erd_postgresql} illustre le modèle entité-relation de cette base de données, faisant apparaître les clés primaires, les clés étrangères et les cardinalités des associations entre entités.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_bdd_postgresql.png}
    \caption{Diagramme Entité-Relation de la base de données PostgreSQL de Rihla-AI (12 tables).}
    \label{fig:erd_postgresql}
\end{figure}

\subsection{Données d'entraînement — Modèle de recommandation}
\label{subsec:donnees_recommandation}

Le modèle de recommandation LightGBM a été entraîné sur des données synthétiques générées via le fichier \texttt{seed.sql}, reproduisant des profils de voyageurs réalistes et leurs interactions avec le catalogue de programmes. Chaque instance d'entraînement associe un profil voyageur à un programme, et est annotée d'un score de pertinence calculé selon un ensemble de règles métier (adéquation budget-prix, correspondance type de profil, compatibilité destination-préférence). Le jeu de données ainsi constitué comporte suffisamment d'exemples pour couvrir les 11 programmes disponibles sur l'ensemble des profils voyageurs types définis par l'agence. Le tableau \ref{tab:features_lightgbm} décrit les 22 caractéristiques (\textit{features}) extraites pour chaque instance.

\begin{table}[H]
    \centering
    \caption{Description des 22 features du modèle de recommandation LightGBM.}
    \label{tab:features_lightgbm}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{0.5cm}|p{4cm}|p{4.5cm}|p{5cm}|}
    \hline
    \textbf{\#} & \textbf{Feature} & \textbf{Type} & \textbf{Description} \\
    \hline
    \multicolumn{4}{|l|}{\textit{Groupe 1 — Profil voyageur (6 features)}} \\
    \hline
    1 & \texttt{budget} & Numérique (TND) & Budget total déclaré par le voyageur. \\
    \hline
    2 & \texttt{type\_profil} & Catégoriel & Type de groupe (solo, couple, famille, groupe). \\
    \hline
    3 & \texttt{nb\_personnes} & Entier & Nombre total de voyageurs dans le dossier. \\
    \hline
    4 & \texttt{nb\_enfants} & Entier & Nombre d'enfants inclus dans le groupe. \\
    \hline
    5 & \texttt{preference\_type} & Catégoriel & Préférence déclarée (aventure, culture, détente, plage, mixte). \\
    \hline
    6 & \texttt{langue} & Binaire & Langue de communication préférée (fr = 0, ar = 1). \\
    \hline
    \multicolumn{4}{|l|}{\textit{Groupe 2 — Attributs du programme (11 features)}} \\
    \hline
    7 & \texttt{prix\_adulte} & Numérique (TND) & Tarif par personne adulte pour ce programme. \\
    \hline
    8 & \texttt{nb\_jours} & Entier & Durée totale du programme en jours. \\
    \hline
    9 & \texttt{public\_cible} & Catégoriel & Public principal visé (famille, couple, solo, groupe). \\
    \hline
    10 & \texttt{nb\_destinations} & Entier & Nombre de destinations couvertes dans le programme. \\
    \hline
    11 & \texttt{inclus\_vol} & Binaire & Indique si le vol aller-retour est inclus (1 = oui). \\
    \hline
    12 & \texttt{inclus\_visa} & Binaire & Indique si les frais de visa sont inclus (1 = oui). \\
    \hline
    13 & \texttt{type\_hebergement} & Catégoriel & Catégorie d'hôtel proposé (3*, 4*, 5*, riad). \\
    \hline
    14 & \texttt{saison\_optimale} & Catégoriel & Période recommandée pour ce programme (été, hiver, printemps, toute saison). \\
    \hline
    15 & \texttt{type\_programme} & Catégoriel & Catégorie du programme (culturel, balnéaire, aventure, circuit, combiné). \\
    \hline
    16 & \texttt{rating\_moyen} & Numérique [0-5] & Note moyenne attribuée par les clients passés. \\
    \hline
    17 & \texttt{nb\_reservations} & Entier & Nombre total de réservations historiques pour ce programme. \\
    \hline
    \multicolumn{4}{|l|}{\textit{Groupe 3 — Features de compatibilité croisée (5 features)}} \\
    \hline
    18 & \texttt{budget\_ratio} & Numérique & Rapport budget déclaré / prix du programme. \\
    \hline
    19 & \texttt{profil\_match} & Binaire & Adéquation entre \texttt{type\_profil} et \texttt{public\_cible}. \\
    \hline
    20 & \texttt{preference\_match} & Binaire & Adéquation entre \texttt{preference\_type} et \texttt{type\_programme}. \\
    \hline
    21 & \texttt{saison\_match} & Binaire & Correspondance entre la saison de départ demandée et \texttt{saison\_optimale}. \\
    \hline
    22 & \texttt{enfants\_compat} & Binaire & Compatibilité du programme avec la présence d'enfants. \\
    \hline
    \end{tabular}
\end{table}

\section{Préparation et pré-traitement des données}
\label{sec:methodo_pretraitement}

\subsection{Pré-traitement des données textuelles pour le pipeline RAG}
\label{subsec:pretraitement_rag}

La transformation des documents bruts de l'agence en représentations vectorielles exploitables par le pipeline RAG s'est déroulée en trois étapes successives.

\paragraph{Segmentation en chunks.}
Les documents ont été découpés en segments textuels de taille fixe à l'aide d'un séparateur récursif (\textit{RecursiveCharacterTextSplitter}), avec une taille cible de \textbf{500 caractères} et un chevauchement (\textit{overlap}) de \textbf{50 caractères} entre segments consécutifs. Ce chevauchement garantit la continuité sémantique aux frontières de découpage, évitant qu'une phrase à cheval sur deux chunks ne se retrouve tronquée lors de la récupération. Chaque segment est enrichi d'un dictionnaire de métadonnées précisant son type (\texttt{programme}, \texttt{destination}, \texttt{hotel}, \texttt{activite}, \texttt{visa}), sa langue (\texttt{fr} ou \texttt{ar}) et son identifiant source.

\paragraph{Vectorisation.}
Chaque chunk est transformé en un vecteur dense de dimension 768 via le modèle \textbf{nomic-embed-text}, exécuté localement par Ollama. Ce modèle a été sélectionné pour ses performances sur les tâches de récupération sémantique multilingue, ainsi que pour sa compatibilité avec une inférence CPU sans GPU. La vectorisation est réalisée par lot (\textit{batch}) de 32 segments afin d'optimiser le débit.

\paragraph{Indexation dans Qdrant.}
Les vecteurs produits sont persistés dans deux collections Qdrant distinctes selon la langue du chunk : \texttt{rihla\_fr} et \texttt{rihla\_ar}. Chaque collection contient 48 points vectoriels à l'issue de l'indexation initiale. La mesure de similarité retenue est la \textbf{similarité cosinus}, standard pour les tâches de récupération sémantique. Le tableau \ref{tab:params_rag} récapitule les paramètres clés de cette phase.

\begin{table}[H]
    \centering
    \caption{Paramètres de segmentation, vectorisation et indexation du pipeline RAG.}
    \label{tab:params_rag}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{5cm}|p{8cm}|}
    \hline
    \textbf{Paramètre} & \textbf{Valeur} \\
    \hline
    Taille de chunk & 500 caractères \\
    \hline
    Chevauchement (overlap) & 50 caractères \\
    \hline
    Modèle d'embedding & nomic-embed-text \\
    \hline
    Dimension des vecteurs & 768 \\
    \hline
    Mesure de similarité & Cosinus \\
    \hline
    Collections Qdrant & \texttt{rihla\_fr} (français), \texttt{rihla\_ar} (arabe) \\
    \hline
    Nombre de vecteurs par collection & 48 \\
    \hline
    Top-K à la récupération & 5 segments \\
    \hline
    Filtrage par métadonnées & Oui — champ \texttt{type} (programme, destination, visa...) \\
    \hline
    \end{tabular}
\end{table}

\subsection{Ingénierie des caractéristiques pour la recommandation}
\label{subsec:pretraitement_recommandation}

La préparation des données pour le modèle LightGBM a nécessité une phase d'ingénierie des caractéristiques visant à construire des représentations numériques encodant à la fois le profil du voyageur, les attributs des programmes disponibles et les indicateurs de compatibilité croisée entre les deux. Les variables catégorielles (\texttt{type\_profil}, \texttt{preference\_type}, \texttt{public\_cible}, \texttt{type\_programme}, \texttt{type\_hebergement}, \texttt{saison\_optimale}) ont été encodées numériquement via un encodage ordinal simple, compatible avec LightGBM qui gère nativement les variables catégorielles sans nécessiter de \textit{one-hot encoding}. Les cinq features de compatibilité croisée (groupe 3 du tableau \ref{tab:features_lightgbm}) ont été calculées par des règles booléennes définies lors de la génération des données dans \texttt{seed.sql}. L'ensemble des données a ensuite été normalisé pour les variables numériques continues (\texttt{budget}, \texttt{prix\_adulte}, \texttt{nb\_jours}) afin d'améliorer la stabilité de l'entraînement, bien que LightGBM soit peu sensible à l'échelle des features en raison de sa nature arborescente.

\subsection{Pré-traitement des images pour l'OCR}
\label{subsec:pretraitement_ocr}

Les images de passeports transmises par les clients via WhatsApp ou email sont soumises à une séquence de pré-traitements légers avant d'être confiées aux moteurs OCR. Cette phase comprend : (i) une détection automatique du format et une conversion en mode RGB si l'image est reçue en mode RGBA ou en niveaux de gris ; (ii) un redimensionnement à une largeur cible de 2 000 pixels, préservant le ratio d'aspect, afin de garantir une résolution suffisante pour la reconnaissance des caractères fin de ligne dans la zone MRZ ; (iii) une normalisation des niveaux de gris par seuillage adaptatif (\textit{adaptive thresholding}) en amont du passage à pytesseract, afin de corriger les variations d'éclairage fréquentes dans les photos prises par smartphone. Ces étapes sont réalisées par la bibliothèque \textbf{Pillow} en Python et n'impliquent aucune dépendance GPU.

\section{Les modèles utilisés}
\label{sec:methodo_modeles}

\subsection{Classificateur d'intentions}
\label{subsec:modele_intent}

La première étape du traitement de tout message entrant consiste à déterminer l'intention de l'utilisateur afin de router la requête vers le module compétent. Ce classificateur est implémenté par correspondance lexicale pondérée (\textit{keyword matching}) sur la base de cinq classes d'intentions, détaillées dans le tableau \ref{tab:intent_classes}. Cette approche légère — ne faisant appel à aucun modèle d'apprentissage — a été privilégiée en raison de sa latence quasi nulle (inférieure à 1 ms mesurée lors des évaluations) et de sa précision suffisante pour les types de requêtes attendus dans le contexte d'une agence de voyages.

\begin{table}[H]
    \centering
    \caption{Classes d'intentions du classificateur Rihla-AI et exemples de déclencheurs lexicaux.}
    \label{tab:intent_classes}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{2.5cm}|p{5cm}|p{6.5cm}|}
    \hline
    \textbf{Intention} & \textbf{Module cible} & \textbf{Exemples de déclencheurs} \\
    \hline
    \texttt{general} & Pipeline RAG (collection selon langue) & « bonjour », « renseignements », « informations », question ouverte. \\
    \hline
    \texttt{programme} & Pipeline RAG avec filtre \texttt{type=programme} & « programme », « voyage », « séjour », « formule », « prix ». \\
    \hline
    \texttt{reservation} & RAG + base PostgreSQL & « réserver », « réservation », « disponibilité », « dossier ». \\
    \hline
    \texttt{ocr} & Service OCR (EasyOCR + passporteye) & « passeport », « pièce d'identité », « document », \textit{[image jointe]}. \\
    \hline
    \texttt{recommandation} & Moteur LightGBM + LLM & « recommandez-moi », « conseillez », « quel programme pour », « mon profil ». \\
    \hline
    \end{tabular}
\end{table}

\subsection{Pipeline RAG — Qwen 2.5 7B + nomic-embed-text + Qdrant}
\label{subsec:modele_rag}

Le cœur conversationnel de Rihla-AI repose sur un pipeline RAG combinant trois composants : le modèle d'embedding \textbf{nomic-embed-text} (vectorisation de la requête entrante), la base vectorielle \textbf{Qdrant} (récupération des segments les plus pertinents par similarité cosinus, Top-5), et le LLM \textbf{Qwen 2.5 7B} (génération de la réponse ancrée dans le contexte récupéré). L'interaction avec le LLM est structurée par un \textit{system prompt} spécifiant son rôle d'agent de l'agence Al-Rihla, ses contraintes de réponse (fidélité aux données de l'agence, refus des sujets hors-périmètre, courtoisie professionnelle), et la structure attendue de ses réponses.

Le pipeline RAG est appelé selon deux variantes :

\begin{itemize}
    \item \textbf{RAG général} : requête soumise sans filtre de métadonnées, la recherche portant sur l'intégralité de la collection concernée. Utilisé pour les intentions \texttt{general}.
    \item \textbf{RAG filtré par type} : la requête est accompagnée d'un filtre Qdrant restreignant la recherche aux chunks du type correspondant à l'intention détectée (\texttt{programme}, \texttt{destination}, etc.). Cette stratégie améliore sensiblement la précision des résultats pour les requêtes thématiques ciblées.
\end{itemize}

La gestion de la mémoire conversationnelle est assurée par \textbf{Redis}, qui maintient pour chaque session une fenêtre glissante des 10 derniers échanges, avec un TTL (\textit{Time-To-Live}) de 24 heures. Ce contexte est injecté dans le prompt à chaque tour de conversation, permettant au LLM de maintenir la cohérence des échanges sur l'ensemble de la session.

\subsection{Pipeline OCR — EasyOCR, pytesseract, passporteye}
\label{subsec:modele_ocr}

Le service OCR de Rihla-AI suit un pipeline à deux branches parallèles, synchronisées en aval vers une structure de sortie unifiée. La branche \textbf{principale} confie l'image au moteur \textbf{EasyOCR}, fondé sur une architecture CRNN (\textit{Convolutional Recurrent Neural Network}) avec mécanisme d'attention, capable de reconnaître du texte dans plus de 80 langues. En cas d'échec ou d'indisponibilité d'EasyOCR, la branche de \textbf{repli} bascule automatiquement vers \textbf{pytesseract}, moteur OCR traditionnel basé sur Tesseract. Parallèlement et indépendamment de ces deux branches, \textbf{passporteye} est systématiquement invoqué pour localiser et décoder la Zone de Lecture Machine (MRZ) du passeport selon la norme ISO 9303. La MRZ, encodée sur deux lignes de 44 caractères chacune, fournit avec une fiabilité maximale les informations d'identité structurées : nom, prénom, nationalité, date de naissance, numéro de passeport et date d'expiration. Les résultats des deux branches sont fusionnés dans un dictionnaire structuré, retourné au client sous forme de JSON normalisé.

\subsection{Modèle de recommandation — LightGBM}
\label{subsec:modele_lightgbm}

Le moteur de recommandation est fondé sur l'algorithme \textbf{LightGBM} (\textit{Light Gradient Boosting Machine}), configuré en mode \textit{LambdaRank} pour l'optimisation directe d'une métrique de classement. Les principaux hyperparamètres retenus sont : un taux d'apprentissage (\textit{learning rate}) de 0,05, un nombre d'estimateurs de 100 arbres, une profondeur maximale de 6 niveaux, et la métrique \textbf{NDCG} (\textit{Normalized Discounted Cumulative Gain}) comme critère d'optimisation. À la suite de l'entraînement, le modèle est persisté sous format \texttt{.pkl} et chargé en mémoire au démarrage du service FastAPI, garantissant une inférence en temps quasi réel pour chaque requête de recommandation. La figure \ref{fig:lightgbm_workflow} illustre la chaîne complète du service de recommandation, depuis la réception du profil voyageur jusqu'à la génération de la réponse textuelle personnalisée par le LLM.

\begin{table}[H]
    \centering
    \caption{Hyperparamètres du modèle LightGBM et performances obtenues.}
    \label{tab:lightgbm_params}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{5.5cm}|p{8cm}|}
    \hline
    \textbf{Paramètre / Métrique} & \textbf{Valeur} \\
    \hline
    Algorithme & LightGBM — mode LambdaRank \\
    \hline
    Nombre d'estimateurs & 100 \\
    \hline
    Taux d'apprentissage & 0,05 \\
    \hline
    Profondeur maximale & 6 \\
    \hline
    Nombre de features & 22 \\
    \hline
    Métrique d'optimisation & NDCG \\
    \hline
    \textbf{NDCG@5 (évaluation)} & \textbf{1,0} \\
    \hline
    \textbf{NDCG@3 (évaluation)} & \textbf{1,0} \\
    \hline
    \textbf{RMSE} & \textbf{5,5 × 10\textsuperscript{−5}} \\
    \hline
    \textbf{MAE} & \textbf{3,1 × 10\textsuperscript{−5}} \\
    \hline
    \end{tabular}
\end{table}

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_lightgbm_workflow.png  (optionnel — peut être remplacé par la table)
% Flux : profil voyageur → extraction des 22 features → LightGBM →
% scores de pertinence → tri → Top-3 programmes → LLM (justification) →
% réponse textuelle personnalisée.
% ────────────────────────────────────────────────────────────────────────────

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_lightgbm_workflow.png}
    \caption{Chaîne du service de recommandation Rihla-AI : du profil voyageur aux recommandations justifiées par le LLM.}
    \label{fig:lightgbm_workflow}
\end{figure}

\section{Conclusion}
\label{sec:methodo_conclusion}

Ce troisième chapitre a présenté la démarche méthodologique complète mise en œuvre pour concevoir et construire les composants intelligents de Rihla-AI. Le workflow du projet, structuré selon les six phases CRISP-DM, a fourni un cadre itératif permettant de naviguer entre les contraintes techniques découvertes en cours de développement — comme la substitution de PaddleOCR par EasyOCR — sans déstabiliser l'architecture globale. L'analyse des données a mis en évidence la diversité des sources mobilisées : textes de l'agence segmentés et vectorisés dans Qdrant, données structurées persistées dans PostgreSQL, et données synthétiques d'entraînement pour le recommandeur LightGBM. Enfin, la description technique des cinq modèles utilisés — classificateur d'intentions, pipeline RAG, extracteur OCR, moteur LightGBM et mémoire conversationnelle Redis — a précisé les paramètres, les algorithmes et les stratégies de prétraitement qui fondent les performances du système.

Le chapitre suivant présentera les résultats de l'évaluation expérimentale conduite sur chacun de ces composants, en s'appuyant sur des métriques quantitatives standardisées afin de valider objectivement la pertinence des choix méthodologiques effectués.
