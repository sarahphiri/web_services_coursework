import Navbar from "./components/Navbar";
import Image from "next/image";

export default function Home() {
  return (
    <>
      <Navbar />

      <main className="min-h-screen text-[#333333]">
        <section className="relative overflow-hidden">
          <div className="max-w-6xl mx-auto px-6 py-16 md:py-24">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-[#00A896] font-semibold mb-3">
                  Calm travel planning
                </p>

                <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6 text-[#007788]">
                  Discover affordable,
                  <span className="block text-[#333333]">
                    low-stress destinations
                  </span>
                </h1>

                <p className="text-lg text-gray-700 mb-8 max-w-xl leading-8">
                  Travel Without Barriers helps users discover destinations that
                  are affordable, less crowded, and highly rated — making travel
                  planning feel simpler, calmer, and more accessible.
                </p>

                <div className="flex flex-wrap gap-4 mb-10">
                  <a
                    href="/recommendations"
                    className="px-6 py-3 rounded-full bg-[#007788] text-white font-medium hover:bg-[#006674] transition shadow-md"
                  >
                    Explore Recommendations
                  </a>

                  <a
                    href="/wishlists"
                    className="px-6 py-3 rounded-full border border-[#007788] text-[#007788] font-medium hover:bg-[#eaf8f7] transition"
                  >
                    View Wishlists
                  </a>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
                    <p className="text-2xl mb-2">💸</p>
                    <h3 className="font-semibold mb-1">Affordable</h3>
                    <p className="text-sm text-gray-600">
                      Destinations that reduce financial barriers.
                    </p>
                  </div>

                  <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
                    <p className="text-2xl mb-2">🌿</p>
                    <h3 className="font-semibold mb-1">Calm</h3>
                    <p className="text-sm text-gray-600">
                      Lower crowd levels for a less stressful experience.
                    </p>
                  </div>

                  <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
                    <p className="text-2xl mb-2">⭐</p>
                    <h3 className="font-semibold mb-1">Highly Rated</h3>
                    <p className="text-sm text-gray-600">
                      Recommendations that still prioritise quality.
                    </p>
                  </div>
                </div>
              </div>

              <div className="relative">
                <div className="bg-white rounded-[2rem] p-6 shadow-xl border border-gray-100">
                  <div className="rounded-2xl bg-gradient-to-br from-cyan-50 to-teal-50 p-6 min-h-[360px] flex flex-col justify-between">
                    <div>
                      <p className="text-sm uppercase tracking-wide text-[#00A896] font-semibold mb-2">
                        Example search
                      </p>
                      <div className="bg-white rounded-full border-2 border-[#007788] px-5 py-4 shadow-sm text-lg text-gray-700">
                        Affordable, calm destinations in Europe
                      </div>
                    </div>

                    <div className="grid gap-4 mt-8">
                      <div className="bg-white rounded-2xl p-5 shadow-sm">
                        <h3 className="text-xl font-semibold mb-2">
                          A quiet Greek village
                        </h3>
                        <div className="grid grid-cols-3 gap-3 text-sm">
                          <div>
                            <p className="text-gray-500">Affordability</p>
                            <p className="font-semibold text-[#00A896]">High</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Crowd Level</p>
                            <p className="font-semibold text-[#007788]">Low</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Rating</p>
                            <p className="font-semibold text-[#FFD166]">4.7</p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white rounded-2xl p-5 shadow-sm">
                        <h3 className="text-xl font-semibold mb-2">
                          Secluded Scottish loch
                        </h3>
                        <div className="grid grid-cols-3 gap-3 text-sm">
                          <div>
                            <p className="text-gray-500">Affordability</p>
                            <p className="font-semibold text-[#00A896]">Medium</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Crowd Level</p>
                            <p className="font-semibold text-[#007788]">Very low</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Rating</p>
                            <p className="font-semibold text-[#FFD166]">4.8</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="absolute -top-6 -right-6 w-20 h-20 bg-[#FFD166]/30 rounded-full blur-2xl" />
                <div className="absolute -bottom-6 -left-6 w-24 h-24 bg-[#00A896]/20 rounded-full blur-2xl" />
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}