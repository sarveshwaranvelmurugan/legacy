from app import cognee_client
cognee_client.wait_for_processing(timeout_s=600)
print(cognee_client.recall(
    "I want to build a new web app that follows the patterns of my projects "
    "app-a and app-b and combines the functionality of both. Describe each "
    "project's stack, architecture, key features and patterns, then recommend "
    "how the combined app should be built based on what I did before.",
    top_k=30,
))
