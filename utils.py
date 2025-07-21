import os

def load_documents(folder_path="documents"):
    docs = []
    filenames = []

    if not os.path.exists(folder_path):
        print("❌ 'documents/' folder not found!")
        return docs, filenames

    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as file:
                docs.append(file.read())
                filenames.append(filename)
    return docs, filenames
