# Benchmark Summary

The test was done with three support thresholds (0.05, 0.02, 0.01, 0.005) and three confidence thresholds (0.5, 0.6, 0.7) to evaluate rule generation, execution time, and memory consumption.

- **Limit memory allocation:** At 0.5% (0.005) minimum support, the Apriori algorithm failed attempting to allocate 72.6 GiB of memory.

#### Benchmark Results

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

#### Selected configuration for the Next Phase

- **Minimum support:** 0.02 (2%)
- **Minimum confidence:** 0.60 (60%)
- **Memory optimization:** `low_memory=True`
- **Lift filter:** Greater than 1, to retain positive associations.

This configuration generated **658 itemsets** and **1099 rules** in 69.91 seconds, using approximately 13.93 GB of peak process memory.

#### Conclusion

The results highlight the trade-off between discovering more association rules and increasing computational requirements. A low support threshold generated too many frequent itemsets, leading to high memory consumption. To address this issue, I changed the `low_memory` parameter from `False` to `True`. I also removed **'Sac réutilisable'**, which appeared in 90% of baskets, and performed association rule mining separately for each season. These adjustments helped reduce memory usage while allowing me to maintain a low support threshold.
