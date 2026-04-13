"""
Hyperparameter Tuning with Optuna
"""

import optuna
import numpy as np
from typing import Dict, Any, Callable
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner


class HyperparameterTuner:
    """Optuna-based hyperparameter optimization"""
    
    def __init__(self, model_class: Callable, n_trials: int = 50,
                 direction: str = 'minimize', random_state: int = 42):
        self.model_class = model_class
        self.n_trials = n_trials
        self.direction = direction
        self.random_state = random_state
        self.study = None
        self.best_params = None
        self.best_value = None
        
    def objective(self, trial, X_train, y_train, X_val, y_val) -> float:
        """Objective function for Optuna"""
        raise NotImplementedError("Subclass must implement objective")
    
    def tune(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Run hyperparameter tuning"""
        
        self.study = optuna.create_study(
            direction=self.direction,
            sampler=TPESampler(seed=self.random_state),
            pruner=MedianPruner()
        )
        
        def objective_wrapper(trial):
            return self.objective(trial, X_train, y_train, X_val, y_val)
        
        self.study.optimize(objective_wrapper, n_trials=self.n_trials)
        
        self.best_params = self.study.best_params
        self.best_value = self.study.best_value
        
        return self.best_params
    
    def get_best_model(self):
        """Get best model with optimized parameters"""
        if self.best_params is None:
            raise ValueError("Run tune() first")
        return self.model_class(**self.best_params)
    
    def plot_optimization_history(self):
        """Plot optimization history"""
        import matplotlib.pyplot as plt
        
        optuna.visualization.plot_optimization_history(self.study)
        plt.show()


class XGBoostTuner(HyperparameterTuner):
    """XGBoost Hyperparameter Tuner"""
    
    def objective(self, trial, X_train, y_train, X_val, y_val) -> float:
        from xgboost import XGBRegressor
        
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 2),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
            'random_state': 42,
            'n_jobs': -1
        }
        
        model = XGBRegressor(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        y_pred = model.predict(X_val)
        
        return np.sqrt(mean_squared_error(y_val, y_pred))


class LightGBMTuner(HyperparameterTuner):
    """LightGBM Hyperparameter Tuner"""
    
    def objective(self, trial, X_train, y_train, X_val, y_val) -> float:
        from lightgbm import LGBMRegressor
        
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 2),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
            'random_state': 42,
            'verbose': -1
        }
        
        model = LGBMRegressor(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], eval_metric='rmse')
        y_pred = model.predict(X_val)
        
        return np.sqrt(mean_squared_error(y_val, y_pred))


class CatBoostTuner(HyperparameterTuner):
    """CatBoost Hyperparameter Tuner"""
    
    def objective(self, trial, X_train, y_train, X_val, y_val) -> float:
        from catboost import CatBoostRegressor
        
        params = {
            'iterations': trial.suggest_int('iterations', 100, 500),
            'depth': trial.suggest_int('depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
            'random_seed': 42,
            'verbose': False
        }
        
        model = CatBoostRegressor(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        y_pred = model.predict(X_val)
        
        return np.sqrt(mean_squared_error(y_val, y_pred))