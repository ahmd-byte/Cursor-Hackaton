"""
Tests for bucket (money jar) endpoints.
"""

import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient, user_data: dict) -> str:
    """Helper to register user and get auth token."""
    await client.post("/api/v1/auth/register", json=user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_bucket(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test creating a bucket."""
    token = await get_auth_token(client, test_user_data)
    
    response = await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_bucket_data["name"]
    assert float(data["target_amount"]) == test_bucket_data["target_amount"]
    assert data["category"] == test_bucket_data["category"]
    assert "id" in data


@pytest.mark.asyncio
async def test_list_buckets(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test listing buckets."""
    token = await get_auth_token(client, test_user_data)
    
    # Create multiple buckets
    await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    await client.post(
        "/api/v1/buckets",
        json={**test_bucket_data, "name": "Vacation Fund"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # List buckets
    response = await client.get(
        "/api/v1/buckets",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_bucket(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test getting a specific bucket."""
    token = await get_auth_token(client, test_user_data)
    
    # Create bucket
    create_response = await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    bucket_id = create_response.json()["id"]
    
    # Get bucket
    response = await client.get(
        f"/api/v1/buckets/{bucket_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bucket_id
    assert data["name"] == test_bucket_data["name"]


@pytest.mark.asyncio
async def test_update_bucket(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test updating a bucket."""
    token = await get_auth_token(client, test_user_data)
    
    # Create bucket
    create_response = await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    bucket_id = create_response.json()["id"]
    
    # Update bucket
    response = await client.put(
        f"/api/v1/buckets/{bucket_id}",
        json={"name": "Updated Name", "target_amount": 15000.00},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert float(data["target_amount"]) == 15000.00


@pytest.mark.asyncio
async def test_deposit_to_bucket(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test depositing to a bucket."""
    token = await get_auth_token(client, test_user_data)
    
    # Create bucket
    create_response = await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    bucket_id = create_response.json()["id"]
    
    # Deposit
    response = await client.post(
        f"/api/v1/buckets/{bucket_id}/deposit",
        json={"amount": 500.00, "description": "Test deposit"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["current_amount"]) == 500.00


@pytest.mark.asyncio
async def test_delete_bucket(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test deleting a bucket."""
    token = await get_auth_token(client, test_user_data)
    
    # Create bucket
    create_response = await client.post(
        "/api/v1/buckets",
        json=test_bucket_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    bucket_id = create_response.json()["id"]
    
    # Delete bucket
    response = await client.delete(
        f"/api/v1/buckets/{bucket_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = await client.get(
        f"/api/v1/buckets/{bucket_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_bucket_summary(client: AsyncClient, test_user_data: dict, test_bucket_data: dict):
    """Test getting bucket summary."""
    token = await get_auth_token(client, test_user_data)
    
    # Create bucket with initial deposit
    bucket_with_amount = {**test_bucket_data, "initial_amount": 1000.00}
    await client.post(
        "/api/v1/buckets",
        json=bucket_with_amount,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get summary
    response = await client.get(
        "/api/v1/buckets/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_buckets"] == 1
    assert float(data["total_saved"]) == 1000.00

