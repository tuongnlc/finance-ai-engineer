
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

print("Thư mục MLflow đang lưu hiện tại là:", mlflow.get_tracking_uri())

with mlflow.start_run(run_name="hello_word_mlflow"):
    # Ghi vao tracking backend (vd. PostgreSQL) thay vi artifact store.
    mlflow.log_param("message", "Hello World Updated!")
    mlflow.set_tag("message_type", "plain_text")

# import mlflow
# print("Thư mục MLflow đang lưu là:", mlflow.get_tracking_uri())
