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

Cette section décrit en détail le fonctionnement interne de chacun des quatre composants intelligents de Rihla-AI, en suivant systématiquement la chaîne de traitement de l'entrée jusqu'à la sortie. Pour chaque modèle, un schéma illustratif est proposé afin de permettre au lecteur de visualiser les transformations successives appliquées aux données.

\subsection{Classificateur d'intentions}
\label{subsec:modele_intent}

\paragraph{Principe de fonctionnement.}
La première étape du traitement d'un message entrant consiste à identifier ce que l'utilisateur cherche à accomplir — son \textit{intention} — afin d'aiguiller automatiquement la requête vers le module compétent. Ce classificateur repose sur une approche de \textbf{correspondance lexicale pondérée} (\textit{keyword matching}) : le message reçu est d'abord normalisé (conversion en minuscules, suppression des accents) puis parcouru à la recherche de termes déclencheurs prédéfinis, organisés en cinq dictionnaires correspondant aux cinq classes d'intentions du système.

\paragraph{Algorithme de décision.}
Pour chaque classe d'intention, un compteur de correspondances est incrémenté à chaque occurrence d'un terme déclencheur dans le message. La classe présentant le plus grand nombre de correspondances est retenue. En l'absence de toute correspondance — pour un message de salutation ou une question très générale —, l'intention par défaut \texttt{general} est attribuée, garantissant qu'aucune requête ne reste sans traitement. La détection de la présence d'une pièce jointe de type image déclenche systématiquement l'intention \texttt{ocr}, indépendamment du texte accompagnateur.

\paragraph{Exemple concret.}
Considérons le message : \textit{« Bonjour, je voudrais réserver un séjour en Turquie pour ma famille »}. Après normalisation, le système détecte les termes \texttt{« reserver »} et \texttt{« sejour »}. Le terme \texttt{« reserver »} appartient au dictionnaire \texttt{reservation} (score : 1), tandis que \texttt{« sejour »} appartient au dictionnaire \texttt{programme} (score : 1). En cas d'égalité, la priorité est accordée à \texttt{programme} selon l'ordre de préférence défini par les règles métier. La requête est alors routée vers le pipeline RAG avec le filtre \texttt{type=programme}.

\begin{table}[H]
    \centering
    \caption{Classes d'intentions du classificateur Rihla-AI, modules cibles et exemples de déclencheurs lexicaux.}
    \label{tab:intent_classes}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{2.5cm}|p{4.5cm}|p{7cm}|}
    \hline
    \textbf{Intention} & \textbf{Module cible} & \textbf{Exemples de déclencheurs} \\
    \hline
    \texttt{general} & Pipeline RAG — collection complète & « bonjour », « renseignements », « informations », question ouverte sans mot-clé spécifique. \\
    \hline
    \texttt{programme} & Pipeline RAG — filtre \texttt{type=programme} & « programme », « voyage », « séjour », « formule », « offre », « prix », « circuit ». \\
    \hline
    \texttt{reservation} & Pipeline RAG + base PostgreSQL & « réserver », « réservation », « disponibilité », « dossier », « confirmer », « acompte ». \\
    \hline
    \texttt{ocr} & Service OCR (EasyOCR + passporteye) & « passeport », « pièce d'identité », « document », \textit{[présence d'une image jointe]}. \\
    \hline
    \texttt{recommandation} & Moteur LightGBM + LLM & « recommandez-moi », « conseillez », « quel programme pour », « mon budget est de », « nous sommes ». \\
    \hline
    \end{tabular}
\end{table}

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_intent_classifier.png
% Flux : message brut → normalisation (minuscules + accents) →
% scan des 5 dictionnaires de mots-clés → compteurs de score →
% sélection de l'intention gagnante (ou fallback → general) →
% flèche de routage vers le module cible (RAG / OCR / LightGBM).
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:intent_classifier} illustre le cheminement complet d'un message au travers du classificateur, depuis la réception du texte brut jusqu'à la décision de routage.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_intent_classifier.png}
    \caption{Flux de classification d'intentions dans Rihla-AI : normalisation du texte, correspondance lexicale sur cinq dictionnaires, sélection de l'intention et routage vers le module compétent.}
    \label{fig:intent_classifier}
\end{figure}

\subsection{Pipeline RAG — Qwen 2.5 7B + nomic-embed-text + Qdrant}
\label{subsec:modele_rag}

