# ADMIE
MSI Caller for cfDNA

### To Generate Distance Vectors
```python calculate_distances.py --allele-counts /path/to/msisensor/output```

### To Predict on Generated Distance Vectors
```python predict.py --model /path/to/model/ADMIE.joblib --output-file ./distance_vectors.tsv```

### To Run Both Steps In Sequence:

```python admie-analyze.py --allele-counts /path/to/msisensor/output --model /path/to/model/ADMIE.joblib --output-file ./distance_vectors.tsv```
