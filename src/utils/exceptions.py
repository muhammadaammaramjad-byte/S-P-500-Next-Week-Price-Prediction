class SP500PredictorError(Exception):
    pass

class DataCollectionError(SP500PredictorError):
    pass

class FeatureEngineeringError(SP500PredictorError):
    pass

class ModelTrainingError(SP500PredictorError):
    pass

class PredictionError(SP500PredictorError):
    pass

class ValidationError(SP500PredictorError):
    pass

class ConfigurationError(SP500PredictorError):
    pass
