class ClauseMatcher:
    def __init__(self, index_path=None, embeddings_path=None):
        pass
 
    def match(self, clause_text):
        # Always return an empty match to effectively remove the 'Best Match' column
        return {"match": "", "score": 0.0} 