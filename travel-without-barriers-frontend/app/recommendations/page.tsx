"use client";

import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import {
    addToWishlist,
    getAllRecommendations,
    getWishlists,
} from "../lib/api";

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
    affordability_score?: number | null;
    quietness_score?: number | null;
    quality_score?: number | null;
    hidden_gem_score?: number | null;
};

type Wishlist = {
    id: number;
    name: string;
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

export default function RecommendationsPage() {
    const [allRecommendations, setAllRecommendations] = useState<Recommendation[]>(
        []
    );
    const [wishlists, setWishlists] = useState<Wishlist[]>([]);
    const [selectedWishlistId, setSelectedWishlistId] = useState<string>("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(true);
    const [addedMap, setAddedMap] = useState<Record<number, boolean>>({});
    const [addingId, setAddingId] = useState<number | null>(null);

    const [continentFilter, setContinentFilter] = useState("");
    const [countryFilter, setCountryFilter] = useState("");
    const [scorePriority, setScorePriority] = useState("");

    useEffect(() => {
        async function loadData() {
            try {
                setLoading(true);

                const recData = await getAllRecommendations();
                setAllRecommendations(Array.isArray(recData) ? recData : []);

                const token = localStorage.getItem("token");
                if (token) {
                    const wishlistData = await getWishlists();
                    setWishlists(wishlistData);

                    if (wishlistData.length > 0) {
                        setSelectedWishlistId(String(wishlistData[0].id));
                    }
                }
            } catch (error) {
                console.error(error);
                setAllRecommendations([]);
            } finally {
                setLoading(false);
            }
        }

        loadData();
    }, []);

    const filteredRecommendations = useMemo(() => {
        let data = [...allRecommendations];

        if (continentFilter.trim()) {
            data = data.filter(
                (d) =>
                    d.continent &&
                    d.continent.toLowerCase() === continentFilter.toLowerCase()
            );
        }

        if (countryFilter.trim()) {
            data = data.filter(
                (d) =>
                    d.country &&
                    d.country.toLowerCase().includes(countryFilter.trim().toLowerCase())
            );
        }

        if (scorePriority === "affordability") {
            data.sort(
                (a, b) => (b.affordability_score ?? 0) - (a.affordability_score ?? 0)
            );
        } else if (scorePriority === "quietness") {
            data.sort((a, b) => (b.quietness_score ?? 0) - (a.quietness_score ?? 0));
        } else if (scorePriority === "quality") {
            data.sort((a, b) => (b.quality_score ?? 0) - (a.quality_score ?? 0));
        } else if (scorePriority === "hidden_gem") {
            data.sort(
                (a, b) => (b.hidden_gem_score ?? 0) - (a.hidden_gem_score ?? 0)
            );
        } else {
            data.sort((a, b) => (b.barrier_score ?? 0) - (a.barrier_score ?? 0));
        }

        return data;
    }, [allRecommendations, continentFilter, countryFilter, scorePriority]);

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

            await addToWishlist(Number(selectedWishlistId), destinationId);

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

    function clearFilters() {
        setContinentFilter("");
        setCountryFilter("");
        setScorePriority("");
    }

    return (
        <>
            <Navbar />

            <main className="min-h-screen px-6 py-10">
                <div className="max-w-7xl mx-auto">
                    <div className="mb-10">
                        <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-2">
                            Smart destination discovery
                        </p>
                        <h1 className="text-4xl font-bold text-[#007788] mb-3">
                            Explore Destinations
                        </h1>
                        <p className="text-gray-700 max-w-2xl">
                            All destinations are shown by default. Use the filters only if you
                            want to narrow results.
                        </p>
                    </div>

                    {message && (
                        <div className="mb-6 rounded-xl bg-[#f9f9f9] border border-gray-200 p-4 text-sm text-gray-700">
                            {message}
                        </div>
                    )}

                    <div className="mb-8 bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4">Optional filters</h2>

                        <div className="grid md:grid-cols-5 gap-4">
                            <select
                                value={continentFilter}
                                onChange={(e) => setContinentFilter(e.target.value)}
                                className="border border-gray-200 rounded-xl px-4 py-3"
                            >
                                <option value="">All continents</option>
                                <option value="Africa">Africa</option>
                                <option value="Asia">Asia</option>
                                <option value="Europe">Europe</option>
                                <option value="North America">North America</option>
                                <option value="South America">South America</option>
                                <option value="Oceania">Oceania</option>
                            </select>

                            <input
                                type="text"
                                placeholder="Filter by country"
                                value={countryFilter}
                                onChange={(e) => setCountryFilter(e.target.value)}
                                className="border border-gray-200 rounded-xl px-4 py-3"
                            />

                            <select
                                value={scorePriority}
                                onChange={(e) => setScorePriority(e.target.value)}
                                className="border border-gray-200 rounded-xl px-4 py-3"
                            >
                                <option value="">Overall barrier score</option>
                                <option value="affordability">Affordability</option>
                                <option value="quietness">Quietness</option>
                                <option value="quality">Quality</option>
                                <option value="hidden_gem">Hidden gem</option>
                            </select>

                            <select
                                value={selectedWishlistId}
                                onChange={(e) => setSelectedWishlistId(e.target.value)}
                                className="border border-gray-200 rounded-xl px-4 py-3"
                            >
                                <option value="">Select a wishlist</option>
                                {wishlists.map((wishlist) => (
                                    <option key={wishlist.id} value={wishlist.id}>
                                        {wishlist.name}
                                    </option>
                                ))}
                            </select>

                            <button
                                onClick={clearFilters}
                                className="rounded-xl px-4 py-3 border border-gray-200 hover:bg-gray-50 transition"
                            >
                                Clear Filters
                            </button>
                        </div>

                        <p className="text-sm text-gray-500 mt-4">
                            Showing {filteredRecommendations.length} destination
                            {filteredRecommendations.length === 1 ? "" : "s"}
                        </p>
                    </div>

                    {loading ? (
                        <div className="bg-white rounded-[1.5rem] p-8 shadow-md border border-gray-100">
                            <p className="text-gray-600">Loading destinations...</p>
                        </div>
                    ) : allRecommendations.length === 0 ? (
                        <div className="bg-white rounded-[1.5rem] p-8 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-3 text-[#333333]">
                                No destinations available
                            </h2>
                            <p className="text-gray-600">
                                Check that your backend is running and the dataset has been
                                imported.
                            </p>
                        </div>
                    ) : filteredRecommendations.length === 0 ? (
                        <div className="bg-white rounded-[1.5rem] p-8 shadow-md border border-gray-100">
                            <h2 className="text-2xl font-semibold mb-3 text-[#333333]">
                                No results match your filters
                            </h2>
                            <p className="text-gray-600">
                                Try changing or clearing the filters to see all destinations
                                again.
                            </p>
                        </div>
                    ) : (
                        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {filteredRecommendations.map((destination, index) => {
                                const isAdded = !!addedMap[destination.id];
                                const isAdding = addingId === destination.id;
                                const emoji = getHolidayEmoji(destination.type);

                                return (
                                    <div
                                        key={destination.id ?? index}
                                        className="bg-white rounded-[1.5rem] overflow-hidden shadow-md border border-gray-100 hover:shadow-xl transition"
                                    >
                                        <div className="h-48 bg-gradient-to-br from-cyan-100 via-teal-100 to-sky-100 flex items-center justify-center relative">
                                            <span className="text-6xl">{emoji}</span>
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
                                                {destination.continent
                                                    ? ` • ${destination.continent}`
                                                    : ""}
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

                                            <div className="space-y-1 text-sm text-gray-600 mb-5">
                                                <p>Type: {destination.type ?? "N/A"}</p>
                                                <p>Season: {destination.best_season ?? "N/A"}</p>
                                                <p>
                                                    Barrier score:{" "}
                                                    <span className="font-semibold text-[#007788]">
                                                        {destination.barrier_score ?? "N/A"}
                                                    </span>
                                                </p>
                                                <p>
                                                    Hidden gem:{" "}
                                                    <span className="font-semibold text-[#00A896]">
                                                        {destination.hidden_gem_score ?? "N/A"}
                                                    </span>
                                                </p>
                                            </div>

                                            <button
                                                onClick={() => handleAddToWishlist(destination.id)}
                                                disabled={isAdding}
                                                className={`w-full rounded-full py-3 font-medium transition ${isAdded
                                                        ? "bg-[#00A896] text-white"
                                                        : "bg-[#007788] text-white hover:bg-[#006674]"
                                                    } ${isAdding ? "opacity-70 cursor-not-allowed" : ""}`}
                                            >
                                                {isAdded
                                                    ? "Added to Wishlist ✓"
                                                    : isAdding
                                                        ? "Adding..."
                                                        : "Add to Wishlist"}
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