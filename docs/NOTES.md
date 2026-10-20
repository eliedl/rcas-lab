# rcas-lab — Notes

## 2026-10-20 — tas · Gulf · 1991–2020 · DJFM (from `exploration/01_casr_tas.ipynb`)

L'affichage des valeurs de R² dans les panneaux mensuels supérieurs indique de plus grandes valeurs pour Janvier et Février, particulièrement sur l'étendue marine du Golfe et de l'Estuaire. Les panneaux de p value montrent des zones significatives de tendances au réchauffement pour le Golfe pour Janvier et Février, avec une petite zone de refroidissement dans l'estuaire supérieur Laurentien en Décembre. Aucune cellule de la grille ne possède un p value sous 0.05 pour le mois de Mars.

## 2026-10-20 — CFIA · usage pour les indices climatologiques de précipitation (à valider)

**Champ.** `CFIA` — *Analysis: Confidence Index of CaPA 24h Analysis at surface*. Indice journalier par cellule, entre 0 et 1, issu de l'interpolation optimale de CaPA : ≈ 0 → l'analyse retombe sur l'ébauche GEM (pas d'observation à proximité) ; ≈ 1 → l'analyse est contrainte par les observations (pluviomètres, puis radar). Définition confirmée : `CFIA = 1 − σ²_a / σ²_b` (σ²_a : variance d'erreur de l'analyse ; σ²_b : variance d'erreur de l'ébauche), Khedhaouiria et al. 2022, éq. 11 → [READING_LOG.md](READING_LOG.md) e004. 

**Portée.** Ne concerne que la précipitation analysée ; sans objet pour `tas` (`01_casr_tas`).

**Usages possibles pour les indices de précipitation (moyennes et tendances) :**

1. **Masquage.** Restreindre les indices aux cellules dont la CFIA moyenne dépasse un seuil, ou les présenter à part.
2. **Hachurage.** Superposer les zones de faible CFIA aux cartes d'indices et de tendances, comme le hachurage de significativité : le résultat y reflète surtout la climatologie du modèle.
3. **Homogénéité des tendances (usage clé).** La CFIA varie dans le temps avec l'évolution du réseau de stations et l'ajout de l'assimilation radar. Un saut dans la densité d'observations peut créer une rupture que Sen / régression linéaire interprète comme une tendance. Contrôle : série temporelle de la CFIA moyenne sur le domaine, recherche de ruptures, puis recalcul des tendances sur une sous-période (ou des cellules) à CFIA stable.
4. **Pondération.** Moyennes spatiales pondérées par la CFIA ; moins courant, justification physique plus faible.
5. **Validation externe.** Là où la CFIA est faible, une tendance CaSR est une tendance GEM ; la corroborer par une source indépendante (stations, ERA5).

**Hypothèse pour le Golfe (non mesurée).** Peu ou pas de pluviomètres en mer et couverture radar limitée → CFIA probablement proche de 0 sur l'essentiel du domaine marin.

**Sondes à faire avant tout choix de méthode :**
- carte de la CFIA moyenne DJFM sur la fenêtre climatologique ;
- série temporelle de la CFIA moyenne (terre vs mer) pour détecter les ruptures.

**Décision en attente (PENDING).** Traitement de la CFIA (seuil, hachurage, sous-période de tendance) à trancher après ces sondes.
