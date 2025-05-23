import datetime as dt
from abc import ABC
from enum import Enum
from typing import Any, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator
from pydantic.json_schema import SkipJsonSchema

from lumigator_schemas.redactable_base_model import RedactableBaseModel
from lumigator_schemas.tasks import (
    SummarizationTaskDefinition,
    TaskDefinition,
    get_metrics_for_task,
)
from lumigator_schemas.transforms.job_submission_response_transform import transform_job_submission_response


class LowercaseEnum(str, Enum):
    """Can be used to ensure that values for enums are returned in lowercase."""

    def __new__(cls, value):
        obj = super().__new__(cls, value.lower())
        obj._value_ = value.lower()
        return obj


class JobType(LowercaseEnum):
    INFERENCE = "inference"
    EVALUATION = "evaluator"
    ANNOTATION = "annotate"


class JobStatus(LowercaseEnum):
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    STOPPED = "stopped"


class JobConfig(BaseModel):
    job_id: UUID
    job_type: JobType
    command: str
    args: dict[str, Any] | None = None


class JobEvent(BaseModel):
    job_id: UUID
    job_type: JobType
    status: JobStatus
    detail: str | None = None


class JobLogsResponse(BaseModel):
    logs: str | None = None


# Check Ray items actually used and copy
# those from the schema
# ref to https://docs.ray.io/en/latest/cluster/running-applications/job-submission/doc/ray.job_submission.JobDetails.html
class JobSubmissionResponse(RedactableBaseModel):
    type: str | None = None
    submission_id: str | None = None
    driver_info: str | None = None
    status: str | None = None
    config: dict | None = Field(default_factory=dict)
    message: str | None = None
    error_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    metadata: dict = Field(default_factory=dict)
    runtime_env: dict = Field(default_factory=dict)
    driver_agent_http_address: str | None = None
    driver_node_id: str | None = None
    driver_exit_code: int | None = None

    @model_validator(mode="before")
    @classmethod
    def transform(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Pre-processes and validates the 'entrypoint' configuration before model validation.

        This method uses Pydantic's 'model_validator' hook to parse the 'entrypoint'
        configuration, and where appropriate, redact sensitive information. It then
        assigns the processed configuration to the `config` field of the model
        (`JobSubmissionResponse`) before model validation occurs.

        :param values: The dictionary of field values to be processed.
            It contains the model data, including the 'entrypoint' configuration.
        :return: The updated values dictionary, with the processed and
            potentially redacted 'entrypoint' configuration assigned to the `config` field.
        """
        transformed_values = transform_job_submission_response(values)
        return transformed_values


class BaseJobConfig(BaseModel, ABC):
    secret_key_name: str | None = Field(
        None,
        title="Secret Key Name",
        description="An optional secret key name. "
        "When creating a job, the secret key name identifies an existing secret stored in Lumigator "
        "that should be used to access the provider.",
    )


class DeepEvalLocalModelConfig(BaseModel):
    model_name: str
    model_base_url: str


class JobEvalConfig(BaseJobConfig):
    job_type: Literal[JobType.EVALUATION] = JobType.EVALUATION
    # NOTE: If changing the default task definition (currently summarization),
    # please ensure that it has a corresponding default metrics mapping in the get_metrics_for_task function.
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())
    metrics: set[str] = Field(default_factory=lambda info: get_metrics_for_task(info["task_definition"].task))
    llm_as_judge: DeepEvalLocalModelConfig | None = None


class GenerationConfig(BaseModel):
    """Custom and limited configuration for generation.
    Sort of a subset of HF GenerationConfig
    https://huggingface.co/docs/transformers/en/main_classes/text_generation#transformers.GenerationConfig
    """

    model_config = ConfigDict(extra="forbid")
    max_new_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 0.5
    top_p: float = 0.5


class JobInferenceConfig(BaseJobConfig):
    job_type: Literal[JobType.INFERENCE] = JobType.INFERENCE
    model: str
    provider: str
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())
    accelerator: str | None = "auto"
    revision: str | None = "main"
    use_fast: bool = True  # Whether or not to use a Fast tokenizer if possible
    trust_remote_code: bool = False
    torch_dtype: str = "auto"
    base_url: str | None = None
    output_field: str | None = "predictions"
    generation_config: GenerationConfig = Field(default_factory=GenerationConfig)
    store_to_dataset: bool = False
    system_prompt: str | None = Field(
        title="System Prompt",
        description="System prompt to use for the model inference."
        "If not provided, a task-specific default prompt will be used.",
        default=None,
        examples=[
            "You are an advanced AI trained to summarize documents accurately and concisely. "
            "Your goal is to extract key information while maintaining clarity and coherence."
        ],
    )


class JobAnnotateConfig(JobInferenceConfig):
    """Job configuration for the annotation job type

    An annotation job is a special type of inference job that is used to
    annotate a dataset with predictions from a model. The predictions are
    stored in the dataset as a new field called `ground_truth`.

    JobAnnotateConfig inherits from JobInferenceConfig but fixes the following
    fields, using the `SkipJsonSchema` type to prevent them from being included
    in the JSON schema:
    - job_type: Literal[JobType.ANNOTATION]
    - output_field: "ground_truth"

    It also sets sensible defaults for the following fields:
    - store_to_dataset: True
    - model: "facebook/bart-large-cnn"
    - provider: "hf"

    Users can change the model and provider fields but cannot change the
    job_type or output_field fields.

    Note that, currently, ground truth generation is limited to summarization
    tasks from the UI. Users can run any ground truth generation task from the
    API.
    """

    job_type: SkipJsonSchema[Literal[JobType.ANNOTATION]] = JobType.ANNOTATION
    model: str = Field(default="facebook/bart-large-cnn")
    provider: str = Field(default="hf")
    output_field: SkipJsonSchema[str] | None = "ground_truth"
    store_to_dataset: bool = True


JobSpecificConfig = JobEvalConfig | JobInferenceConfig | JobAnnotateConfig
"""
Job configuration dealing exclusively with the Ray jobs
"""
# JobSpecificConfigVar = TypeVar('JobSpecificConfig', bound=JobSpecificConfig)
JobSpecificConfigVar = TypeVar("JobSpecificConfig", JobEvalConfig, JobInferenceConfig, JobAnnotateConfig)


class JobCreate(BaseModel):
    """Job configuration dealing exclusively with backend job handling"""

    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    batch_size: PositiveInt = 1
    job_config: JobSpecificConfig = Field(discriminator="job_type")


class JobAnnotateCreate(JobCreate):
    job_config: JobAnnotateConfig


class JobEvalCreate(JobCreate):
    job_config: JobEvalConfig


class JobInferenceCreate(JobCreate):
    job_config: JobInferenceConfig


class JobResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    job_type: JobType
    created_at: dt.datetime
    experiment_id: UUID | None = None
    updated_at: dt.datetime | None = None


class JobResultResponse(BaseModel, from_attributes=True):
    id: UUID
    job_id: UUID


class JobResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str


class JobResults(BaseModel):
    id: UUID
    metrics: list[dict[str, Any]] | None = None
    parameters: list[dict[str, Any]] | None = None
    metric_url: str
    artifact_url: str


class JobResultObject(BaseModel):
    """This is a very loose definition of what data
    should be stored in the output settings.S3_JOB_RESULTS_FILENAME.
    As long as a job result file only has the fields defined here,
    it should be accepted by the backend.
    """

    model_config = ConfigDict(extra="ignore")
    metrics: dict = {}
    parameters: dict = {}
    artifacts: dict = {}

    def merge(self, other: "JobResultObject"):
        """Merge the properties from another JobResultObject into this one."""
        for field in self.model_fields:
            # Get the current and new field values
            current_value = getattr(self, field)
            new_value = getattr(other, field)

            # Update if the field is a dict and the new value is non-empty
            if isinstance(current_value, dict) and new_value:
                current_value.update(new_value)


class Job(JobResponse, JobSubmissionResponse):
    """Job represents the composition of JobResponse and JobSubmissionResponse.

    JobSubmissionResponse was formerly returned from some /health/jobs related
    endpoints, while JobResponse was used by /jobs related endpoints.

    The only conflicting field in the two schemas is 'status' which is consistent
    in what it intends to represent, but uses different types (JobStatus/str).

    The Job type has both id and submission_id which will contain the same data.

    NOTE: Job is intended to reduce breaking changes experienced by the UI and other
    consumers. Tt was not conceived as a type that will be around for long, as
    the API needs to be refactored to better support experiments.
    """

    pass
