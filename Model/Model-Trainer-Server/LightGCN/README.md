# PyTorch Template

## Usage
train
`python -W ignore main.py -c config.json`

### Config file format
Config files are in `.json` format:
```javascript
{
    "model_name": "LightGCN",
    "embedding_name": "LightGCN-Embedding",
    "save_dir" : "./save",
    "remote_server_uri" : "http://34.64.110.227:5000",
    "experiment_name" : "/LightGCN",
    "user" : "SeongBeom",

    "data_dir" : "./data",
    "data_name" : "user",

    "seed" : 22,
    "epochs" : 30,
    "batch_size" : 5000,
    "num_workers" : 8,
    "hidden_units" : 128,
    "n_layers" : 2,
    "reg" : 1e-5,
    "node_dropout_rate" : 0.2,
    "lr" : 0.001
}


```