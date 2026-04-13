import ray
from ray import tune
from ray.data import from_pandas
import dask.dataframe as dd

@ray.remote(num_gpus=0.5)
class DistributedTrainer:
    """Distributed hyperparameter optimization"""
    
    def __init__(self, model_class, param_space):
        self.model_class = model_class
        self.param_space = param_space
        
    def train(self, train_data, valid_data):
        analysis = tune.run(
            self.model_class,
            config=self.param_space,
            resources_per_trial={"cpu": 2, "gpu": 0.5},
            num_samples=100,
            metric="validation_accuracy",
            mode="max"
        )
        return analysis.best_config