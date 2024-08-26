from ace import ACEBulkLoader

# Example usage of ACEBulkLoader
loader = ACEBulkLoader(path="data/color_picking/ucsf_ace", data_type="explorer")
data = loader.load()

print(data)

