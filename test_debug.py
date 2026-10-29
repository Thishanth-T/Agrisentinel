import asyncio
import os
from advisor_service import GroqAdvisoryService

print("Testing Avocado...")
res = asyncio.run(GroqAdvisoryService.get_agronomic_advisory("plot_1", "Avocado", 20.0, 28.0, 0.0))
print("Result:", res["status"])
