import os
from typing import Optional, Dict, Any, List
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
TIMEOUT = 10


class BidSphereAPIClient:
    """Centralized HTTP client communicating with FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        token = st.session_state.get("access_token")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text or "Unknown response from server."}

        if response.status_code >= 400:
            error_msg = data.get("detail", "An error occurred.")
            if isinstance(error_msg, list):  # Pydantic validation error array
                error_msg = "; ".join([f"{e.get('loc', [''])[ -1]}: {e.get('msg', '')}" for e in error_msg])
            raise requests.HTTPError(error_msg, response=response)
        return data

    def check_health(self) -> Dict[str, Any]:
        try:
            res = requests.get(f"{self.base_url}/health", timeout=3)
            return self._handle_response(res)
        except requests.exceptions.ConnectionError:
            return {
                "status": "unhealthy",
                "connected": False,
                "detail": "FastAPI backend is unreachable. Ensure Uvicorn is running on port 8000.",
                "database": {"connected": False},
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "detail": str(e),
                "database": {"connected": False},
            }

    # --- Authentication & Users ---
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/auth/login",
            json={"username_or_email": username_or_email, "password": password},
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.post(f"{self.base_url}/auth/register", json=data, timeout=TIMEOUT)
        return self._handle_response(res)

    def get_me(self) -> Dict[str, Any]:
        res = requests.get(f"{self.base_url}/auth/me", headers=self._headers(), timeout=TIMEOUT)
        return self._handle_response(res)

    # --- Auctions ---
    def get_categories(self) -> List[Dict[str, Any]]:
        res = requests.get(f"{self.base_url}/auctions/categories", timeout=TIMEOUT)
        return self._handle_response(res)

    def get_auctions(
        self,
        status: Optional[str] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = "closing_soon",
    ) -> List[Dict[str, Any]]:
        params = {}
        if status and status != "ALL":
            params["status"] = status
        if category_id:
            params["category_id"] = category_id
        if search:
            params["search"] = search
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if sort_by:
            params["sort_by"] = sort_by

        res = requests.get(
            f"{self.base_url}/auctions",
            params=params,
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_auction(self, auction_id: int) -> Dict[str, Any]:
        res = requests.get(
            f"{self.base_url}/auctions/{auction_id}",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def create_auction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/auctions",
            json=data,
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def update_auction(self, auction_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        res = requests.put(
            f"{self.base_url}/auctions/{auction_id}",
            json=data,
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def cancel_auction(self, auction_id: int) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/auctions/{auction_id}/cancel",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def close_auction(self, auction_id: int) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/auctions/{auction_id}/close",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    # --- Bids ---
    def place_bid(self, auction_id: int, bid_amount: float) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/bids/auctions/{auction_id}",
            json={"bid_amount": bid_amount},
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_auction_bids(self, auction_id: int) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/bids/auctions/{auction_id}", timeout=TIMEOUT
        )
        return self._handle_response(res)

    def get_my_bids(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/bids/my-bids", headers=self._headers(), timeout=TIMEOUT
        )
        return self._handle_response(res)

    # --- Watchlist ---
    def add_to_watchlist(self, auction_id: int) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/watchlist/{auction_id}",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def remove_from_watchlist(self, auction_id: int) -> Dict[str, Any]:
        res = requests.delete(
            f"{self.base_url}/watchlist/{auction_id}",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_my_watchlist(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/watchlist", headers=self._headers(), timeout=TIMEOUT
        )
        return self._handle_response(res)

    # --- Payments ---
    def submit_payment(self, result_id: int, payment_method: str) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/payments",
            json={"result_id": result_id, "payment_method": payment_method},
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_my_payments(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/payments/my-payments",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    # --- Notifications ---
    def get_notifications(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/notifications",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_unread_count(self) -> int:
        try:
            res = requests.get(
                f"{self.base_url}/notifications/unread-count",
                headers=self._headers(),
                timeout=3,
            )
            data = self._handle_response(res)
            return data.get("unread_count", 0)
        except Exception:
            return 0

    def mark_notification_read(self, notification_id: int) -> Dict[str, Any]:
        res = requests.put(
            f"{self.base_url}/notifications/{notification_id}/read",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def mark_all_notifications_read(self) -> Dict[str, Any]:
        res = requests.put(
            f"{self.base_url}/notifications/mark-all-read",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    # --- Dashboards ---
    def get_seller_dashboard(self) -> Dict[str, Any]:
        res = requests.get(
            f"{self.base_url}/dashboard/seller",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_buyer_dashboard(self) -> Dict[str, Any]:
        res = requests.get(
            f"{self.base_url}/dashboard/buyer",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_auction_results(self) -> List[Dict[str, Any]]:
        res = requests.get(f"{self.base_url}/dashboard/results", timeout=TIMEOUT)
        return self._handle_response(res)

    # --- Admin ---
    def get_admin_dashboard(self) -> Dict[str, Any]:
        res = requests.get(
            f"{self.base_url}/admin/dashboard",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_all_users(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/admin/users",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def toggle_user_active(self, user_id: int) -> Dict[str, Any]:
        res = requests.put(
            f"{self.base_url}/admin/users/{user_id}/toggle-active",
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{self.base_url}/admin/audit-logs",
            params={"limit": limit},
            headers=self._headers(),
            timeout=TIMEOUT,
        )
        return self._handle_response(res)


# Singleton instance
api_client = BidSphereAPIClient()
