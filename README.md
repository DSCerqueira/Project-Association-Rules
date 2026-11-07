# 🛒 Boréal Marché — Product Recommendation Engine

[🛒 Launch Boréal Marché](https://boreal-marche.onrender.com)

## 1. Project Overview

**Boréal Marché** is a Quebec online grocery retailer. Today its website shows the same list of “popular products” to every customer. Management wants to replace that list with real recommendations based on what is already in the shopping basket, and it wants to understand why each suggestion is made.

The project analyzes approximately **1 million shopping baskets, 8.38 million transaction rows, and 98 products**, considering seasonal purchasing differences.

### Objectives

Build a complete web application recommendation system that can be demosntrated in front of a client. The system should be able to answer the question: “Given what this customer has already put in their basket, what should
we suggest next - and why?”

**Project steps:**

- Prepare transaction data and identify frequent product combinations using Apriori.
- Evaluate association rules using **support, confidence, and lift**.
- Compare purchasing patterns across four seasons.
- Develop an interactive **Streamlit application** that provides up to five explainable product recommendations.

## 2. Repository Structure and Installation

### Repository Structure

```text
Boréal-Marche/
├── app/
│   └── streamlit_app.py
├── data/
│   ├── popular_items_by_session.csv
│   ├── products.csv
│   └── products.zip
├── models/
│   ├── benchmark_results.json
│   ├── metadata.json
│   ├── rules.csv
│   └── rules.json
├── notebook/
│   ├── 01_mining.ipynb
├── reports/
│   └── benchmark.md
├── README.md
└── requirements.txt
```

- **`app/`:** Streamlit recommendation application.
- **`data/`:** Product Transactions, Product catalogue, and seasonal popularity.
- **`models/`:** Generated association rules, metadata, and benchmark results.
- **`notebook/`:** Apriori experiments, analysis, and generated outputs.
- **`reports/`:** benchmark.md with .

## 3. Data Preparation

The dataset contains **1,000,000 shopping baskets, 8,379,837 transaction rows, and 98 products**, with an average of 8.38 products per basket.

### Data Cleaning

- Checked missing values, duplicate records, and product-name consistency. No issues found
- Investigated similar products. No duplicate products or products with similar names were found in the dataset.
- Identified `Sac réutilisable` (reusable bag) in approximately **90% of baskets**.

### Transaction Transformation

The transaction data was converted into a **Boolean basket-product matrix**:

- **Rows:** 1,000,000 shopping baskets.
- **Columns:** 98 products.
- **Values:** `True` if a product was purchased; otherwise `False`.

The resulting matrix occupied approximately **93.49 MB of memory**, with a measured creation time of **10.47 seconds**.

## 4. Apriori

The Apriori algorithm was tested with different **minimum support (5%, 2%, and 1%)** and **confidence (70%, 60%, and 50%)** thresholds to evaluate their impact on the number of association rules, execution time, and memory consumption.

### Benchmark Results

| min_support | min_confidence | n_itemsets | n_rules | execution_time | peak_memory_mb |
| ----------- | -------------- | ---------- | ------- | -------------- | -------------- |
| 0.05        | 0.7            | 191        | 153     | 38.48          | 8100.66        |
| 0.05        | 0.6            | 191        | 195     | 36.34          | 8101.91        |
| 0.05        | 0.5            | 191        | 242     | 35.67          | 8101.94        |
| 0.02        | 0.7            | 658        | 730     | 71.27          | 12928.56       |
| 0.02        | 0.6            | 658        | 1099    | 69.91          | 12929.18       |
| 0.02        | 0.5            | 658        | 1552    | 56.02          | 12929.7        |
| 0.01        | 0.7            | 2267       | 2177    | 196.8          | 19434.15       |
| 0.01        | 0.6            | 2267       | 3111    | 164.72         | 19136.88       |
| 0.01        | 0.5            | 2267       | 4325    | 172.86         | 20758.5        |
| 0.005       | Failed         | Failed     | Failed  | Failed         | Failed         |

At `min_support=0.005`, Apriori failed while attempting to allocate **72.6 GiB** of memory.
Lower support thresholds generated more rules but significantly increased computational costs.

### Memory Optimization

To address this limitation, I enabled `low_memory=True`, excluded `Sac réutilisable` (present in approximately 90% of baskets), and divided the transactions into four seasonal datasets. The `low_memory=True` paramter increase the time to generate itemsets but reduce the peak memory comsuption.

### Final Configuration

The final association rules were generated separately for each season using:

- **Minimum support:** 0.5%
- **Minimum confidence:** 50%
- **Minimum lift:** Greater than 1
- **Memory optimization:** `low_memory=True`
- **Consequents:** One product per rule

**Rules by Season**

| Season           | Number of Rules |
| ---------------- | --------------: |
| Winter (Dec–Feb) |            2823 |
| Spring (Mar–May) |            4489 |
| Summer (Jun–Aug) |           10523 |
| Autumn (Sep–Nov) |            3739 |
| **Total**        |      **16,808** |

This configuration generated **16,808 association rules** across the four seasons, balancing recommendation coverage and computational feasibility.

## 5. Association Rule Evaluation

Association rules were evaluated using three metrics:

- **Support:** Percentage of baskets containing both antecedents and consequents.
- **Confidence:** Probability of purchasing the consequent given the antecedents.
- **Lift:** Association strength compared to independent purchasing.

### Rule Evaluation

The final model uses **confidence ≥ 50% and lift > 1**, ranking recommendations by lift.

Example of a **winter** rule:

**Ketchup + Steak de boeuf → Charbon de bois**

| Metric     |  Value |
| ---------- | -----: |
| Support    |  1.50% |
| Confidence | 98.22% |
| Lift       |  19.88 |

This indicates a strong purchasing association, approximately 19.88 times the rate expected under independence.

### Recommendation Coverage

The rules cover **38 of 98 products (38.78%)** as potential recommendations.

Lower support thresholds increase rule discovery but require more computational resources.

**Note:** Association does not imply causation.

## 6. Seasonal Analysis

The dataset was divided into **Winter, Spring, Summer, and Fall** to identify seasonal purchasing patterns and generate more relevant recommendations.

### Rules Generated by Season

| Season    | Association Rules |
| --------- | ----------------: |
| Winter    |             2,359 |
| Spring    |             3,574 |
| Summer    |             7,878 |
| Fall      |             2,997 |
| **Total** |        **16,808** |

| Season      | Number of Association Rules | Coverage (%) |
| ----------- | --------------------------: | -----------: |
| Winter      |                       2,359 |       37.76% |
| Spring      |                       3,574 |       36.73% |
| Summer      |                       7,878 |       32.65% |
| Fall        |                       2,997 |       36.73% |
| **Average** |                   **4,202** |   **35.97%** |

Summer generated the highest number of rules, indicating more product combinations meeting the selected thresholds.

### Rules That Disappear Across Seasons

Some associations are identified in one season but not another.

For example, **Bananes + Farine tout usage + Bacon → Sirop d'érable** appears in Summer but not in Winter's mined rules.

This does not mean the combination never occurs in Winter; it may simply fail to meet the minimum support or confidence thresholds.

### Changes in Rule Rankings

Rules can also change their **lift values and rankings** across seasons because purchasing frequencies vary.

A highly ranked rule in Summer may have a lower ranking in Winter, even when the same association exists in both seasons.

## 7. Recommendation Engine

The recommendation engine uses **seasonal association rules** to suggest up to **five products** based on the customer's shopping basket.

### Recommendation Process

1. **Season selection:** Load association rules for the selected season.
2. **Basket matching:** Search for rules matching all products in the basket. If none qualify, progressively check smaller subsets. **Sac réutilisable** is excluded from the basket during the matching process.
3. **Rule filtering:** Exclude products already in the basket and remove duplicate recommendations.
4. **Ranking:** Sort eligible recommendations by **lift**, selecting up to five products.
5. **Fallback:** If no matching rule is found, recommend a popular product from the selected season.

### Explainability

Each rule-based recommendation includes its **support, confidence, and lift**, allowing users to understand the purchasing association behind the suggestion.

### Limitations

The engine prioritizes the largest matching basket subset and stops when eligible recommendations are found. Therefore, it may return fewer than five products even when smaller subsets have additional matches. Therefore, as the number of items in the basket increases, the number of recommended products may decrease, potentially reducing recommendation coverage.

## 8. Streamlit Application & Edge Cases

The project includes an interactive **Streamlit application** that allows users to build shopping baskets and receive seasonal product recommendations.

### Main Features

- **Product catalogue:** Browse 98 products, filter by category, and search in French or English.
- **Shopping basket:** Add or remove products, manage quantities, and view total prices.
- **Season selection:** Automatically detect the current season or manually select another.
- **Recommendations:** Display up to five products ranked by lift.
- **Explainability:** Show support, confidence, lift, and matching association rules.
- **Fallback:** Suggest a popular seasonal product when no eligible rule is found.

### Edge Cases & Validation

| Edge Case                          | Application Behavior                                         |
| ---------------------------------- | ------------------------------------------------------------ |
| Empty basket or no matching rules  | Recommend a popular seasonal product.                        |
| Reusable bag (`Sac réutilisable`)  | Excluded from rule matching.                                 |
| Products already in basket         | Excluded from recommendations.                               |
| Duplicate recommendations          | Keep the highest-lift rule per product.                      |
| No full-basket match               | Progressively search smaller subsets.                        |
| Fewer than five recommendations    | Return available products without searching smaller subsets. |
| Multiple quantities of one product | Count as one item for rule matching.                         |
| Season changes                     | Load the corresponding seasonal rules.                       |

### Running the Application

From the repository root:

```bash
streamlit run app/streamlit_app.py
```

The application loads precomputed association rules from JSON files without rerunning Apriori.

## 9. Responsible Use & Limitations

### Responsible Use

- **Association is not causation:** Rules identify purchasing patterns but do not explain why products are purchased together.
- **Metric interpretation:** High lift does not necessarily indicate a reliable recommendation, especially when support is low.
- **Transparency:** Recommendations display support, confidence, and lift.

### Famous Retail Example: Beer and Diapers

The dataset reproduces the famous **beer and diapers** association from market basket analysis.

For example, a Winter rule identifies:

**Bière + Lingettes pour bébé → Couches**

| Metric     |  Value |
| ---------- | -----: |
| Support    |  2.15% |
| Confidence | 91.95% |
| Lift       |  11.69 |

### Current Limitations

- **Product coverage:** Only 38 of 98 products (38.78%) appear as rule consequents.
- **Basket matching:** Larger subsets may return fewer than five recommendations.
- **Cold-start problem:** Empty or unmatched baskets rely on seasonal popularity.
- **Computational cost:** Lower support thresholds increase memory requirements.

### Reinforcement bias

The recommendation system has an average coverage of around 36% across seasons, which means that many products are never suggested through association rules. This could lead customers to keep buying the same products instead of discovering new ones. Another issue is that when the basket is empty or no matching rule is found, the system recommends popular products. As a result, we may end up encouraging customers to buy products that are already popular, rather than giving less popular products a chance.
