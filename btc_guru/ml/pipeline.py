from sklearn.pipeline import Pipeline
from ta.pipeline_wrapper import TAFeaturesTransform
from tsfresh.transformers.feature_augmenter import FeatureAugmenter


def feature_extraction_pipeline():
    return Pipeline([
        ('ta', TAFeaturesTransform('open', 'high', 'low', 'close', 'volume')),
        ('tsfresh', FeatureAugmenter()),
    ])

def model_fit_pipeline():
    return Pipeline([

    ])

