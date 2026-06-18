import os

doc_file = "sample.doc"

print("File Exists:", os.path.exists(doc_file))

if os.path.exists(doc_file):
    print("File Size:", os.path.getsize(doc_file))


    import os

print("Current Folder:", os.getcwd())
print("\nFiles in Folder:")
print(os.listdir())