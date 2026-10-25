# DecisionLab 01 — Le comité d’investissement

## Votre mission

Janvier 2021, convention pédagogique. Vous disposez d’un budget notionnel de 10 millions de dollars pour choisir des expositions à douze marchés immobiliers américains. Vous pouvez conserver du cash. Votre objectif est de défendre une politique, ses coûts et ses risques, pas de gagner à tout prix.

Les données historiques sont des observations Zillow Research. **Data Provided by Zillow Group.** Le ZHVI décrit une valeur immobilière typique estimée par métropole, en USD. Ce ne sont ni les transactions de l’entreprise ni des prix de maisons individuelles. Les données actuelles ont été révisées : ce cours ne reconstitue pas une archive de janvier 2021. Le mois de délai de publication est une convention explicite, non un calendrier historique vérifié.

## Trois actes en deux heures

- 0–10 min : briefing et question métier.
- 10–75 min : notebook, 65 minutes guidées, avec code de départ fonctionnel.
- 75–80 min : remise et gel des quatre décisions.
- 80–90 min : révélation progressive par l’enseignant.
- 90–100 min : scénarios de stress pédagogiques.
- 100–112 min : quatre pitchs de deux minutes et une minute de question.
- 112–120 min : conseil et débrief.

## Notebook en 65 minutes

1. Explorer trois marchés et les unités : 8 min.
2. Définir une cible à six mois et lire les bornes temporelles : 10 min.
3. Comparer baselines et régression : 12 min.
4. Évaluer une règle économique sur validation : 15 min.
5. Exporter le JSON et son empreinte : 8 min.
6. Préparer le pitch et les limites : 12 min.

Les TODO ne sont pas des trous de code bloquants : expliquez, comparez et choisissez. Un manque d’investissement est une décision recevable. Ne changez pas une hypothèse commune pour rendre votre score plus favorable.

## Protocole de prévision

L’entrée est une métropole et un mois. Les variables sont les variations passées à 1, 3, 6 et 12 mois. La cible est 100 × (indice à t+6 / indice à t − 1), en points de pourcentage. Le train et la validation sont chronologiques. Toute cible du train se termine avant la première origine de validation. Les dernières observations dont le futur est inconnu servent à décider, pas à apprendre.

MAE et RMSE sont exprimées en points de pourcentage. Le biais est prévision moins observation. Exemple : prévoir 8 % au lieu de 5 % donne une erreur de 3 points. Le code de prétraitement apprend seulement sur le train.

## Règles du jeu économique

Les positions sont notionnelles et fractionnables. Aucun achat de maison individuelle n’est simulé. Le budget inclut les frais d’achat. Les frais de vente portent sur la valeur de sortie ; le portage est proportionnel à la durée. Les hypothèses communes sont lues dans config.json. Votre marge de sécurité, en points, filtre les opportunités : elle n’est pas une dépense comptable.

Les douze cohortes mensuelles de validation sont des exercices séparés avec budget réinitialisé. Ne cumulez pas leurs profits comme s’il s’agissait d’un portefeuille unique : les horizons se chevauchent.

## Remise avant révélation

Remettez le fichier submissions/Groupe_N.json et son SHA256 à l’enseignant. Ajoutez un pitch.txt indiquant : modèle choisi, erreur de validation, règle, capital engagé, cash, risque majeur et signal d’arrêt. Le professeur conserve une copie et un reçu avant toute révélation. Une empreinte conservée par vous seuls ne prouve pas l’antériorité.

## Pitch au conseil

Vous avez deux minutes pour expliquer vos choix et leurs limites. Après révélation, distinguez l’erreur du modèle, l’effet des coûts, les positions exposées et les scénarios fictifs. Une stratégie rentable dans un résultat historique unique n’est pas nécessairement robuste.

## En cas de blocage

Exécuter le code fourni sans modifier les paramètres ; demander de l’aide au professeur ; utiliser la baseline zéro si l’entraînement bloque. Ne chercher aucune donnée future sur Internet pendant l’expérience. Ne fabriquer aucune observation ni aucun score.
