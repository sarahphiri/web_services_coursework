"use client";

import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import {
    registerUser,
    loginUser,
    getWishlists,
    createWishlist,
} from "../lib/api";

type Wishlist = {
    id: number;
    user_id: number;
    name: string;
    description?: string | null;
    created_at: string;
};

export default function WishlistsPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [wishlistName, setWishlistName] = useState("");
    const [wishlistDescription, setWishlistDescription] = useState("");

    const [token, setToken] = useState("");
    const [wishlists, setWishlists] = useState<Wishlist[]>([]);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const savedToken = localStorage.getItem("token");
        if (savedToken) {
            setToken(savedToken);
            loadWishlists(savedToken);
        }
    }, []);

    async function loadWishlists(authToken: string) {
        try {
            const data = await getWishlists(authToken);
            setWishlists(data);
        } catch (error: any) {
            setMessage(error.message || "Failed to load wishlists");
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
            await loadWishlists(data.access_token);
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

        setLoading(true);
        setMessage("");

        try {
            await createWishlist(token, wishlistName, wishlistDescription);
            setMessage("Wishlist created successfully");
            setWishlistName("");
            setWishlistDescription("");
            await loadWishlists(token);
        } catch (error: any) {
            setMessage(error.message || "Failed to create wishlist");
        } finally {
            setLoading(false);
        }
    }

    function handleLogout() {
        localStorage.removeItem("token");
        setToken("");
        setWishlists([]);
        setMessage("Logged out");
    }

    return (
        <>
            <Navbar />

            <main className="min-h-screen px-6 py-10">
                <div className="max-w-5xl mx-auto">
                    <div className="mb-10">
                        <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-2">
                            Save destinations
                        </p>

                        <h1 className="text-4xl font-bold text-[#007788] mb-3">
                            Wishlists
                        </h1>

                        <p className="text-gray-700 max-w-2xl">
                            Create an account, log in, and save low-stress destinations for
                            future trips.
                        </p>
                    </div>

                    {message && (
                        <div className="mb-6 rounded-xl bg-[#f9f9f9] border border-gray-200 p-4 text-sm text-gray-700">
                            {message}
                        </div>
                    )}

                    <div className="grid md:grid-cols-2 gap-6 mb-8">
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

                                <textarea
                                    placeholder="Description"
                                    value={wishlistDescription}
                                    onChange={(e) => setWishlistDescription(e.target.value)}
                                    className="w-full border border-gray-200 rounded-xl px-4 py-3 min-h-[120px]"
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

                    <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
                        <h2 className="text-2xl font-semibold mb-4">Your Wishlists</h2>

                        {wishlists.length === 0 ? (
                            <p className="text-gray-600">
                                No wishlists yet. Log in and create one to get started.
                            </p>
                        ) : (
                            <div className="space-y-4">
                                {wishlists.map((wishlist) => (
                                    <div
                                        key={wishlist.id}
                                        className="rounded-xl bg-[#f9f9f9] p-4 border border-gray-100"
                                    >
                                        <p className="font-semibold text-lg">{wishlist.name}</p>
                                        <p className="text-sm text-gray-600">
                                            {wishlist.description || "No description provided"}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-2">
                                            Created: {new Date(wishlist.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </>
    );
}