\paragraph{Vue d'ensemble.}
Le pipeline RAG (\textit{Retrieval-Augmented Generation}) est le cœur conversationnel de Rihla-AI. Son rôle est de produire des réponses précises, fondées sur les données réelles de l'agence, en évitant les hallucinations que génèrerait un LLM consulté sans contexte factuel. Pour ce faire, il n'interroge jamais le LLM directement : il lui soumet toujours un \textit{prompt assemblé} contenant à la fois la question de l'utilisateur, les passages pertinents extraits de la base de connaissances et le contexte de la conversation en cours.

\paragraph{Étape 1 — Vectorisation de la requête.}
À la réception du message, celui-ci est transformé en un vecteur numérique dense de dimension 768 par le modèle \textbf{nomic-embed-text}, exécuté localement via Ollama. Ce vecteur capture la signification sémantique du message — deux formulations différentes d'une même question produisent des vecteurs très proches — indépendamment de la formulation exacte utilisée par le client.

\paragraph{Étape 2 — Récupération dans Qdrant.}
Le vecteur de la requête est comparé par \textbf{similarité cosinus} à l'ensemble des 48 vecteurs de la collection correspondant à la langue du message (\texttt{rihla\_fr} ou \texttt{rihla\_ar}). Les 5 segments les plus proches sémantiquement (\textit{Top-5}) sont récupérés. Selon la variante du pipeline activée par l'intention détectée, cette recherche peut être restreinte à un sous-ensemble de chunks filtrés par leur champ de métadonnées \texttt{type} :

\begin{itemize}
    \item \textbf{RAG général} (intention \texttt{general}) : aucun filtre, recherche sur l'intégralité de la collection.
    \item \textbf{RAG filtré par type} (intentions \texttt{programme}, \texttt{reservation}) : filtre Qdrant restreignant la recherche aux seuls chunks de type \texttt{programme} ou \texttt{destination}, augmentant la précision thématique.
\end{itemize}

\paragraph{Étape 3 — Récupération du contexte conversationnel.}
En parallèle, le service consulte \textbf{Redis} pour récupérer les 10 derniers échanges de la session en cours, identifiée par un identifiant de conversation unique. Cette fenêtre d'historique est essentielle pour la cohérence des échanges multi-tours : elle permet au LLM de comprendre les références anaphoriques (« ce programme », « cette destination ») et de maintenir la continuité thématique sans demander à l'utilisateur de se répéter. Si aucun historique n'existe (première interaction), Redis renvoie un contexte vide et une nouvelle session est initialisée avec un TTL de 24 heures.

\paragraph{Étape 4 — Assemblage du prompt et génération.}
Les trois sources d'information — \textit{system prompt} d'identité, historique Redis, chunks récupérés de Qdrant — sont assemblées en un prompt structuré soumis à \textbf{Qwen 2.5 7B}. Le \textit{system prompt} définit le rôle du modèle (« Tu es l'assistant de l'agence de voyages Al-Rihla, spécialisée en Tunisie »), ses contraintes (répondre uniquement à partir des données fournies, refuser les demandes hors-périmètre, utiliser la même langue que le client) et le format attendu. Le LLM génère alors une réponse ancrée dans les faits de l'agence, que Redis enregistre immédiatement pour alimenter les tours de conversation suivants.

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_rag_complet.png
% Flux détaillé en 4 étapes :
% [Message + session_id]
%   → (1) nomic-embed-text → vecteur 768-dim
%   → (2) Qdrant (rihla_fr ou rihla_ar, avec/sans filtre type) → Top-5 chunks
%   → (3) Redis → historique 10 derniers échanges (ou vide si nouvelle session)
%   → (4) Assemblage du prompt :
%         [ System prompt | Historique | Chunks contexte | Question ]
%         → Qwen 2.5 7B → réponse texte
%   → Redis : sauvegarde du nouvel échange (TTL 24h)
%   → Réponse renvoyée au client
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:rag_complet} illustre le flux complet du pipeline RAG, de la réception du message jusqu'à la génération et la sauvegarde de la réponse.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_rag_complet.png}
    \caption{Pipeline RAG détaillé de Rihla-AI : vectorisation, récupération Qdrant (avec ou sans filtre), injection du contexte Redis, assemblage du prompt et génération par Qwen 2.5 7B.}
    \label{fig:rag_complet}
\end{figure}

\subsection{Pipeline OCR — EasyOCR, pytesseract, passporteye}
\label{subsec:modele_ocr}

