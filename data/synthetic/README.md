# Synthetic data

Files in this directory are generated exclusively by this repository.

`leads_sample.csv` contains 20 records generated with seed `42`. The sample
exists only to make the public schema easy to inspect. It is not derived from,
masked from, or statistically fitted to the historical corporate dataset.

Generate a larger working dataset with:

```bash
python scripts/run_data_pipeline.py --rows 500 --seed 42
```
