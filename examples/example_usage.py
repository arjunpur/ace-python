from ace import ACEBulkLoader
from ace import load_ace_bulk

# Example usage of ACEBulkLoader
# loader = ACEBulkLoader(path="data/data_from_jessi/reports")
# data = loader.data_by_filename

data = load_ace_bulk(path="data/data_from_jessi/reports")
print(data)

 