\paragraph{Vue d'ensemble.}
Lorsqu'un client envoie une photo de son passeport, le système doit en extraire automatiquement les données d'identité sans intervention humaine. Cette tâche mobilise trois composants distincts organisés en deux branches parallèles : une branche de reconnaissance de texte général (EasyOCR ou pytesseract) et une branche de décodage structuré de la zone MRZ (passporteye). Les résultats des deux branches sont ensuite fusionnés dans une structure JSON normalisée.

\paragraph{Pré-traitement de l'image.}
Avant toute reconnaissance, l'image reçue — généralement une photographie de smartphone au format JPEG ou PNG — subit trois opérations préparatoires réalisées par la bibliothèque \textbf{Pillow} : conversion en mode RGB (en cas d'image RGBA ou en niveaux de gris), redimensionnement à une largeur cible de 2 000 pixels (préservant le ratio d'aspect afin de garantir la lisibilité des caractères fins de la MRZ), et seuillage adaptatif des niveaux de gris en amont de pytesseract pour corriger les variations d'éclairage.

\paragraph{Branche principale — EasyOCR (architecture CRNN).}
\textbf{EasyOCR} repose sur une architecture CRNN (\textit{Convolutional Recurrent Neural Network}) à trois étages : (i) un réseau de neurones convolutif (\textit{ResNet}) extrait des cartes de caractéristiques visuelles depuis l'image prétraitée ; (ii) un réseau récurrent bidirectionnel (\textit{BiLSTM}) traite la séquence de caractéristiques pour capturer les dépendances contextuelles entre caractères adjacents ; (iii) un décodeur CTC (\textit{Connectionist Temporal Classification}) convertit la séquence de probabilités en texte brut, gérant naturellement les caractères répétés et les espaces variables entre lettres. Ce pipeline produit le texte libre visible dans la zone de données lisibles à l'œil (nom imprimé, numéros de vols, etc.).

\paragraph{Branche de repli — pytesseract.}
En cas d'échec ou d'indisponibilité d'EasyOCR (timeout, exception runtime), le service bascule automatiquement vers \textbf{pytesseract}, interface Python du moteur Tesseract développé par Google. Bien que moins précis sur les images de qualité variable, pytesseract garantit la continuité du service et ne requiert aucune dépendance deep learning.

\paragraph{Branche MRZ — passporteye (ISO 9303).}
En parallèle et indépendamment des deux branches précédentes, \textbf{passporteye} est systématiquement invoqué sur l'image originale. Ce module spécialisé localise automatiquement la \textbf{Zone de Lecture Machine} (\textit{Machine Readable Zone} — MRZ), bande de deux lignes de 44 caractères chacune imprimée en bas de la page biographique de tout passeport biométrique. Chaque ligne est encodée selon le standard international \textbf{ISO 9303} : les chiffres de contrôle (\textit{check digits}) garantissent l'intégrité de chaque champ, permettant de détecter et corriger des erreurs de reconnaissance. Les champs extraits sont : nom de famille, prénom(s), nationalité (code ISO 3166-1 alpha-3), date de naissance (AAMMJJ), numéro de passeport et date d'expiration.

\paragraph{Fusion et sortie JSON.}
Les résultats des deux branches sont combinés dans un dictionnaire Python, qui fait la priorité aux données MRZ de passporteye — plus structurées et fiables — pour les champs d'identité normalisés, et complète avec le texte libre d'EasyOCR pour les informations non encodées dans la MRZ. La structure JSON retournée contient systématiquement : \texttt{nom}, \texttt{prenom}, \texttt{numero\_passeport}, \texttt{date\_naissance}, \texttt{date\_expiration}, \texttt{nationalite}, ainsi qu'un champ \texttt{methode\_ocr} indiquant le moteur effectivement utilisé (\texttt{"easyocr"} ou \texttt{"pytesseract"}).

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_ocr_detail.png
% Flux de transformation des données :
% [Image passeport (JPEG/PNG)]
%   → Prétraitement Pillow : RGB + resize 2000px + seuillage adaptatif
%   → Branche A (principale) :
%       EasyOCR : ResNet (conv) → BiLSTM (séquence) → CTC (décodage) → texte brut
%   → Branche B (fallback) :
%       pytesseract : heuristiques Tesseract → texte brut
%   → Branche C (MRZ — toujours active) :
%       passporteye : détection MRZ → ligne 1 (44 car.) + ligne 2 (44 car.)
%                  → parsing ISO 9303 + vérification check digits
%                  → champs structurés
%   → Fusion : priorité branche C pour champs normalisés
%   → Sortie JSON : {nom, prenom, numero, naissance, expiration, nationalite}
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:ocr_detail} illustre les transformations successives appliquées à l'image, depuis la réception du fichier brut jusqu'à la production de la structure JSON d'identité.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_ocr_detail.png}
    \caption{Pipeline OCR détaillé de Rihla-AI : prétraitement Pillow, branche EasyOCR (CRNN), branche passporteye (MRZ ISO 9303), fusion et sortie JSON structurée.}
    \label{fig:ocr_detail}
\end{figure}

\subsection{Modèle de recommandation — LightGBM}
\label{subsec:modele_lightgbm}

\paragraph{Vue d'ensemble.}
Lorsqu'un client sollicite une recommandation personnalisée, le système ne se contente pas de proposer les programmes les plus populaires : il calcule pour chaque programme disponible un \textit{score de pertinence} tenant compte du profil spécifique du voyageur. Ce score est produit par un modèle \textbf{LightGBM} entraîné à ordonner les programmes du plus au moins adapté à chaque profil, avant que le LLM ne rédige une justification personnalisée pour les meilleures recommandations.

\paragraph{Principe du gradient boosting et de LightGBM.}
LightGBM appartient à la famille des algorithmes d'\textit{ensemble learning} par \textbf{gradient boosting}. Il construit séquentiellement un ensemble de 100 arbres de décision : le premier arbre apprend à prédire les scores de pertinence à partir des 22 features ; chaque arbre suivant se concentre exclusivement sur les erreurs résiduelles du précédent, les corrigeant de manière itérative. L'originalité de LightGBM réside dans sa stratégie de croissance des arbres \textit{leaf-wise} (par feuille) plutôt que \textit{level-wise} (par niveau), qui converge plus rapidement vers une précision élevée en trouvant les partitions les plus discriminantes à chaque étape.

\paragraph{Mode LambdaRank — optimisation du classement.}
Le modèle est configuré en mode \textbf{LambdaRank}, une variante spécialisée dans l'apprentissage au classement (\textit{learning to rank}). Contrairement aux modes de régression ou de classification, LambdaRank optimise directement la métrique \textbf{NDCG} (\textit{Normalized Discounted Cumulative Gain}), définie formellement comme suit :

\[
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{avec } \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i+1)}
\]

