from sentence_transformers import SentenceTransformer, util

# Load the model from the local directory
model = SentenceTransformer("./local_model")

def semantic_similarity(resume_text, job_text):
    embeddings = model.encode([resume_text, job_text], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return float(similarity.item()) * 100
