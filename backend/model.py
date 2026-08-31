try:
   from typing import Literal
   from dotenv import load_dotenv
   import os
except Exception as e:
   raise ImportError(f"Failed to import necessary modules: {e}")

# import secret keys if any
load_dotenv()
# fix local models catch directory
os.environ['HF_HOME'] = 'S:/ollama_models'

# -------------------------------------------------------------------
# Hugging Face Model Creation
# -------------------------------------------------------------------

def create_hf_model(type: Literal['api','local'], model_name: str, model_task: str, model_temperature: float, model_max_new_tokens: int):
   try:
      from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFacePipeline

      # hf api models
      if type == 'api':
         llm = HuggingFaceEndpoint(
            repo_id=model_name,
            task=model_task,
            pipeline_kwargs=dict(
               temperature=model_temperature,
               max_new_tokens=model_max_new_tokens,
            )
         )
      # hf local models
      elif type == 'local':
         
         model_kwargs = {"device_map": "auto", "dtype": "auto"}
         # Hardware Optimization: Attempt 4-bit quantization for low-spec PCs
         try:
            from transformers import BitsAndBytesConfig
            import torch
            # 4-bit cuts memory usage by 75%, making 3B models take only ~2GB VRAM
            quant_config = BitsAndBytesConfig(
               load_in_4bit=True,
               bnb_4bit_compute_dtype=torch.float16
            )
            model_kwargs["quantization_config"] = quant_config
         except ImportError:
            pass # bitsandbytes not installed, fallback to standard precision

         from transformers import GenerationConfig

         generation_config = GenerationConfig.from_pretrained(model_name)

         # Override only the parameters controlled by app
         generation_config.max_new_tokens = model_max_new_tokens
         generation_config.do_sample = True
         generation_config.temperature = model_temperature

         llm = HuggingFacePipeline.from_model_id(
            model_id=model_name,
            task=model_task,
            model_kwargs=model_kwargs,
            pipeline_kwargs={
               "generation_config": generation_config,
               "return_full_text": False,
            },
         )
      else:
         raise ValueError("model type must be an api or local.")

      # create model and return it
      model = ChatHuggingFace(llm = llm)
      return model

   except Exception as e:
      print(f"Error occured while calling creating model instance: {e}")
