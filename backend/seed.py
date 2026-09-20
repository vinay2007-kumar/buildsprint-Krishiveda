"""Seed DB with crops + diseases for demo."""
import asyncio
from backend.database import AsyncSessionLocal, init_db
from backend.models import Crop, Disease

CROPS = [
    ("wheat", "Triticum aestivum", "cereal", "rabi"),
    ("rice", "Oryza sativa", "cereal", "kharif"),
    ("tomato", "Solanum lycopersicum", "vegetable", "rabi"),
    ("potato", "Solanum tuberosum", "vegetable", "rabi"),
    ("cotton", "Gossypium hirsutum", "fibre", "kharif"),
]

async def main():
    await init_db()
    async with AsyncSessionLocal() as s:
        for name, sci, cat, season in CROPS:
            s.add(Crop(name=name, scientific_name=sci, category=cat, growing_season=season))
        await s.commit()
    print("Seeded crops.")

if __name__ == "__main__":
    asyncio.run(main())
