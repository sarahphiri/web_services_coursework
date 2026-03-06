const API_BASE = "http://127.0.0.1:8000";

export async function registerUser(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to register");
    }

    return res.json();
}

export async function loginUser(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to login");
    }

    return res.json();
}

export async function getWishlists(token: string) {
    const res = await fetch(`${API_BASE}/wishlists`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to fetch wishlists");
    }

    return res.json();
}

export async function createWishlist(
    token: string,
    name: string,
    description: string
) {
    const res = await fetch(`${API_BASE}/wishlists`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to create wishlist");
    }

    return res.json();
}

export async function addDestinationToWishlist(
    token: string,
    wishlistId: number,
    destinationId: number
) {
    const res = await fetch(`${API_BASE}/wishlists/${wishlistId}/items`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            destination_id: destinationId,
            notes: null,
            priority: null,
        }),
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to add destination to wishlist");
    }

    return res.json();
}

export async function getWishlistItems(token: string, wishlistId: number) {
    const res = await fetch(`${API_BASE}/wishlists/${wishlistId}/items`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Failed to fetch wishlist items");
    }

    return res.json();
}