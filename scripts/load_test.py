"""Load testing for 10,000 concurrent users"""
import asyncio
import aiohttp
import time
from typing import List

async def make_request(session, url, api_key):
    """Single API request"""
    start = time.time()
    headers = {"api-key": api_key, "api_key": api_key} # Support both headers
    try:
        async with session.get(url, headers=headers) as response:
            latency = time.time() - start
            return response.status, latency
    except Exception:
        return 500, 0

async def load_test(concurrent: int, duration: int = 60):
    """Run load test"""
    url = "https://api.sp500predictor.com/v2/predict?days=5"
    api_key = "test_key_123"
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        print(f"🚀 Starting load test: {concurrent} concurrent users for {duration} seconds")
        
        # Generate load (simplified for demo)
        while time.time() - start_time < duration:
            batch = [make_request(session, url, api_key) for _ in range(concurrent // 10)]
            tasks.extend(batch)
            await asyncio.sleep(0.1)
        
        # Collect results
        results = await asyncio.gather(*tasks)
        
        # Calculate metrics
        statuses = [r[0] for r in results]
        latencies = [r[1] for r in results if r[1] > 0]
        
        print(f"📊 Load Test Results")
        print(f"✅ Success rate: {statuses.count(200)/max(1, len(statuses))*100:.1f}%")
        if latencies:
            print(f"⚡ Avg latency: {sum(latencies)/len(latencies)*1000:.1f}ms")
        print(f"🚀 Peak RPS: {len(tasks)/duration:.1f}")

if __name__ == "__main__":
    import sys
    conc = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    asyncio.run(load_test(concurrent=conc, duration=dur))
