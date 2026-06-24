from src.helpers.monday_check import check_monday
from src.applications.topic_modeling.use_case.training_umap import TrainingUMAPUseCase


def main():
    """
        Main UMAP training function
    """
    if check_monday():
        print("Today is Monday, training UMAP model")
        training_umap = TrainingUMAPUseCase()
        training_umap.train()
    else:
        print("Today is not Monday, skip training UMAP model")
