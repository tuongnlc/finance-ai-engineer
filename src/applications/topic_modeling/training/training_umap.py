# # import polả

# class TrainingUmap:
#     def __init__(self, 
#                  n_components: int = 100,
#                  min_dist: float = 0.1,
#                  metric: str = "cosine",
#                  random_state: int = 42):
#         self.n_components = n_components
#         self.min_dist = min_dist
#         self.metric = metric
#         self.random_state = random_state

#     def train(self, df: pl.DataFrame, embedding_column_name: str) -> None:
#         """
#             Train the UMAP model on the input DataFrame.
#         """
#         pass