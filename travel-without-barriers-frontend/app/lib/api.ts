const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

function getAuthHeaders(token?: string): HeadersInit {
    if (token) {
        return {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        };
    }

    return {
        "Content-Type": "application/json",
    };
}

async function parseResponse(res: Response) {
    const text = await res.text();

    let data: any = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch {
        data = null;
    }

    if (!res.ok) {
        throw new Error(
            data?.detail ||
            data?.message ||
            text ||
            `Request failed with status ${res.status}`
        );
    }

    return data;
}

export async function registerUser(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ email, password }),
    });

    return parseResponse(res);
}

export async function loginUser(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ email, password }),
    });

    return parseResponse(res);
}

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
        headers: getAuthHeaders(),
        cache: "no-store",
    });

    return parseResponse(res);
}

export async function getWishlists(token: string) {
    const res = await fetch(`${API_BASE_URL}/wishlists`, {
        method: "GET",
        headers: getAuthHeaders(token),
        cache: "no-store",
    });

    return parseResponse(res);
}

export async function createWishlist(
    token: string,
    name: string,
    description = ""
) {
    const res = await fetch(`${API_BASE_URL}/wishlists`, {
        method: "POST",
        headers: getAuthHeaders(token),
        body: JSON.stringify({ name, description }),
    });

    return parseResponse(res);
}

export async function deleteWishlist(token: string, wishlistId: number) {
    const res = await fetch(`${API_BASE_URL}/wishlists/${wishlistId}`, {
        method: "DELETE",
        headers: getAuthHeaders(token),
    });

    return parseResponse(res);
}

export async function getWishlistItems(token: string, wishlistId: number) {
    const res = await fetch(`${API_BASE_URL}/wishlists/${wishlistId}/items`, {
        method: "GET",
        headers: getAuthHeaders(token),
        cache: "no-store",
    });

    return parseResponse(res);
}

export async function addDestinationToWishlist(
    token: string,
    wishlistId: number,
    destinationId: number,
    notes = "",
    priority?: number
) {
    const res = await fetch(`${API_BASE_URL}/wishlists/${wishlistId}/items`, {
        method: "POST",
        headers: getAuthHeaders(token),
        body: JSON.stringify({
            destination_id: destinationId,
            notes,
            priority,
        }),
    });

    return parseResponse(res);
}

export async function deleteWishlistItem(
    token: string,
    wishlistId: number,
    itemId: number
) {
    const res = await fetch(
        `${API_BASE_URL}/wishlists/${wishlistId}/items/${itemId}`,
        {
            method: "DELETE",
            headers: getAuthHeaders(token),
        }
    );

    return parseResponse(res);
}