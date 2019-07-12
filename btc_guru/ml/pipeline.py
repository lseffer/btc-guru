from sklearn.pipeline import Pipeline
from ta.pipeline_wrapper import TAFeaturesTransform
from tsfresh.transformers.feature_augmenter import FeatureAugmenter

feature_extraction = Pipeline([
    ('ta', TAFeaturesTransform('open', 'high', 'low', 'close', 'volume')),
    ('tsfresh', FeatureAugmenter()),
])
