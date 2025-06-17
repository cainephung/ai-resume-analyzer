from sentence_transformers import SentenceTransformer

# Download and save the model locally
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model.save("./local_model")
print("Model downloaded to ./local_model")
