from ace import ACEBulkLoader

# Example usage of ACEBulkLoader
loader = ACEBulkLoader(path="data/data_from_jessi/reports")
data = loader.load()

print(data)

