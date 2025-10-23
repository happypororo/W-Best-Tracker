#!/bin/bash

echo "🧪 Testing W Concept Tracking API Endpoints"
echo "============================================"

echo -e "\n1️⃣ Health Check:"
curl -s http://localhost:8000/api/health | python -m json.tool | head -15

echo -e "\n\n2️⃣ Current Products (Top 3):"
curl -s "http://localhost:8000/api/products/current?limit=3" | python -m json.tool | head -20

echo -e "\n\n3️⃣ Brand Statistics (Top 3):"
curl -s "http://localhost:8000/api/brands/stats?limit=3" | python -m json.tool | head -20

echo -e "\n\n4️⃣ Price Changes:"
curl -s "http://localhost:8000/api/price-changes?limit=2" | python -m json.tool | head -15

echo -e "\n\n5️⃣ Ranking Changes:"
curl -s "http://localhost:8000/api/ranking-changes?limit=2" | python -m json.tool | head -15

echo -e "\n\n6️⃣ Scraping Jobs History:"
curl -s "http://localhost:8000/api/jobs/history?limit=3" | python -m json.tool | head -15

echo -e "\n\n✅ All tests completed!"

