"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import {
    registerUser,
    loginUser,
    getWishlists,
    createWishlist,
    getWishlistItems,
    deleteWishlist,
    deleteWishlistItem,
} from "../lib/api";

type Wishlist = {
    id: number;
    name: string;
    created_at: string;
    items?: WishlistItem[];
};

type WishlistItem = {
    id: number;
    wishlist_id: number;
    destination_id: number;
    notes?: string | null;
    created_at: string;
    name?: string | null;
    country?: string | null;
    continent?: string | null;
    type?: string | null;
    best_season?: string | null;
    avg_cost_usd?: number | null;
    rating?: number | null;
    annual_visitors_m?: number | null;
    unesco?: boolean | null;
};

function getHolidayEmoji(type?: string | null) {
    if (!type) return "🌍";

    const t = type.toLowerCase();

    if (
        t.includes("beach") ||
        t.includes("coast") ||
        t.includes("coastal") ||
        t.includes("seaside")
    )
        return "🏖️";

    if (t.includes("island")) return "🏝️";

    if (
        t.includes("nature") ||
        t.includes("park") ||
        t.includes("wildlife") ||
        t.includes("eco")
    )
        return "🌿";

    if (
        t.includes("mountain") ||
        t.includes("hiking") ||
        t.includes("hill")
    )
        return "⛰️";

    if (
        t.includes("cultural") ||
        t.includes("history") ||
        t.includes("historical") ||
        t.includes("heritage") ||
        t.includes("museum") ||
        t.includes("temple")
    )
        return "🏛️";

    if (
        t.includes("city") ||
        t.includes("urban") ||
        t.includes("metropolitan")
    )
        return "🏙️";

    if (
        t.includes("adventure") ||
        t.includes("activity") ||
        t.includes("sport")
    )
        return "🧗";

    if (t.includes("desert")) return "🏜️";
    if (t.includes("lake")) return "🏞️";
    if (t.includes("forest")) return "🌲";
    if (t.includes("ski") || t.includes("snow")) return "🎿";
    if (t.includes("romantic")) return "💕";
    if (t.includes("luxury")) return "✨";

    return "🌍";
}

