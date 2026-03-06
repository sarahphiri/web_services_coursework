"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { addDestinationToWishlist, getWishlists } from "../lib/api";

type Recommendation = {
    id: number;
    name?: string | null;
    country?: string | null;
    continent?: string | null;
    type?: string | null;
    best_season?: string | null;
    avg_cost_usd?: number | null;
    rating?: number | null;
    annual_visitors_m?: number | null;
    barrier_score?: number | null;
};

type Wishlist = {
    id: number;
    user_id: number;
    name: string;
    description?: string | null;
    created_at: string;
};

function getCostLabel(cost?: number | null) {
    if (cost == null) return "Unknown";
    if (cost < 120) return "Very affordable";
    if (cost < 200) return "Affordable";
    if (cost < 300) return "Moderate";
    return "Premium";
}

function getCrowdLabel(visitors?: number | null) {
    if (visitors == null) return "Unknown";
    if (visitors < 2) return "Very low";
    if (visitors < 5) return "Low";
    if (visitors < 8) return "Moderate";
    return "Busy";
}

function formatCost(cost?: number | null) {
    if (cost == null) return "N/A";
    return `$${cost.toFixed(2)}`;
}

function formatRating(rating?: number | null) {
    if (rating == null) return "N/A";
    return rating.toFixed(1);
}

