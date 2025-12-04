import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from api.main import app
from api.chat_bot.table_detail_routes import get_repository
from api.chat_bot.models import TableDetails

# Mock Repository
mock_repo = MagicMock()

def override_get_repository():
    return mock_repo

app.dependency_overrides[get_repository] = override_get_repository

client = TestClient(app)

def test_table_details_crud():
    print("Testing Create...")
    mock_item = TableDetails(id=1, table_description="Test Table", embedding=[0.1, 0.2])
    mock_repo.add.return_value = mock_item
    
    response = client.post(
        "/table-details",
        json={"table_description": "Test Table"}
    )
    if response.status_code != 200:
        print(f"Create failed: {response.text}")
        sys.exit(1)
    data = response.json()
    assert data["table_description"] == "Test Table"
    assert data["id"] == 1
    print("Create passed.")

    print("Testing Get All...")
    mock_repo.get_all.return_value = [mock_item]
    response = client.get("/table-details")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    print("Get All passed.")

    print("Testing Get By ID...")
    mock_repo.get_by_id.return_value = mock_item
    response = client.get("/table-details/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    print("Get By ID passed.")

    print("Testing Search...")
    mock_repo.search.return_value = [mock_item]
    response = client.post("/table-details/search?query=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    print("Search passed.")

    print("Testing Delete...")
    mock_repo.delete.return_value = True
    response = client.delete("/table-details/1")
    assert response.status_code == 200
    print("Delete passed.")

if __name__ == "__main__":
    test_table_details_crud()
    print("All tests passed!")
