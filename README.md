<p align="center">
<img src="https://img.shields.io/github/license/mashape/apistatus" alt="" />
</p>

# JRepair: Just-In-Time Defect Repair (Under Review)
## Environment dependencies
* python 3.9
* torch 1.12.0
* numpy 1.23.5
* tqdm 4.67.0
* fairseq 0.6.0
* yaml 0.1.6
* libclang 14.0.6
## Data Process
Run prepare_source_data.py.<br />
Reprocess the raw data and process the data in _test.bin_ format for subsequent model inference. For different evaluations, the processed datasets are at three levels, including context-free, method-level, and class-level.
## Model Inference
Run inference.py.<br />
The parameter settings correspond to the _config.yaml_ file. The inference results are saved in the _res.pred_ file.
