import httpx

DATA_GOV_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad38d07d4be62bbb97"  # free public key


async def fetch_market_prices(crop_name: str, state: str = None) -> dict:
    params = {
        "api-key": DATA_GOV_KEY,
        "format": "json",
        "filters[commodity]": crop_name.capitalize(),
        "limit": 10,
    }
    if state:
        params["filters[state]"] = state.capitalize()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DATA_GOV_API, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("records") and len(data["records"]) > 0:
                return {
                    "success": True,
                    "crop": crop_name,
                    "records": data["records"],
                    "total": data.get("total", 0)
                }
            else:
                return {
                    "success": False,
                    "message": f"No market data found for {crop_name}."
                }
    except httpx.TimeoutException:
        return {"success": False, "message": "Market API timed out."}
    except Exception as e:
        return {"success": False, "message": f"Could not fetch market data: {str(e)}"}