from app import cognee_client
cognee_client.wait_for_processing()
print(cognee_client.recall(
    "Is user shanks doing any system design preparation? What changed after the "
    "hypothesis calibration, and what did the user correct?"
))
