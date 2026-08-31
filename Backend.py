try:
   from langgraph.graph import StateGraph, START, END
   from typing import TypedDict, Annotated, Literal
   from langchain_core.messages import BaseMessage
   from langgraph.graph.message import add_messages
   from langgraph.checkpoint.memory import InMemorySaver
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
         
         # # Monkey patch TextIteratorStreamer to increase the hardcoded 60s timeout in langchain
         # from transformers import TextIteratorStreamer
         # original_init = TextIteratorStreamer.__init__
         # def patched_init(self, tokenizer, skip_prompt=False, timeout=None, **kwargs):
         #     original_init(self, tokenizer, skip_prompt=skip_prompt, timeout=600.0, **kwargs)
         # TextIteratorStreamer.__init__ = patched_init
         
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

# -------------------------------------------------------------------
# create chatstate
# -------------------------------------------------------------------

class ChatState(TypedDict):
   messages: Annotated[list[BaseMessage], add_messages]

def create_chatbot(model):
   # create checkpointer for memory
   check_pointer = InMemorySaver()

   # Create chat node function
   def chat_node(state: ChatState):
      messages = state['messages']
      response = model.invoke(messages)
      return {'messages': [response]}

   # create graph instance
   graph = StateGraph(ChatState)
   # add nodes to the graph 
   graph.add_node('chat_node', chat_node)
   # add edges to the graph
   graph.add_edge(START, 'chat_node')
   graph.add_edge('chat_node', END)

   chatbot = graph.compile(checkpointer = check_pointer)
   return chatbot

class ChatBot:
   def __init__(self, model_type: Literal['api','local'], model_name: str, model_task: str, model_temperature: float, model_max_new_tokens: int):
      self.model = create_hf_model(model_type, model_name, model_task, model_temperature, model_max_new_tokens)

      self.bot = create_chatbot(self.model)

# -------------------------------------------------------------------
# Default configuration for local Hugging Face model
# -------------------------------------------------------------------

DEFAULT_MODEL_CONFIG = {
   'model_type': 'local',
   'model_name': 'Qwen/Qwen2.5-3B-Instruct',  # Great performance, fits comfortably in 6GB VRAM
   'model_task': 'text-generation',
   'model_temperature': 0.7,
   'model_max_new_tokens': 512
}

# Create default chatbot instance
try:
   chatbot = ChatBot(**DEFAULT_MODEL_CONFIG).bot
except Exception as e:
   print(f"Error initializing default chatbot: {e}")
   chatbot = None
