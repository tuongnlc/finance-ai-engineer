import os
import mlflow



class PromptRegister:
    def __init__(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_registry_uri(tracking_uri)
    
    def register_prompt(self, prompt_name, prompt_template):
        mlflow.register_prompt(prompt_name, prompt_template)
