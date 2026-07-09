from ai_engineer.helpers.monday_check import check_monday
from ai_engineer.applications.topic_modeling.use_case.umap_training import TrainingUMAPUseCase


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
