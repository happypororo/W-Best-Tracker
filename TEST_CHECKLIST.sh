#!/bin/bash
# 배포 후 테스트 체크리스트

echo "🧪 Testing W-Best-Tracker after deployment"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s https://w-best-tracker.fly.dev/api/health)
echo "$response" | jq '.'
db_connected=$(echo "$response" | jq -r '.database_connected')

if [ "$db_connected" = "true" ]; then
    echo "✅ Database connected"
else
    echo "❌ Database NOT connected"
    exit 1
fi
echo ""

# Test 2: Manual Crawl Trigger
echo "Test 2: Manual Crawl Trigger"
echo "-----------------------------"
response=$(curl -s -X POST https://w-best-tracker.fly.dev/api/crawl/trigger)
echo "$response" | jq '.'
status=$(echo "$response" | jq -r '.status')

if [ "$status" = "started" ]; then
    echo "✅ Crawl triggered successfully"
    echo "⏳ Waiting 3 minutes for crawl to complete..."
    sleep 180
elif [ "$status" = "error" ]; then
    detail=$(echo "$response" | jq -r '.detail')
    if [[ "$detail" == *"already in progress"* ]]; then
        echo "⚠️  Crawl already in progress - this is OK"
        echo "⏳ Waiting 3 minutes..."
        sleep 180
    else
        echo "❌ Unexpected error: $detail"
        exit 1
    fi
else
    echo "❌ Unexpected status: $status"
    exit 1
fi
echo ""

# Test 3: Verify Data Updated
echo "Test 3: Verify Data Updated"
echo "----------------------------"
response=$(curl -s https://w-best-tracker.fly.dev/api/health)
latest=$(echo "$response" | jq -r '.latest_collection')
echo "Latest collection: $latest"

if [ "$latest" != "null" ]; then
    echo "✅ Data exists"
else
    echo "⚠️  No data yet (first crawl may still be running)"
fi
echo ""

# Test 4: Concurrent Crawl Prevention
echo "Test 4: Concurrent Crawl Prevention"
echo "------------------------------------"
response=$(curl -s -X POST https://w-best-tracker.fly.dev/api/crawl/trigger)
echo "$response" | jq '.'
status=$(echo "$response" | jq -r '.status // .detail')

if [[ "$status" == *"already in progress"* ]]; then
    echo "✅ Concurrent crawl prevented (HTTP 409)"
else
    echo "⚠️  Expected 409, got: $status"
fi
echo ""

# Test 5: API Performance (during crawl)
echo "Test 5: API Performance (during crawl)"
echo "---------------------------------------"
start_time=$(date +%s)
response=$(curl -s https://w-best-tracker.fly.dev/api/products/current?limit=10)
end_time=$(date +%s)
duration=$((end_time - start_time))

products=$(echo "$response" | jq 'length')
echo "Fetched $products products in ${duration}s"

if [ "$products" -gt 0 ] && [ "$duration" -lt 5 ]; then
    echo "✅ API responsive during crawl (no DB lock)"
else
    echo "⚠️  API slow or no data"
fi
echo ""

# Summary
echo "=========================================="
echo "🎉 All tests completed!"
echo ""
echo "Next steps:"
echo "1. Check Dashboard: https://w-concept-tracker.pages.dev"
echo "2. Monitor next scheduled crawl (every hour at :20)"
echo "3. Check GitHub Actions logs if issues occur"
echo ""
echo "Useful commands:"
echo "- Health: curl https://w-best-tracker.fly.dev/api/health | jq"
echo "- Trigger: curl -X POST https://w-best-tracker.fly.dev/api/crawl/trigger"
echo "- Products: curl https://w-best-tracker.fly.dev/api/products/current | jq"