export default function WishlistsPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [wishlistName, setWishlistName] = useState("");
    const [token, setToken] = useState("");

    const [wishlists, setWishlists] = useState<Wishlist[]>([]);
    const [selectedWishlistId, setSelectedWishlistId] = useState<string>("");
    const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const savedToken = localStorage.getItem("token");
        if (savedToken) {
            setToken(savedToken);
            loadWishlists();
        }
    }, []);

    useEffect(() => {
        if (selectedWishlistId) {
            loadWishlistItems(Number(selectedWishlistId));
        } else {
            setWishlistItems([]);
        }
    }, [selectedWishlistId]);

    async function loadWishlists() {
        try {
            const data = await getWishlists();
            setWishlists(data);

            if (data.length > 0) {
                const stillExists = data.some(
                    (w: Wishlist) => String(w.id) === selectedWishlistId
                );

                if (!stillExists) {
                    setSelectedWishlistId(String(data[0].id));
                }
            } else {
                setSelectedWishlistId("");
            }
        } catch (error: any) {
            setMessage(error.message || "Failed to load wishlists");
        }
    }

    async function loadWishlistItems(wishlistId: number) {
        try {
            const data = await getWishlistItems(wishlistId);
            setWishlistItems(data);
        } catch (error: any) {
            setMessage(error.message || "Failed to load wishlist items");
        }
    }

    async function handleRegister() {
        setLoading(true);
        setMessage("");

        try {
            await registerUser(email, password);
            setMessage("Registration successful. You can now log in.");
        } catch (error: any) {
            setMessage(error.message || "Registration failed");
        } finally {
            setLoading(false);
        }
    }

    async function handleLogin() {
        setLoading(true);
        setMessage("");

        try {
            const data = await loginUser(email, password);
            localStorage.setItem("token", data.access_token);
            setToken(data.access_token);
            setMessage("Login successful");
            await loadWishlists();
        } catch (error: any) {
            setMessage(error.message || "Login failed");
        } finally {
            setLoading(false);
        }
    }

    async function handleCreateWishlist() {
        if (!token) {
            setMessage("Please log in first");
            return;
        }

        if (!wishlistName.trim()) {
            setMessage("Please enter a wishlist name");
            return;
        }

        setLoading(true);
        setMessage("");

        try {
            const newWishlist = await createWishlist(wishlistName);
            setMessage("Wishlist created successfully");
            setWishlistName("");
            await loadWishlists();
            setSelectedWishlistId(String(newWishlist.id));
            await loadWishlistItems(newWishlist.id);
        } catch (error: any) {
            setMessage(error.message || "Failed to create wishlist");
        } finally {
            setLoading(false);
        }
    }

    async function handleDeleteWishlist() {
        if (!token || !selectedWishlistId) {
            setMessage("Please select a wishlist first.");
            return;
        }

        try {
            await deleteWishlist(Number(selectedWishlistId));
            setMessage("Wishlist deleted.");
            await loadWishlists();
        } catch (error: any) {
            setMessage(error.message || "Failed to delete wishlist");
        }
    }

    async function handleRemoveFromWishlist(itemId: number) {
        if (!token || !selectedWishlistId) {
            setMessage("Please select a wishlist first.");
            return;
        }

        try {
            await deleteWishlistItem(Number(selectedWishlistId), itemId);
            setMessage("Destination removed from wishlist.");
            await loadWishlistItems(Number(selectedWishlistId));
        } catch (error: any) {
            setMessage(error.message || "Failed to remove destination");
        }
    }

    function handleLogout() {
        localStorage.removeItem("token");
        setToken("");
        setWishlists([]);
        setWishlistItems([]);
        setSelectedWishlistId("");
        setMessage("Logged out");
    }

    return (
        <>
            <Navbar />

            <main className="min-h-screen px-6 py-10">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-10">
                        <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-2">
                            Save destinations
                        </p>

                        <h1 className="text-4xl font-bold text-[#007788] mb-3">
                            Wishlists
                        </h1>

                        <p className="text-gray-700 max-w-2xl">
                            Create an account, log in, and organise low-stress destinations
                            into travel wishlists.
                        </p>
                    </div>

                    {message && (
                        <div className="mb-6 rounded-xl bg-[#f9f9f9] border border-gray-200 p-4 text-sm text-gray-700">
                            {message}
                        </div>
                    )}

                    <div className="grid lg:grid-cols-2 gap-6 mb-8">
                        <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-4">Register / Login</h2>

                            <div className="space-y-4">
                                <input
                                    type="email"
                                    placeholder="Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full border border-gray-200 rounded-xl px-4 py-3"
                                />

                                <input
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full border border-gray-200 rounded-xl px-4 py-3"
                                />

                                <div className="flex gap-3">
                                    <button
                                        onClick={handleRegister}
                                        disabled={loading}
                                        className="flex-1 rounded-full border border-[#007788] text-[#007788] py-3 font-medium hover:bg-[#eaf8f7] transition disabled:opacity-50"
                                    >
                                        Register
                                    </button>

                                    <button
                                        onClick={handleLogin}
                                        disabled={loading}
                                        className="flex-1 rounded-full bg-[#007788] text-white py-3 font-medium hover:bg-[#006674] transition disabled:opacity-50"
                                    >
                                        Login
                                    </button>
                                </div>

                                {token && (
                                    <button
                                        onClick={handleLogout}
                                        className="w-full rounded-full border border-red-300 text-red-600 py-3 font-medium hover:bg-red-50 transition"
                                    >
                                        Logout
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-4">Create a Wishlist</h2>

                            <div className="space-y-4">
                                <input
                                    type="text"
                                    placeholder="Wishlist name"
                                    value={wishlistName}
                                    onChange={(e) => setWishlistName(e.target.value)}
                                    className="w-full border border-gray-200 rounded-xl px-4 py-3"
                                />

                                <button
                                    onClick={handleCreateWishlist}
                                    disabled={loading}
                                    className="w-full rounded-full bg-[#007788] text-white py-3 font-medium hover:bg-[#006674] transition disabled:opacity-50"
                                >
                                    Create Wishlist
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="grid lg:grid-cols-[320px_1fr] gap-6">
                        <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100 h-fit">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-2xl font-semibold">Your Wishlists</h2>

                                {selectedWishlistId && (
                                    <button
                                        onClick={handleDeleteWishlist}
                                        className="text-sm px-3 py-2 rounded-full bg-red-50 text-red-600 hover:bg-red-100 transition"
                                    >
                                        Delete
                                    </button>
                                )}
                            </div>

                            {wishlists.length === 0 ? (
                                <p className="text-gray-600">
                                    No wishlists yet. Log in and create one to get started.
                                </p>
                            ) : (
                                <div className="space-y-3">
                                    {wishlists.map((wishlist) => {
                                        const isSelected =
                                            String(wishlist.id) === selectedWishlistId;

                                        return (
                                            <button
                                                key={wishlist.id}
                                                onClick={() =>
                                                    setSelectedWishlistId(String(wishlist.id))
                                                }
                                                className={`w-full text-left rounded-xl p-4 border transition ${isSelected
                                                        ? "bg-[#eaf8f7] border-[#00A896]"
                                                        : "bg-[#f9f9f9] border-gray-100 hover:border-[#00A896]"
                                                    }`}
                                            >
                                                <p className="font-semibold text-lg">{wishlist.name}</p>
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-4">Saved Destinations</h2>

                            {!selectedWishlistId ? (
                                <p className="text-gray-600">
                                    Select a wishlist to view its saved destinations.
                                </p>
                            ) : wishlistItems.length === 0 ? (
                                <p className="text-gray-600">
                                    No destinations saved yet. Add some from the Recommendations
                                    page.
                                </p>
                            ) : (
                                <div className="grid md:grid-cols-2 gap-4">
                                    {wishlistItems.map((item) => (
                                        <div
                                            key={item.id}
                                            className="rounded-[1.25rem] border border-gray-100 bg-[#f9f9f9] p-5"
                                        >
                                            <div className="flex items-start justify-between gap-3 mb-3">
                                                <h3 className="text-xl font-semibold text-[#333333]">
                                                    {item.name ?? "Unknown destination"}
                                                </h3>
                                                <span className="text-2xl">
                                                    {getHolidayEmoji(item.type)}
                                                </span>
                                            </div>

                                            <p className="text-gray-600 mb-3">
                                                {item.country ?? "Unknown country"}
                                                {item.continent ? ` • ${item.continent}` : ""}
                                            </p>

                                            <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                                                <div className="bg-white rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Rating</p>
                                                    <p className="font-semibold text-[#FFD166]">
                                                        ⭐ {item.rating ?? "N/A"}
                                                    </p>
                                                </div>

                                                <div className="bg-white rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Cost</p>
                                                    <p className="font-semibold text-[#333333]">
                                                        {item.avg_cost_usd != null
                                                            ? `$${item.avg_cost_usd}`
                                                            : "N/A"}
                                                    </p>
                                                </div>

                                                <div className="bg-white rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Type</p>
                                                    <p className="font-semibold text-[#007788]">
                                                        {item.type ?? "N/A"}
                                                    </p>
                                                </div>

                                                <div className="bg-white rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Season</p>
                                                    <p className="font-semibold text-[#00A896]">
                                                        {item.best_season ?? "N/A"}
                                                    </p>
                                                </div>
                                            </div>

                                            <button
                                                onClick={() => handleRemoveFromWishlist(item.id)}
                                                className="w-full rounded-full bg-red-50 text-red-600 py-3 font-medium hover:bg-red-100 transition"
                                            >
                                                Remove from Wishlist
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </>
    );
}