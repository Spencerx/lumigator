export type WorkflowResults = {
  artifacts: Artifacts
  metrics: MetricsResult
  parameters: Parameters
}

export type Artifacts = {
  examples: string[]
  ground_truth: string[]
  model: string
  predictions: string[]

  inference_time: number
  evaluation_time: number
}

export type MetricsResult = {
  bertscore?: Bertscore
  meteor?: Meteor
  rouge?: Rouge
  bleu?: {
    bleu: number[]
    bleu_mean: number
  }
  comet?: Comet
}

export type Parameters = {
  dataset: {
    path: string
  }
  evaluation: {
    max_samples: number
  }
  metrics: string[]
  return_input_data: boolean
  return_predictions: boolean
  storage_path: string
  hf_pipeline: HfPipeline
  inference_server?: unknown
  name: string
  job: {
    enable_tqdm: boolean
    max_samples: number
    output_field: string
    storage_path: string
  }
  generation_config: unknown
}

export type HfPipeline = {
  accelerator: string
  max_new_tokens: number
  model_uri: string
  revision: string
  task: string
  torch_dtype: string
  truncation: boolean
  trust_remote_code: boolean
  use_fast: boolean
}

export type Bertscore = {
  f1: number[]
  f1_mean: number
  hashcode: number
  precision: number[]
  precision_mean: number
  recall: number[]
  recall_mean: number
}

export type Meteor = {
  meteor: number[]
  meteor_mean: number
}

export type Comet = {
  scores: number[]
  mean_score: number
}

export type Rouge = {
  rouge1: number[]
  rouge1_mean: number
  rouge2: number[]
  rouge2_mean: number
  rougeL: number[]
  rougeL_mean: number
  rougeLsum: number[]
  rougeLsum_mean: number
}