export default function RecommendationsPage() {
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [wishlists, setWishlists] = useState<Wishlist[]>([]);
    const [selectedWishlistId, setSelectedWishlistId] = useState<string>("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(true);
    const [addedMap, setAddedMap] = useState<Record<number, boolean>>({});
    const [addingId, setAddingId] = useState<number | null>(null);

    useEffect(() => {
        async function loadData() {
            try {
                const recRes = await fetch("http://127.0.0.1:8000/recommendations?limit=10", {
                    cache: "no-store",
                });

                const recData = await recRes.json();

                if (Array.isArray(recData)) {
                    setRecommendations(recData);
                } else {
                    setRecommendations([]);
                }

                const token = localStorage.getItem("token");
                if (token) {
                    const wishlistData = await getWishlists(token);
                    setWishlists(wishlistData);

                    if (wishlistData.length > 0) {
                        setSelectedWishlistId(String(wishlistData[0].id));
                    }
                }
            } catch (error) {
                console.error(error);
                setRecommendations([]);
            } finally {
                setLoading(false);
            }
        }

        loadData();
    }, []);

    async function handleAddToWishlist(destinationId: number) {
        const token = localStorage.getItem("token");

        if (!token) {
            setMessage("Please log in first on the Wishlists page.");
            return;
        }

        if (!selectedWishlistId) {
            setMessage("Please create or select a wishlist first.");
            return;
        }

        try {
            setAddingId(destinationId);
            await addDestinationToWishlist(token, Number(selectedWishlistId), destinationId);

            setAddedMap((prev) => ({
                ...prev,
                [destinationId]: true,
            }));

            setMessage("Destination added to wishlist.");
        } catch (error: any) {
            setMessage(error.message || "Failed to add destination to wishlist.");
        } finally {
            setAddingId(null);
        }
    }

    return (
        <>
            <Navbar />

            <main className="min-h-screen px-6 py-10">
                <div className="max-w-6xl mx-auto">
                    <div className="mb-10">
                        <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-2">
                            Smart destination discovery
                        </p>
                        <h1 className="text-4xl font-bold text-[#007788] mb-3">
                            Recommended Destinations
                        </h1>
                        <p className="text-gray-700 max-w-2xl">
                            Explore destinations selected for affordability, lower crowd
                            levels, and quality - helping users make calmer and more informed
                            travel decisions.
                        </p>
                    </div>

                    {message && (
                        <div className="mb-6 rounded-xl bg-[#f9f9f9] border border-gray-200 p-4 text-sm text-gray-700">
                            {message}
                        </div>
                    )}

                    <div className="mb-8 bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                        <h2 className="text-xl font-semibold mb-3">Save recommendations</h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Log in on the Wishlists page, then choose a wishlist here to save destinations directly.
                        </p>

                        <select
                            value={selectedWishlistId}
                            onChange={(e) => setSelectedWishlistId(e.target.value)}
                            className="w-full md:w-80 border border-gray-200 rounded-xl px-4 py-3"
                        >
                            <option value="">Select a wishlist</option>
                            {wishlists.map((wishlist) => (
                                <option key={wishlist.id} value={wishlist.id}>
                                    {wishlist.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {loading ? (
                        <div className="bg-white rounded-[1.5rem] p-8 shadow-md border border-gray-100">
                            <p className="text-gray-600">Loading recommendations...</p>
                        </div>
                    ) : recommendations.length === 0 ? (
                        <div className="bg-white rounded-[1.5rem] p-8 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-3 text-[#333333]">
                                No recommendations available
                            </h2>
                            <p className="text-gray-600">
                                Make sure the backend is running and the destinations dataset has been imported.
                            </p>
                        </div>
                    ) : (
                        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {recommendations.map((destination, index) => {
                                const isAdded = !!addedMap[destination.id];
                                const isAdding = addingId === destination.id;

                                return (
                                    <div
                                        key={destination.id ?? index}
                                        className="bg-white rounded-[1.5rem] overflow-hidden shadow-md border border-gray-100 hover:shadow-xl transition"
                                    >
                                        <div className="h-48 bg-gradient-to-br from-cyan-100 via-teal-100 to-sky-100 flex items-center justify-center relative">
                                            <span className="text-6xl">🌍</span>
                                            {isAdded && (
                                                <div className="absolute top-4 right-4 bg-[#FFD166] text-[#333333] text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                                                    Added!
                                                </div>
                                            )}
                                        </div>

                                        <div className="p-6">
                                            <h2 className="text-2xl font-semibold mb-2 text-[#333333]">
                                                {destination.name ?? "Unknown destination"}
                                            </h2>

                                            <p className="text-gray-600 mb-4">
                                                {destination.country ?? "Unknown country"}
                                                {destination.continent ? ` • ${destination.continent}` : ""}
                                            </p>

                                            <div className="grid grid-cols-2 gap-4 mb-5 text-sm">
                                                <div className="bg-[#f9f9f9] rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Affordability</p>
                                                    <p className="font-semibold text-[#00A896]">
                                                        {getCostLabel(destination.avg_cost_usd)}
                                                    </p>
                                                </div>

                                                <div className="bg-[#f9f9f9] rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Crowd level</p>
                                                    <p className="font-semibold text-[#007788]">
                                                        {getCrowdLabel(destination.annual_visitors_m)}
                                                    </p>
                                                </div>

                                                <div className="bg-[#f9f9f9] rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Rating</p>
                                                    <p className="font-semibold text-[#FFD166]">
                                                        ⭐ {formatRating(destination.rating)}
                                                    </p>
                                                </div>

                                                <div className="bg-[#f9f9f9] rounded-xl p-3">
                                                    <p className="text-gray-500 mb-1">Cost</p>
                                                    <p className="font-semibold text-[#333333]">
                                                        {formatCost(destination.avg_cost_usd)}
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center text-sm text-gray-600 mb-5">
                                                <span>Type: {destination.type ?? "N/A"}</span>
                                                <span>Season: {destination.best_season ?? "N/A"}</span>
                                            </div>

                                            <div className="mb-4 text-sm text-gray-600">
                                                Barrier score:{" "}
                                                <span className="font-semibold text-[#007788]">
                                                    {destination.barrier_score ?? "N/A"}
                                                </span>
                                            </div>

                                            <button
                                                onClick={() => handleAddToWishlist(destination.id)}
                                                disabled={isAdding}
                                                className={`w-full rounded-full py-3 font-medium transition ${isAdded
                                                        ? "bg-[#00A896] text-white"
                                                        : "bg-[#007788] text-white hover:bg-[#006674]"
                                                    } ${isAdding ? "opacity-70 cursor-not-allowed" : ""}`}
                                            >
                                                {isAdded ? "Added to Wishlist ✓" : isAdding ? "Adding..." : "Add to Wishlist"}
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}