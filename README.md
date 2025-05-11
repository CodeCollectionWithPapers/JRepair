<p align="center">
<img src="https://img.shields.io/github/license/mashape/apistatus" alt="" />
</p>

# JRepair
Link to download artifacts for our JIT defect repair model:
https://zenodo.org/records/15382992

## Data Process
Run prepare_source_data.py.<br />
Reprocess the raw data and process the data in _test.bin_ format for subsequent model inference. For different evaluations, the processed datasets are at three levels, including context-free, method-level, and class-level.
## Model Inference
Run inference.py.<br />
The parameter settings correspond to the _config.yaml_ file. The inference results are saved in the _res.pred_ file.
