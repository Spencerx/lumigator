import pytest
from model_clients.mixins.huggingface_model_mixin import DEFAULT_MAX_POSITION_EMBEDDINGS, HuggingFaceModelMixin
from transformers import PretrainedConfig, PreTrainedModel


class MockPreTrainedModel(PreTrainedModel):
    def __init__(self, config: PretrainedConfig, *inputs, **kwargs):
        self.config = config


class MockPretrainedConfig(PretrainedConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_get_max_position_embeddings_valid():
    config = MockPretrainedConfig(max_position_embeddings=512)
    model = MockPreTrainedModel(config)
    mixin = HuggingFaceModelMixin()
    assert mixin.get_max_position_embeddings(model) == 512


def test_get_max_position_embeddings_missing():
    config = MockPretrainedConfig()
    model = MockPreTrainedModel(config)
    mixin = HuggingFaceModelMixin()
    max_pos_emb = mixin.get_max_position_embeddings(model)
    assert max_pos_emb == DEFAULT_MAX_POSITION_EMBEDDINGS


def test_get_max_position_embeddings_none_model():
    mixin = HuggingFaceModelMixin()
    with pytest.raises(TypeError, match="The pre-trained model cannot be None"):
        mixin.get_max_position_embeddings(None)


def test_get_max_position_embeddings_none_config():
    model = MockPreTrainedModel(config=None)
    mixin = HuggingFaceModelMixin()
    with pytest.raises(TypeError, match="The pre-trained model's config cannot be None"):
        mixin.get_max_position_embeddings(model)
