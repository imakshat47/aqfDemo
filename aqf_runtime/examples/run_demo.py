
from pathlib import Path
from aqf_runtime.pipeline import AQFPipeline

pipeline = AQFPipeline()
result = pipeline.generate('sample_dataset.json')
pipeline.export_all(result, Path(__file__).parent.parent/'exports')
print('AQF demo artifacts exported')
