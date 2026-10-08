import mlflow


def setup_mlflow() -> None:
    mlflow.set_tracking_uri("http://localhost:5001")
    mlflow.set_experiment("Chatbot_AutoLog_Tracking")
    mlflow.langchain.autolog()