où $r_i$ est le score de pertinence du programme en position $i$ dans le classement produit, et IDCG@k est le DCG du classement idéal (trié par pertinence décroissante). Un NDCG@5 = 1,0 signifie que les 5 programmes retournés sont ordonnés dans l'ordre de pertinence optimal — résultat obtenu lors de nos évaluations. Cette métrique est particulièrement adaptée à notre cas d'usage car elle pénalise plus sévèrement les erreurs de classement en tête de liste, là où l'attention du client est maximale.

\paragraph{Processus d'inférence étape par étape.}
Lorsqu'une requête de recommandation est reçue, les étapes suivantes sont exécutées :

\begin{enumerate}
    \item \textbf{Extraction du profil} : Les informations déclarées par le client (budget, type de profil, nombre de personnes, préférences) sont extraites du message par le LLM et structurées en un dictionnaire Python.
    \item \textbf{Construction des vecteurs de features} : Pour chacun des 11 programmes du catalogue, un vecteur de 22 features est calculé en combinant les attributs du profil voyageur, les attributs du programme, et les 5 indicateurs de compatibilité croisée (tableau \ref{tab:features_lightgbm}).
    \item \textbf{Scoring LightGBM} : Le modèle pré-entraîné (chargé en mémoire depuis le fichier \texttt{.pkl}) produit un score de pertinence pour chacun des 11 vecteurs en un temps inférieur à 5 ms.
    \item \textbf{Classement et sélection} : Les 11 scores sont triés par ordre décroissant ; les 3 programmes les mieux classés (\textit{Top-3}) sont sélectionnés.
    \item \textbf{Génération de la justification} : Les titres et descriptions des 3 programmes retenus, accompagnés du profil du voyageur, sont injectés dans un prompt soumis à Qwen 2.5 7B, qui rédige une réponse explicative personnalisée, dans la langue du client.
\end{enumerate}

\paragraph{Exemple concret.}
Considérons un client envoyant : \textit{« Nous sommes une famille de 4, budget 6 000 TND, on aime la mer et la culture. »} Le profil extrait est : \texttt{type\_profil=famille}, \texttt{nb\_personnes=4}, \texttt{budget=6000}, \texttt{preference=balnéaire+culturel}. Après scoring LightGBM, supposons que le programme \textit{Istanbul + Cappadoce} obtienne le score le plus élevé (forte compatibilité culturelle, prix adulte dans la fourchette budgétaire, hébergement 4 étoiles adapté famille). Le LLM génère alors : \textit{« Pour votre famille de 4 personnes avec un budget de 6 000 TND, nous vous recommandons en priorité notre programme Istanbul + Cappadoce (12 jours), qui allie découverte culturelle et confort en hôtel 4 étoiles... »}

\begin{table}[H]
    \centering
    \caption{Hyperparamètres du modèle LightGBM et performances d'évaluation.}
    \label{tab:lightgbm_params}
    \renewcommand{\arraystretch}{1.4}
    \begin{tabular}{|p{6cm}|p{8cm}|}
    \hline
    \textbf{Paramètre / Métrique} & \textbf{Valeur} \\
    \hline
    Algorithme & LightGBM — mode LambdaRank \\
    \hline
    Nombre d'estimateurs (arbres) & 100 \\
    \hline
    Taux d'apprentissage & 0,05 \\
    \hline
    Profondeur maximale par arbre & 6 \\
    \hline
    Nombre de features en entrée & 22 \\
    \hline
    Métrique d'optimisation & NDCG \\
    \hline
    \textbf{NDCG@5} & \textbf{1,0} (classement parfait sur les 5 premiers) \\
    \hline
    \textbf{NDCG@3} & \textbf{1,0} (classement parfait sur les 3 premiers) \\
    \hline
    \textbf{RMSE} & \textbf{5,5 × 10\textsuperscript{−5}} \\
    \hline
    \textbf{MAE} & \textbf{3,1 × 10\textsuperscript{−5}} \\
    \hline
    \end{tabular}
\end{table}

% ─── SCHÉMA À GÉNÉRER ───────────────────────────────────────────────────────
% schema_lightgbm_pipeline.png
% Flux de traitement :
% [Message client] → LLM (extraction profil) → profil structuré
%   → Pour chacun des 11 programmes :
%       features_voyageur (6) + features_programme (11) + features_compat (5)
%       = vecteur 22-dim
%   → LightGBM (100 arbres, LambdaRank) → 11 scores de pertinence
%   → Tri décroissant → Top-3 programmes
%   → [profil + Top-3 descriptions] → Qwen 2.5 7B → réponse justifiée
%   → [Réponse personnalisée au client]
% ────────────────────────────────────────────────────────────────────────────

La figure \ref{fig:lightgbm_pipeline} illustre la chaîne complète du service de recommandation, depuis l'extraction du profil voyageur jusqu'à la réponse justifiée générée par le LLM.

\begin{figure}[H]
    \centering
    \includegraphics[width=1.0\textwidth]{schema_lightgbm_pipeline.png}
    \caption{Pipeline de recommandation LightGBM de Rihla-AI : extraction du profil, calcul des 22 features, scoring sur 11 programmes, sélection Top-3 et génération de justifications par Qwen 2.5 7B.}
    \label{fig:lightgbm_pipeline}
\end{figure}

\section{Conclusion}
\label{sec:methodo_conclusion}

Ce troisième chapitre a présenté la démarche méthodologique complète mise en œuvre pour concevoir et construire les composants intelligents de Rihla-AI. Le workflow du projet, structuré selon les six phases CRISP-DM, a fourni un cadre itératif permettant de naviguer entre les contraintes techniques découvertes en cours de développement — comme la substitution de PaddleOCR par EasyOCR — sans déstabiliser l'architecture globale. L'analyse des données a mis en évidence la diversité des sources mobilisées : textes de l'agence segmentés et vectorisés dans Qdrant, données structurées persistées dans PostgreSQL, et données synthétiques d'entraînement pour le recommandeur LightGBM. Enfin, la description technique des cinq modèles utilisés — classificateur d'intentions, pipeline RAG, extracteur OCR, moteur LightGBM et mémoire conversationnelle Redis — a précisé les paramètres, les algorithmes et les stratégies de prétraitement qui fondent les performances du système.

Le chapitre suivant présentera les résultats de l'évaluation expérimentale conduite sur chacun de ces composants, en s'appuyant sur des métriques quantitatives standardisées afin de valider objectivement la pertinence des choix méthodologiques effectués.
