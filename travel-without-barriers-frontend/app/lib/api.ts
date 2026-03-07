const API_BASE_URL = "http://127.0.0.1:8000";

/* =========================
   AUTH
========================= */

export async function registerUser(username: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Register error:", errorText);
        throw new Error(errorText || "Failed to register user");
    }

    return res.json();
}

export async function loginUser(username: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Login error:", errorText);
        throw new Error(errorText || "Failed to login");
    }

    return res.json();
}

/* =========================
   RECOMMENDATIONS
========================= */

export async function getAllRecommendations(filters?: {
    continent?: string;
    country?: string;
    min_rating?: number;
    max_cost?: number;
    sort_by?: string;
}) {
    const params = new URLSearchParams();

    if (filters?.continent) params.append("continent", filters.continent);
    if (filters?.country) params.append("country", filters.country);
    if (filters?.min_rating !== undefined) {
        params.append("min_rating", String(filters.min_rating));
    }
    if (filters?.max_cost !== undefined) {
        params.append("max_cost", String(filters.max_cost));
    }
    if (filters?.sort_by) params.append("sort_by", filters.sort_by);

    const url = `${API_BASE_URL}/recommendations${params.toString() ? `?${params.toString()}` : ""
        }`;

    const res = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        cache: "no-store",
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Recommendations error:", errorText);
        throw new Error(errorText || "Failed to fetch recommendations");
    }

    return res.json();
}

/* =========================
   WISHLISTS
========================= */

export async function getWishlists() {
    const res = await fetch(`${API_BASE_URL}/wishlists`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        cache: "no-store",
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Wishlists error:", errorText);
        throw new Error(errorText || "Failed to fetch wishlists");
    }

    return res.json();
}

export async function createWishlist(name: string) {
    const res = await fetch(`${API_BASE_URL}/wishlists`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Create wishlist error:", errorText);
        throw new Error(errorText || "Failed to create wishlist");
    }

    return res.json();
}

export async function deleteWishlist(wishlistId: number) {
    const res = await fetch(`${API_BASE_URL}/wishlists/${wishlistId}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Delete wishlist error:", errorText);
        throw new Error(errorText || "Failed to delete wishlist");
    }

    return res.json();
}

export async function addToWishlist(
    wishlistId: number,
    destinationId: number,
    notes: string = ""
) {
    const res = await fetch(`${API_BASE_URL}/wishlists/${wishlistId}/items`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            destination_id: destinationId,
            notes,
        }),
    });

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Add to wishlist error:", errorText);
        throw new Error(errorText || "Failed to add to wishlist");
    }

    return res.json();
}

export async function removeFromWishlist(wishlistId: number, itemId: number) {
    const res = await fetch(
        `${API_BASE_URL}/wishlists/${wishlistId}/items/${itemId}`,
        {
            method: "DELETE",
        }
    );

    if (!res.ok) {
        const errorText = await res.text();
        console.error("Remove from wishlist error:", errorText);
        throw new Error(errorText || "Failed to remove from wishlist");
    }

    return res.json();
}

/* IMPORTANT:
   Your page is importing deleteWishlistItem, so export that exact name too.
*/
export async function deleteWishlistItem(
    wishlistId: number,
    itemId: number
) {
    return removeFromWishlist(wishlistId, itemId);
}

/* IMPORTANT:
   Your page is importing getWishlistItems, so export that exact name too.
*/
export async function getWishlistItems(wishlistId: number) {
    const wishlists = await getWishlists();
    const wishlist = wishlists.find((w: any) => w.id === wishlistId);
    return wishlist?.items || [];
}