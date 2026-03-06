import Navbar from "../components/Navbar";

export default function WishlistsPage() {
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
              This page will allow users to save destinations they are interested
              in visiting, organise low-stress travel ideas, and build shortlists
              for future trips.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
              <h2 className="text-2xl font-semibold mb-3">Create a Wishlist</h2>
              <p className="text-gray-600 mb-5">
                Soon, users will be able to create personal travel wishlists and
                save recommended destinations.
              </p>

              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Wishlist name"
                  className="w-full border border-gray-200 rounded-xl px-4 py-3"
                  disabled
                />
                <textarea
                  placeholder="Description"
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 min-h-[120px]"
                  disabled
                />
                <button className="w-full rounded-full bg-[#007788] text-white py-3 font-medium opacity-70 cursor-not-allowed">
                  Create Wishlist
                </button>
              </div>
            </div>

            <div className="bg-white rounded-[1.5rem] p-6 shadow-md border border-gray-100">
              <h2 className="text-2xl font-semibold mb-3">Saved Ideas</h2>
              <p className="text-gray-600 mb-5">
                Wishlist functionality will later connect to the authenticated API
                endpoints.
              </p>

              <div className="space-y-4">
                <div className="rounded-xl bg-[#f9f9f9] p-4">
                  <p className="font-semibold">Affordable + Calm</p>
                  <p className="text-sm text-gray-600">
                    Shortlist for low-stress destinations
                  </p>
                </div>

                <div className="rounded-xl bg-[#f9f9f9] p-4">
                  <p className="font-semibold">Nature Escapes</p>
                  <p className="text-sm text-gray-600">
                    Saved ideas for peaceful scenic trips
                  </p>
                </div>

                <div className="rounded-xl bg-[#f9f9f9] p-4">
                  <p className="font-semibold">Summer Options</p>
                  <p className="text-sm text-gray-600">
                    Places to revisit for affordable summer travel
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}